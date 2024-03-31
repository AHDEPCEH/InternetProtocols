import subprocess
import re
import json
from urllib import request
from prettytable import PrettyTable


def get_args(count, info):
    try:
        as_number = info['org'].split()[0][2::]
        provider = " ".join(info['org'].split()[1::])
    except KeyError:
        as_number, provider = '*', '*'
    return [f"{count}.", info['ip'], info['country'], as_number, provider]


def get_bogon_args(count, info):
    return [f"{count}.", info['ip'], '*', '*', '*']


def is_complete(text_data):
    return 'Trace complete' in text_data or 'Трассировка завершена' in text_data


def is_timed_out(text_data):
    return 'Request timed out' in text_data or 'Превышен интервал ожидания' in text_data


def is_beginning(text_data):
    return 'Tracing route' in text_data or 'Трассировка маршрута' in text_data


def is_invalid_input(text_data):
    return 'Unable to resolve' in text_data or 'Не удается разрешить' in text_data


def get_ip_info(ip):
    return json.loads(request.urlopen('https://ipinfo.io/' + ip + '/json').read())


def trace_as(address, table):
    tracert_proc = subprocess.Popen(["tracert", address], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    number = 0

    for raw_line in iter(tracert_proc.stdout.readline, ''):
        line = raw_line.decode('cp866')
        ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)

        if is_complete(line):
            print()
            print(table)
            return
        if is_invalid_input(line):
            print('invalid input')
            return
        if is_beginning(line):
            print(line, end='')
            continue
        if is_timed_out(line):
            print('-', end='')
            continue
        if ip:
            number += 1
            #print(f'{"".join(ip)}')
            print("*", end='')
            info = get_ip_info(ip[0])
            if 'bogon' in info:
                table.add_row(get_bogon_args(number, info))
            else:
                table.add_row(get_args(number, info))


def main():
    address = input('Enter address: ')
    table = PrettyTable()
    table.field_names = ["number", "ip", "country", "AS number", "provider"]
    trace_as(address, table)


if __name__ == '__main__':
    main()