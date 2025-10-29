import sys
import numpy as np
import pandas as pd
from scipy.stats import entropy
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QGroupBox
)

from anonymization_functions import (
    anonymize_SNP, anonymize_passport, anonymize_snils, anonymize_symptoms,
    anonymize_doctors, anonymize_dates_visit, anonymize_tests, local_suppression,
    anonymize_dates_takeaway, anonymize_price, anonymize_bankcard,
    doctors_local_aggregation, test_local_aggregation, symptom_local_aggregation,
    calculate_k_anonymity, get_bad_k
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Анонимизация данных")
        self.setGeometry(100, 100, 1200, 700)

        main_layout = QVBoxLayout()

        # Блок выбора квази-идентификаторов
        checkbox_group = QGroupBox("Выберите квази-идентификаторы")
        checkbox_layout = QHBoxLayout()
        self.checkboxes = {}

        for q in QUASI_IDENTIFIERS:
            cb = QCheckBox(q)
            checkbox_layout.addWidget(cb)
            self.checkboxes[q] = cb

        self.all_selected = QCheckBox("Выбрать всё")
        checkbox_layout.addWidget(self.all_selected)

        checkbox_group.setLayout(checkbox_layout)
        main_layout.addWidget(checkbox_group)

        # Таблица плохих K-анонимностей 
        main_layout.addWidget(QLabel("Топ плохих K-анонимностей:"))
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["K", "Доля (%)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setFixedHeight(150)
        main_layout.addWidget(self.table)

        self.recommended_k_anonymity = QLabel("Рекомендуемое значение К-анонимити для набора данных: ")
        main_layout.addWidget(self.recommended_k_anonymity)

        # Уникальные строки (K=1) 
        self.unique_label = QLabel("Количество уникальных комбинаций: -")
        main_layout.addWidget(self.unique_label)

        self.k1_table = QTableWidget()
        self.k1_table.setColumnCount(0)
        self.k1_table.setFixedHeight(200)
        main_layout.addWidget(self.k1_table)

        # Метка и таблица для оценки полезности
        self.kl_label = QLabel("KL-дивергенция (полезность данных):")
        main_layout.addWidget(self.kl_label)

        self.kl_table = QTableWidget()
        self.kl_table.setColumnCount(2)
        self.kl_table.setHorizontalHeaderLabels(["Столбец", "KL-дивергенция"])
        self.kl_table.horizontalHeader().setStretchLastSection(True)
        self.kl_table.setFixedHeight(200)
        main_layout.addWidget(self.kl_table)

        # Кнопки управления 
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

        unique_btn = QPushButton("Уникальные строки (K=1)")
        unique_btn.clicked.connect(self.show_unique_rows)
        button_layout.addWidget(unique_btn)

        utility_btn = QPushButton("Оценить полезность данных")
        utility_btn.clicked.connect(self.evaluate_utility)
        button_layout.addWidget(utility_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_file)
        button_layout.addWidget(save_btn)

        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def recommend_k(self):
        global original_df
        length = len(original_df)
        
        if length < 51000:
            r = 10
        elif length < 105000:
            r = 7
        else: r = 5
        self.recommended_k_anonymity.setText(f"Рекомендуемое значение К-анонимити для набора данных: {r} и больше")

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
                self.recommend_k()
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
        
        anonymized_df, l, removed = local_suppression(anonymized_df, selected, 0.05)
        QMessageBox.information(self, "Готово",
         f"Анонимизация выполнена. С помощью Локального Подавления удалено {removed} строк ({removed / l * 100:.2f}%)")

    def calculate_k(self):
        global anonymized_df
        selected = self.set_selected()
        if not selected:
            QMessageBox.information(self, "Информация", "Не выбраны квази-идентификаторы.")
            return

        grouped, _, _ = calculate_k_anonymity(anonymized_df, selected)
        bad = get_bad_k(grouped, len(anonymized_df))

        self.table.setRowCount(0)
        for k, pct in bad:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(k)))
            self.table.setItem(row, 1, QTableWidgetItem(pct))

    def show_unique_rows(self):
        global anonymized_df
        selected = self.set_selected()

        if anonymized_df is None:
            QMessageBox.warning(self, "Ошибка", "Сначала обезличьте данные.")
            return
        if not selected:
            QMessageBox.information(self, "Информация", "Не выбраны квази-идентификаторы.")
            return

        _, num_unique, k1_df = calculate_k_anonymity(anonymized_df, selected)

        self.unique_label.setText(f"Количество уникальных комбинаций: {num_unique}")

        self.k1_table.setRowCount(0)

        if not k1_df.empty:
            cols = [c for c in selected if c in k1_df.columns]
            self.k1_table.setColumnCount(len(cols))
            self.k1_table.setHorizontalHeaderLabels(cols)

            for _, row in k1_df.iterrows():
                row_idx = self.k1_table.rowCount()
                self.k1_table.insertRow(row_idx)
                for col_idx, col in enumerate(cols):
                    self.k1_table.setItem(row_idx, col_idx, QTableWidgetItem(str(row[col])))
        else:
            QMessageBox.information(self, "Информация", "Нет строк с K = 1.")

    def evaluate_utility(self):
        global original_df, anonymized_df
        if original_df is None or anonymized_df is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите и обезличьте данные.")
            return

        results = []

        for col in original_df.columns:
            orig = original_df[col].dropna()
            anon = anonymized_df[col].dropna()

            if pd.api.types.is_numeric_dtype(orig):
                orig_vals = pd.to_numeric(orig, errors='coerce').dropna()
                anon_vals = pd.to_numeric(anon, errors='coerce').dropna()

                if len(orig_vals) == 0 or len(anon_vals) == 0:
                    kl_div = np.nan
                else:
                    min_val = min(orig_vals.min(), anon_vals.min())
                    max_val = max(orig_vals.max(), anon_vals.max())
                    hist_orig, edges = np.histogram(orig_vals, bins=10, range=(min_val, max_val), density=True)
                    hist_anon, _ = np.histogram(anon_vals, bins=edges, density=True)
                    hist_orig += 1e-10
                    hist_anon += 1e-10
                    kl_div = entropy(hist_orig, hist_anon)

            else:
                orig_counts = orig.value_counts(normalize=True)
                anon_counts = anon.value_counts(normalize=True)
                all_categories = set(orig_counts.index) | set(anon_counts.index)
                p = np.array([orig_counts.get(c, 1e-10) for c in all_categories])
                q = np.array([anon_counts.get(c, 1e-10) for c in all_categories])
                kl_div = entropy(p, q)

            results.append((col, kl_div))

        self.kl_table.setRowCount(0)
        for col, kl in sorted(results, key=lambda x: (np.nan_to_num(x[1], nan=0)), reverse=True):
            row_idx = self.kl_table.rowCount()
            self.kl_table.insertRow(row_idx)
            self.kl_table.setItem(row_idx, 0, QTableWidgetItem(str(col)))
            self.kl_table.setItem(row_idx, 1, QTableWidgetItem(f"{kl:.4f}" if not pd.isna(kl) else "N/A"))

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
