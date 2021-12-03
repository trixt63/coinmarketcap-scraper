'''
This program is to parse time, price and volume values 
after they are crawled
'''
from datetime import datetime as dt

def parse_time(day_str, hour_str):
    time_index = dt.strptime(day_str+' '+hour_str, '%m/%d/%Y %I:%M:%S %p')
    return time_index 


def parse_vol24h(vol24h_str):
    # vol24h has the format: $<number><unit>. e.g: $1.45B
    # if vol24h is less than 1 million, treated as usual
    units_list = {'M': 1e6, 'B':1e9}
    unit = vol24h_str[-1]
    if unit in units_list:
        vol24h = float(vol24h_str[1:-1]) * units_list[unit]
    else:
        vol24h = float(vol24h_str[1:])
    return vol24h

def parse_money(money_str):
    # vol24h has the format: $<number><unit>. e.g: $1.45B
    # if vol24h is less than 1 million, treated as usual
    units_list = {'M': 1e6, 'B':1e9}
    unit = money_str[-1]
    if unit in units_list:
        money = float(money_str[1:-1].replace(',','')) * units_list[unit]
    else:
        money = float(money_str[1:].replace(',',''))
    return money 
