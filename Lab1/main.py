from functions import *
import argparse

def make_medcard(bank_card_data, male_list, female_list):

    total = []
    
    """Случайное количество случайных записей из medicine.csv в виде списка seed"""
    rnum = randint(3, 10)
    seed = [medicine[randrange(med_num)] for i in range(rnum)] 

    name = generate_fullname(randrange(2), male_list, female_list)
    passport = generate_passport()
    snils = generate_snils()
    card = generate_card_number(bank_card_data)

    counter, flag = 0, True
    for elem in seed:

        """Генерируем новую карту если использована больше 5 раз"""
        counter += 1
        if counter > 5 and flag:
            card = generate_card_number(bank_card_data)
            flag = False

        data = dict()
        analysis = []
        """ Случайное количество анализов (от 3 до 5), соответствующее симптому"""
        temp = elem[1].split('|')
        al = [temp[randrange(len(temp))] for i in range(3, 5)]
        for _ in al:
            analysis.append(_)

        temp = elem[2].split(', ')

        al_cost = 0
        for i in analysis:
            """Для каждого анализа ищем стоймость в costs.csv и суммируем в an_cost"""
            for line in costs:
                if line[0] == i:
                    al_cost += int(line[1])
                    break

        date = generate_datetime()

        data["ФИО"] = name
        data["Паспортные данные"] = passport
        data["СНИЛС"] = snils
        data["Симптомы"] = elem[0]
        """Случайный доктор, соответствующий симптому"""
        data["Выбор врача"] = temp[randrange(len(temp))]
        data["Дата посещения врача"] = date
        data["Анализы"] = ' | '.join(analysis)
        data["Дата получения анализов"] = get_back_analysis(date)
        data["Стоимость анализов"] = al_cost
        data["Карта оплаты"] = card

        total.append(data)
    return total

def get_csv(source):
    lst = []
    with open(source, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            temp = [row[elem] for elem in reader.fieldnames]
            lst.append(temp)
    return lst

def output(source, data):
    with open(source, "w", newline="", encoding="utf-8-sig") as f:
        head = ["ФИО", "Паспортные данные", "СНИЛС", "Симптомы", "Выбор врача",
                "Дата посещения врача", "Анализы", "Дата получения анализов",
                "Стоимость анализов", "Карта оплаты"]
        writer = csv.DictWriter(f, fieldnames=head, delimiter=';')
        writer.writeheader()
        writer.writerows(data)

def generate_output_csv(source, bank_card_data, male_list, female_list, limit):
    out = []
    counter = limit
    while counter > 0:
        newline = make_medcard(bank_card_data=bank_card_data, male_list=male_list,
                             female_list=female_list)
        out += newline
        counter -= len(newline)
    out = out[:limit]
    output(source=source, data=out)


def set_input():
    parser = argparse.ArgumentParser(description="Генерация медицинских карт")
    parser.add_argument("-n", "--num", type=int, default=50000,
                        help="Количество строк в выходном файле (по умолчанию 50000)")
    parser.add_argument("-w", "--weights", nargs=5, type=float,
                        default=[0.3, 0.2, 0.2, 0.2, 0.1],
                        help="Веса банков в формате: w1 w2 w3 w4 w5 (сумма = 1)")
    
    args = parser.parse_args()
    weights = args.weights

    card_data = [
        ["Сбербанк", [
            ["Мир", ["220100", "220220"]],
            ["Visa", ["427402", "427406", "427411"]],
            ["Mastercard", ["559901", "559521", "557000"]],
            ["UnionPay", ["623371", "623372"]]
        ], weights[0]],

        ["Тинькофф", [
            ["Мир", ["220070"]],
            ["Visa", ["415428", "415429"]],
            ["Mastercard", ["553691", "553420", "551960"]],
            ["UnionPay", ["623373"]]
        ], weights[1]],

        ["ВТБ", [
            ["Мир", ["220024"]],
            ["Visa", ["489195", "489196"]],
            ["Mastercard", ["518704", "518373"]],
            ["UnionPay", ["623374"]]
        ], weights[2]],

        ["АльфаБанк", [
            ["Мир", ["220015"]],
            ["Visa", ["410584", "415400"]],
            ["Mastercard", ["555949"]],
            ["UnionPay", ["623375"]]
        ], weights[3]],

        ["ГазпромБанк", [
            ["Мир", ["220001"]],
            ["Visa", ["404136", "404270"]],
            ["Mastercard", ["539839", "544026"]],
            ["UnionPay", ["623376"]]
        ], weights[4]]
    ]

    return args.num, card_data

if  __name__ == "__main__":

    num, card_data = set_input()
    MALE, FEMALE = load_names('data/names.csv')
    medicine = get_csv('data/medicine.csv')
    med_num = len(medicine)
    costs = get_csv('data/costs.csv')
    cost_num = len(costs)

    generate_output_csv('output.csv', card_data, MALE, FEMALE, num)