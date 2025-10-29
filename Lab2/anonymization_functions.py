import pandas as pd
import numpy as np
from datetime import datetime
from random import shuffle
from collections import Counter

symptom_local_aggregation = {
    "Физиологические симптомы": [
        "Боль в горле", "Кашель", "Заложенность носа", "Насморк",
        "Ощущение кома в горле", "Хриплый голос", "Трудно дышать",
        "Частые простуды", "Боль в животе", "Изжога", "Тяжесть в желудке",
        "Рвота", "Тошнота", "Запор", "Потеря аппетита",
        "Металлический привкус во рту", "Жжение при мочеиспускании",
        "Кровь в моче", "Частое мочеиспускание", "Увеличенные лимфоузлы"
    ],

    "Кожные и опорно-двигательные симптомы": [
        "Высыпания на коже", "Покраснение кожи", "Зуд", "Сухость кожи",
        "Выпадение волос", "Синяки без причины",
        "Боль в мышцах", "Боль в суставах", "Боль в пояснице",
        "Ломота в теле", "Слабость в ногах"
    ],

    "Неврологические и общие симптомы": [
        "Головная боль", "Двоение в глазах", "Тремор рук", "Постоянная усталость",
        "Боль в груди", "Учащённое сердцебиение", "Головокружение при вставании",
        "Кружится голова", "Повышенная температура", "Потливость",
        "Потеря веса", "Увеличение веса", "Ухудшение зрения", "Шум в ушах", "Боль в ухе"
    ]
}

test_local_aggregation = {
    "Гормональные и метаболические исследования": [
        "Тестостерон общий", "Тестостерон свободный", "Дигидротестостерон",
        "Эстрадиол (Е2)", "Прогестерон", "Кортизол", "Кортизол суточной мочи",
        "АКТГ (адренокортикотропный гормон)", "ТТГ (тиреотропный гормон)",
        "Трийодтиронин свободный (Т3 свободный)", "Тироксин свободный (Т4 свободный)",
        "Паратгормон", "Альдостерон", "Ренин", "Альдостерон-рениновое соотношение",
        "Инсулин", "Антитела к инсулину (IAA)", "Пролактин", "ФСГ (фолликулостимулирующий гормон)",
        "Лютеинизирующий гормон (ЛГ)", "Лептин", "Гастрин",
        "Глюкоза", "Креатинин", "Мочевина", "Общий белок", "Альбумин",
        "Билирубин общий", "Билирубин прямой", "Щелочная фосфатаза", "КФК (креатинкиназа)",
        "АЛТ (аланинаминотрансфераза)", "АСТ (аспартатаминотрансфераза)",
        "Лактатдегидрогеназа (ЛДГ)", "Ферритин", "Гомоцистеин"
    ],

    "Иммунологические и инфекционные исследования": [
        "Антитела к вирусу гепатита С, сум. (Anti-HCV)", "ВИЧ (антитела и антигены)",
        "Диагностика гепатитов, скрининг", "Поверхностный антиген вируса гепатита В (HbsAg)",
        "Антитела к вирусу Эпштейна-Барр (Epstein-Barr virus), IgG",
        "Антитела к цитомегаловирусу (Cytomegalovirus), IgG",
        "Антитела к вирусу простого герпеса I, II типов (Herpes simplex virus I, II)",
        "Вирусы группы герпеса (EBV, CMV, HHV6)", "Антитела к хеликобактеру (Helicobacter pylori), IgG",
        "13С – уреазный дыхательный тест (H. pylori)", "Антитела к микоплазме (Mycoplasma pneumoniae), IgM",
        "Антитела к хламидии (Chlamydia trachomatis), IgG", "Антитела к токсоплазме (Toxoplasma gondii), IgG",
        "Антитела к эхинококкам (Echinococcus granulosus), IgG", "Антитела к аскаридам (Ascaris lumbricoides), IgG",
        "Антитела к боррелиям (Borrelia burgdorferi), IgG", "Антитела к лямблиям (Lamblia intestinalis), IgM",
        "Антитела к бруцелле (Brucella), IgA", "Антитела к фосфолипидам", "Антитела к кардиолипину",
        "Антитела к двуспиральной ДНК", "Антинуклеарные антитела",
        "Иммуноглобулин G (IgG)", "Иммуноглобулин M (IgM)", "Иммуноглобулин A (IgA)", "Иммуноглобулин Е (IgE)"
    ],

    "Общие, витаминно-минеральные и микробиологические анализы": [
        "Витамин Д (25-OH витамин D)", "Витамин B12 (цианкобаламин)", "Витамин B6 (пиридоксаль-5-фосфат)",
        "Витамин B1 (тиамин-пирофосфат)", "Витамин В9 (фолиевая кислота)", "Витамин А (ретинол)",
        "Витамин Е (альфа-токоферол)", "Витамин К (филлохинон)", "Витамин С (аскорбиновая кислота)",
        "Кальций общий", "Кальций ионизированный", "Магний", "Железо", "Цинк", "Медь", "Селен", "Фосфор неорганический",
        "Общий анализ крови", "Клинический анализ крови (5DIFF)",
        "Клинический анализ крови без лейкоцитарной формулы", "Общий анализ мочи",
        "Анализ мочи по Нечипоренко", "Анализ мочи по Зимницкому", "3-х стаканная проба мочи",
        "Исследование кала на скрытую кровь", "Общий анализ кала (копрограмма)",
        "Посев мочи на флору", "Посев крови на стерильность",
        "Исследование антигена хеликобактера (Helicobacter pylori) в кале",
        "Исследование кала на простейшие и яйца гельминтов",
        "Микроскопическое исследование мазков", "Микроскопическое исследование соскобов кожи",
        "Микроскопическое исследование отделяемого уретры", "Дисбактериоз с определением чувствительности к бактериофагам",
        "Типирование грибов (Candida spp.)", "Посев на возбудителей кишечной инфекции"
    ]
}

