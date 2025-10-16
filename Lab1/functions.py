from random import *
import csv
from datetime import datetime, timedelta

def load_names(source):
    Male, Female = [[], [], []], [[], [], []]
    with open(source, encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        for row in reader:
            if row[3] == 'М':
                Male[0].append(row[0])
                Male[1].append(row[1])
                Male[2].append(row[2])
            else:
                Female[0].append(row[0])
                Female[1].append(row[1])
                Female[2].append(row[2])
    return Male, Female


def generate_fullname(gender, Male, Female):
    if gender == 0:
        surname, name, patronym = choice(Male[0]), choice(Male[1]), choice(Male[2])
    else: surname, name, patronym = choice(Female[0]), choice(Female[1]), choice(Female[2])
    return f'{surname} {name} {patronym}'



def generate_snils():
    n = [randrange(10) for i in range(9)]
    c = sum([n[-i]*i for i in range(9, 0, -1)])
    while c > 101:
        c -= 101
    if (c == 100 or c == 101): c = 00
    res = ''.join([str(i) for i in n])
    return res[0:3] + '-' + res[3:6] + '-' + res[6:9] + ' ' + str(c).zfill(2)


def generate_passport():
    series_1 = ['01','03','04','05','07','08','10','11','14','15','17','18','19','20',
        '22','24','25','26','27','28','29','30','32','33','34','36','37','38',
        '40','41','42','44','45','46','47','49','50','52','53','54','56','57',
        '58','60','61','63','64','65','66','68','69','70','71','73','75','76',
        '77','79','80','81','82','83','84','85','86','87','88','89','90','91',
        '92','93','94','95','96','97','98','99',]
    series_2 = ['27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38',
            '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50',
            '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', 
            '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', 
            '75', '76', '77', '78', '79', '80', '81', '82', '83', '84', '85', '86', 
            '87', '88', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98', 
            '99', '00', '01', '02', '03', '04', '05', '06', '07']
    return series_1[randrange(len(series_1))] + series_2[randrange(len(series_2))] + ''.join([str(randrange(10)) for i in range(6)])


def generate_datetime(time_begin="08:00", time_end="21:00"):
    time_begin_elem = datetime.strptime(time_begin, "%H:%M").time()     # time(8, 0)
    time_end_elem = datetime.strptime(time_end, "%H:%M").time()         # time(21, 0)

    start, end = datetime(2025, 1, 1), datetime(2025, 12, 31)
    time_gap = end - start

    while True:
        rday = randint(0, time_gap.days)
        rdate = start + timedelta(days=rday)
        if rdate.weekday() < 5:                                         # 0-4 -> Пн-Пт
            break
    
    min_seconds = time_begin_elem.minute * 60 + time_begin_elem.hour * 3600
    max_seconds = time_end_elem.minute * 60 + time_end_elem.hour * 3600
    rseconds = randint(min_seconds, max_seconds)
    rtime = (datetime.min + timedelta(seconds=rseconds)).time()
    
    rdatetime = datetime.combine(rdate, rtime)
    return rdatetime.strftime("%Y-%m-%dT%H:%M")


def get_back_analysis(date_time, time_begin="08:00", time_end="21:00"):
    time_begin_elem = datetime.strptime(time_begin, "%H:%M").hour
    time_end_elem = datetime.strptime(time_end, "%H:%M").hour
    dt = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
    while True:
        hours_to_add = uniform(24, 72)
        new_dt = dt + timedelta(hours=hours_to_add)
        if new_dt.weekday() < 5:
            if new_dt.hour < time_begin_elem:
                new_dt = new_dt.replace(hour=time_begin_elem, minute=0, second=0, microsecond=0)
            elif new_dt.hour >= time_end_elem:
                new_dt = new_dt.replace(hour=time_end_elem-1, minute=59, second=0, microsecond=0)
            return new_dt.strftime("%Y-%m-%dT%H:%M")
        

def calculate_luhn_checksum(partial_card_number):
    digits = [int(d) for d in partial_card_number]
    for i in range(len(digits)-1, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    total = sum(digits)
    checksum = (10 - (total % 10)) % 10
    return str(checksum)

def generate_card_number(banks):
    chosen_bank = choices(range(len(banks)), weights=[bank[2] for bank in banks], k=1)[0]
    system_name, bin_list = choice(banks[chosen_bank][1])
    bin_code = choice(bin_list)
    partial_num = bin_code + ''.join(str(randrange(9)) for i in range(9))
    return partial_num + calculate_luhn_checksum(partial_num)
