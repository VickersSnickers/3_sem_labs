import sys
import pandas as pd
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QGroupBox
)

from anonymization_functions import (
    anonymize_SNP, anonymize_passport, anonymize_snils, anonymize_symptoms,
    anonymize_doctors, anonymize_dates_visit, anonymize_tests,
    anonymize_dates_takeaway, anonymize_price, anonymize_bankcard,
    doctors_local_aggregation, test_local_aggregation, symptom_local_aggregation
)

original_df = None
anonymized_df = None

QUASI_IDENTIFIERS = [
    "ФИО",
    "Паспортные данные",
    "СНИЛС",
    "Симптомы",
    "Выбор врача",
    "Дата посещения врача",
    "Анализы",
    "Дата получения анализов",
    "Стоимость анализов",
    "Карта оплаты"
]


def calculate_k_anonymity(df: pd.DataFrame, quasi_identifiers):
    grouped = df.groupby(quasi_identifiers).size()
    return grouped
    # (Кашель, Иванов, 2023-05): 3

def get_bad_k(grouped: pd.Series, length: int, top_n: int = 5):
    counts = grouped.value_counts().sort_index()
    bad = counts.head(top_n)
    result = [(int(k), f"{(v/length*100):.2f}%") for k, v in bad.items()]
    return result

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Анонимизация данных")
        self.setGeometry(100, 100, 900, 600)

        main_layout = QVBoxLayout()

        self.checkbox_group = QGroupBox("Выберите квази-идентификаторы")
        checkbox_layout = QVBoxLayout()
        self.checkboxes = {}

        for q in QUASI_IDENTIFIERS:
            cb = QCheckBox(q)
            checkbox_layout.addWidget(cb)
            self.checkboxes[q] = cb

        self.all_selected = QCheckBox("Выбрать всё")
        checkbox_layout.addWidget(self.all_selected)

        self.checkbox_group.setLayout(checkbox_layout)
        main_layout.addWidget(self.checkbox_group)


        button_layout = QHBoxLayout()

        load_btn = QPushButton("Загрузить файл")
        load_btn.clicked.connect(self.load_file)
        button_layout.addWidget(load_btn)

        anonymize_btn = QPushButton("Обезличить")
        anonymize_btn.clicked.connect(self.run_anonymization)
        button_layout.addWidget(anonymize_btn)

        kanon_btn = QPushButton("Рассчитать k-анонимность")
        kanon_btn.clicked.connect(self.calculate_k)
        button_layout.addWidget(kanon_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_file)
        button_layout.addWidget(save_btn)

        main_layout.addLayout(button_layout)


        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["K", "Доля (%)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(QLabel("Топ плохих K-анонимностей:"))
        main_layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def set_selected(self):
        if self.all_selected.isChecked():
            selected = [q for q, cb in self.checkboxes.items()]
        else: selected = [q for q, cb in self.checkboxes.items() if cb.isChecked()]
        return selected

    def load_file(self):
        global original_df, anonymized_df
        path, _ = QFileDialog.getOpenFileName(self, "Открыть CSV", "", "CSV файлы (*.csv)")
        if path:
            try:
                original_df = pd.read_csv(
                    path,
                    sep=';',
                    encoding='utf-8-sig',
                    parse_dates=["Дата посещения врача", "Дата получения анализов"]
                )
                anonymized_df = original_df.copy()
                QMessageBox.information(self, "Успех", f"Файл успешно загружен: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {e}")

    def run_anonymization(self):

        global anonymized_df, original_df
        if original_df is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите файл.")
            return
        selected = self.set_selected()

        if not selected:
            QMessageBox.information(self, "Информация", "Не выбраны квази-идентификаторы.")
            return

        for col in selected:
            if col == "ФИО":
                anonymize_SNP(anonymized_df)
            elif col == "Паспортные данные":
                anonymize_passport(anonymized_df)
            elif col == "СНИЛС":
                anonymize_snils(anonymized_df)
            elif col == "Симптомы":
                anonymize_symptoms(anonymized_df)
            elif col == "Выбор врача":
                anonymize_doctors(anonymized_df)
            elif col == "Дата посещения врача":
                anonymize_dates_visit(anonymized_df)
            elif col == "Анализы":
                anonymize_tests(anonymized_df)
            elif col == "Дата получения анализов":
                anonymize_dates_takeaway(anonymized_df)
            elif col == "Стоимость анализов":
                anonymize_price(anonymized_df)
            elif col == "Карта оплаты":
                anonymize_bankcard(anonymized_df)
        QMessageBox.information(self, "Готово", f"Анонимизация выполнена.")

    def calculate_k(self):
        global anonymized_df

        selected = self.set_selected()
        if not selected:
            QMessageBox.information(self, "Информация", "Не выбраны квази-идентификаторы.")
            return

        grouped = calculate_k_anonymity(anonymized_df, selected)
        bad = get_bad_k(grouped, len(anonymized_df))

        self.table.setRowCount(0)
        for k, pct in bad:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(k)))
            self.table.setItem(row, 1, QTableWidgetItem(pct))


    def save_file(self):
        global anonymized_df

        if anonymized_df is None:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "CSV файлы (*.csv)")
        if path:
            anonymized_df.to_csv(path, sep=';', encoding='utf-8-sig', index=False)
            QMessageBox.information(self, "Готово", f"Файл сохранён: {path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