doctors_local_aggregation = {
    "Терапевтические, инфекционные и иммунные блоки": [
        "Терапевт",
        "Семейный врач",
        "Кардиолог",
        "Пульмонолог",
        "Гастроэнтеролог",
        "Ревматолог",
        "Эндокринолог",
        "Гематолог",
        "Инфекционист",

    ],

    "Неврологические, психофизиологические и иммунные блоки": [
        "Невролог",
        "Физиотерапевт",
        "Вертебролог",
        "Аллерголог",
        "Иммунолог"
    ],

    "Специалисты органов чувств и Хирургический блок": [
        "ЛОР",
        "Сурдолог",
        "Офтальмолог",
        "Фониатр",
        "Стоматолог",
        "Дерматолог",
        "Хирург",
        "Ортопед",
        "Уролог"
    ]
}


names = {'Смирнов':'М','Иванов':'М','Кузнецов':'М','Попов':'М','Соколов':'М',
         'Лебедев':'М','Козлов':'М','Новиков':'М','Морозов':'М','Петров':'М',
         'Волков':'М','Соловьев':'М','Виноградов':'М','Богданов':'М','Васильев':'М',
         'Зайцев':'М','Павлов':'М','Семенов':'М','Григорьев':'М','Кузьмин':'М',
         'Куликов':'М','Киселев':'М','Макаров':'М','Александров':'М','Михайлов':'М',
         'Федоров':'М','Сергеев':'М','Орлов':'М','Никитин':'М','Тихонов':'М','Беликов':'М',
         'Карпов':'М','Данилов':'М','Борисов':'М','Тарасов':'М','Воронов':'М','Егоров':'М',
         'Котов':'М','Дмитриев':'М','Лазарев':'М','Сафонов':'М','Гусев':'М','Коновалов':'М',
         'Мельников':'М','Крылов':'М','Власов':'М','Ширяев':'М','Панфилов':'М','Дорофеев':'М',
         'Игнатьев':'М','Конов':'М','Фролов':'М','Смирнова':'Ж','Иванова':'Ж','Кузнецова':'Ж',
         'Попова':'Ж','Соколова':'Ж','Лебедева':'Ж','Козлова':'Ж','Новикова':'Ж','Морозова':'Ж',
         'Петрова':'Ж','Волкова':'Ж','Соловьева':'Ж','Виноградова':'Ж','Богданова':'Ж','Васильева':'Ж',
         'Зайцева':'Ж','Павлова':'Ж','Семенова':'Ж','Григорьева':'Ж','Кузьмина':'Ж','Куликова':'Ж',
         'Киселева':'Ж','Макарова':'Ж','Александрова':'Ж','Михайлова':'Ж','Федорова':'Ж','Сергеева':'Ж',
         'Орлова':'Ж','Никитина':'Ж','Тихонова':'Ж','Беликова':'Ж','Карпова':'Ж','Данилова':'Ж',
         'Борисова':'Ж','Тарасова':'Ж','Воронова':'Ж','Егорова':'Ж','Котова':'Ж','Дмитриева':'Ж',
         'Лазарева':'Ж','Сафонова':'Ж','Гусева':'Ж','Коновалова':'Ж','Мельникова':'Ж','Крылова':'Ж',
         'Власова':'Ж','Ширяева':'Ж','Панфилова':'Ж','Дорофеева':'Ж','Игнатьева':'Ж','Конова':'Ж'}

card_data = [
    ["Сбербанк", [
        ["Мир", ["220100", "220220"]],
        ["Visa", ["427402", "427406", "427411"]],
        ["Mastercard", ["559901", "559521", "557000"]],
        ["UnionPay", ["623371", "623372"]]]],
    ["Тинькофф", [
        ["Мир", ["220070"]],
        ["Visa", ["415428", "415429"]],
        ["Mastercard", ["553691", "553420", "551960"]],
        ["UnionPay", ["623373"]]]],
    ["ВТБ", [
        ["Мир", ["220024"]],
        ["Visa", ["489195", "489196"]],
        ["Mastercard", ["518704", "518373"]],
        ["UnionPay", ["623374"]]]],
    ["АльфаБанк", [
        ["Мир", ["220015"]],
        ["Visa", ["410584", "415400"]],
        ["Mastercard", ["555949"]],
        ["UnionPay", ["623375"]]]],
    ["ГазпромБанк", [
        ["Мир", ["220001"]],
        ["Visa", ["404136", "404270"]],
        ["Mastercard", ["539839", "544026"]],
        ["UnionPay", ["623376"]]]]
]

def get_season(date: datetime) -> str:
    month = date.month
    if month in (1, 2, 3, 4, 5, 6):
        return "1 Полугодие"
    else:
        return "2 Полугодие"
    
def get_bank(card_number: int) -> str:
    bin_code = str(card_number)[:6]
    for bank_name, systems in card_data:
        for system_name, bins in systems:
            if bin_code in bins:
                return system_name
    return "Неизвестнная система"

def change_to_gender(SNP: str) -> str:
    for s, g in names.items():
        if s == SNP.split(' ')[0]:
            if g == 'М': return 'Мужчина'
            else: return 'Женщина'

def categorize_tests(value: str) -> str:
    value_l = str(value).lower()
    for category, tests in test_local_aggregation.items():
        for test in tests:
            if test.lower() in value_l:
                return category
    return 'Прочие исследования'

def anonymize_SNP(df: pd.DataFrame) -> None:
    df['ФИО'] = df['ФИО'].apply(change_to_gender)

def anonymize_passport(df: pd.DataFrame) -> None:
    df['Паспортные данные'] = df['Паспортные данные'].apply(lambda x: 'Удалено')

def anonymize_snils(df: pd.DataFrame) -> None:
    df['СНИЛС'] = df['СНИЛС'].apply(lambda x: 'Удалено')

def anonymize_bankcard(df: pd.DataFrame) -> None:
    df['Карта оплаты'] = df['Карта оплаты'].apply(get_bank)

def anonymize_price(df: pd.DataFrame) -> None:
    prices = pd.to_numeric(df['Стоимость анализов'], errors='coerce')
    min_price = prices.min()
    mean_price = prices.mean()
    max_price = prices.max()

    labels = [f"{int(min_price)} — {int(mean_price)}", f"{int(mean_price)} — {int(max_price)}"]
    df['Стоимость анализов'] = pd.cut(prices, bins=[min_price, mean_price, max_price], labels=labels, include_lowest=True)




def anonymize_dates_visit(df: pd.DataFrame) -> None:
    dates = pd.to_datetime(df['Дата посещения врача'], errors='coerce')
    df['Дата посещения врача'] = dates.apply(
        lambda d: get_season(d) if not pd.isna(d) else 'Не указано'
    )

def anonymize_dates_takeaway(df: pd.DataFrame) -> None:
    dates_takeaway = pd.to_datetime(df['Дата получения анализов'], errors='coerce')
    df['Дата получения анализов'] = dates_takeaway.apply(
        lambda d: get_season(d) if not pd.isna(d) else 'Не указано'
    )

def anonymize_symptoms(df: pd.DataFrame) -> None:
    for category, symptoms in symptom_local_aggregation.items():
        df['Симптомы'] = df['Симптомы'].replace(symptoms, category)

def anonymize_tests(df: pd.DataFrame) -> None:
    df['Анализы'] = df['Анализы'].apply(categorize_tests)

def anonymize_doctors(df: pd.DataFrame) -> None:
    for category, doctors in doctors_local_aggregation.items():
        df['Выбор врача'] = df['Выбор врача'].replace(doctors, category)

def calculate_k_anonymity(df, quasi_identifiers):
    counts = {}
    for idx, row in df.iterrows():
        key = tuple(str(row[q]) for q in quasi_identifiers)
        counts[key] = counts.get(key, 0) + 1
    k_list = []
    for idx, row in df.iterrows():
        key = tuple(str(row[q]) for q in quasi_identifiers)
        k_list.append(counts[key])
    num_unique = len(counts)
    unique_keys = [key for key, value in counts.items() if value == 1]
    k1_df = df[df.apply(lambda row: tuple(str(row[q]) for q in quasi_identifiers) in unique_keys, axis=1)]
    return k_list, num_unique, k1_df

def local_suppression(df, quasi_identifiers, max_fraction=0.05):
    k_list, _, _ = calculate_k_anonymity(df, quasi_identifiers)
    df = df.copy()
    df["k_value"] = k_list

    max_remove = int(len(df) * max_fraction)
    if max_remove == 0:
        return df.drop(columns=["k_value"])

    df_sorted = df.sort_values(by="k_value", ascending=True)
    df_suppressed = df_sorted.iloc[max_remove:]
    df_suppressed = df_suppressed.drop(columns=["k_value"]).reset_index(drop=True)
    length = len(df)
    return df_suppressed, length, max_remove
    


def get_bad_k(k_list: list, total_length: int, top_n: int = 5):
    counts = Counter(k_list)
    sorted_items = sorted(counts.items(), key=lambda x: x[0])

    result = []
    for k_value, freq in sorted_items[:top_n]:
        perc = (freq / total_length) * 100
        result.append((k_value, f"{perc:.2f}%"))
    return result

import pandas as pd

def unique_rows_info(df: pd.DataFrame, quasi_identifiers: list):
    cols = [c for c in quasi_identifiers if c in df.columns]
    if not cols:
        raise ValueError("Не выбрано ни одного квази-идентификатора, присутствующего в таблице.")
    group_counts = df.groupby(cols).size().reset_index(name='count')
    df_with_counts = df.merge(group_counts, on=cols, how='left')
    k1_df = df_with_counts[df_with_counts['count'] == 1].drop(columns=['count'])
    num_unique = len(group_counts)
    return num_unique, k1_df
