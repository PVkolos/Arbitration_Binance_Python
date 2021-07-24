import requests
import json
import datetime
from binance.client import Client
import binance
from binance import exceptions
import math
import time

api_key = ''
api_secret = ''

client = Client(api_key, api_secret)


def binance_torg():
    try:
        bookTicker = requests.get('https://api.binance.com/api/v3/ticker/bookTicker')
        bookTicker = json.loads(bookTicker.text)
        Book = {}
        for block in bookTicker:
            Book.update({block["symbol"]: [block["bidPrice"], block["askPrice"]]})

        Info_list = requests.get('https://api.binance.com/api/v3/exchangeInfo')
        Info_list = json.loads(Info_list.text)

        Data = {}
        lis = []
        for block in Info_list["symbols"]:
            if block["status"] == "TRADING" and 'UP' not in block['symbol'] and 'DOWN' not in block['symbol']:
                Data.update({block["baseAsset"]: {}})
                Data.update({block["quoteAsset"]: {}})

        for block in Info_list["symbols"]:
            if block["status"] == "TRADING" and 'UP' not in block['symbol'] and 'DOWN' not in block['symbol']:
                Data[block["baseAsset"]].update({block["quoteAsset"]: float(Book[block["symbol"]][0])})
                Data[block["quoteAsset"]].update({block["baseAsset"]: 1 / (float(Book[block["symbol"]][1]))})

        for one_name in Data:
            for two_name in Data[one_name]:
                for tree_name in Data[two_name]:
                    for four_name in Data[tree_name]:
                        if four_name == one_name:
                            sum_start = 1
                            tr_1 = Data[one_name][two_name] * sum_start
                            tr_2 = Data[two_name][tree_name] * tr_1
                            sum_end = Data[tree_name][four_name] * tr_2
                            pro = (sum_end - sum_start) / sum_end * 100
                            if pro >= 0.1 and pro not in lis:
                                now = datetime.datetime.now()
                                print(f'{one_name} -> {two_name} -> {tree_name} -> {four_name} ----> {pro} {now.strftime("%H:%M:%S")}')
                                if float(balance(one_name)['free']) == 0:
                                    try:
                                        symbol = one_name + 'BTC'
                                        pre = get_symbol_info(one_name, 'BTC')
                                        quantity = float(balance('BTC')['free']) / price(symbol)
                                        final = math.floor(quantity * 10 ** pre) / 10 ** pre
                                        order_market_buy(symbol, final)
                                        print(f"Купленно {one_name} в количестве {final}")
                                    except Exception as e:
                                        e = str(e)
                                        if ('Invalid' in e) or ('closed' in e) or (not pre):
                                            try:
                                                symbol = 'BTC' + one_name
                                                pre = get_symbol_info('BTC', one_name)
                                                quantity = float(balance('BTC')['free']) * 0.999
                                                final = (math.floor(quantity * 10 ** pre) / 10 ** pre)
                                                order_market_sell(symbol, final)
                                                print(f"Купленно {one_name} в количестве {final}")
                                            except Exception as r:
                                                print('Нет 0 0', r)
                                                continue
                                        else:
                                            print('Нет 0 1', e)
                                            continue

                                try:
                                    print('Стадия 1')
                                    symbol = two_name + one_name
                                    pre = get_symbol_info(two_name, one_name)
                                    quantity = float(balance(one_name)['free']) / price(symbol) * 0.999
                                    final = (math.floor(quantity * 10 ** pre) / 10 ** pre)
                                    order_market_buy(symbol, final)
                                    print(f"Купленно {two_name} в количестве {final}")
                                except Exception as e:
                                    e = str(e)
                                    if ('Invalid' in e) or ('closed' in e) or (not pre):
                                        try:
                                            symbol = one_name + two_name
                                            pre = get_symbol_info(one_name, two_name)
                                            quantity = float(balance(one_name)['free']) * 0.999
                                            final = (math.floor(quantity * 10 ** pre) / 10 ** pre)
                                            order_market_sell(symbol, final)
                                            print(f"Купленно {two_name} в количестве {final}")
                                        except Exception as r:
                                            print('Нет 1 0', r)
                                            check('BTC', one_name)
                                            continue
                                    else:
                                        print('Нет 1 1', e)
                                        check('BTC', one_name)
                                        continue

                                try:
                                    print('Стадия 2')
                                    symbol = tree_name + two_name
                                    pre = get_symbol_info(tree_name, two_name)
                                    quantity = float(balance(two_name)['free']) / price(symbol) * 0.999
                                    final = (math.floor(quantity * 10 ** pre) / 10 ** pre)
                                    order_market_buy(symbol, final)
                                    print(f'Купленно {tree_name} в количестве {final}')
                                except Exception as e:
                                    e = str(e)
                                    if ('Invalid symbol' in e) or ('closed' in e) or (not pre):
                                        try:
                                            symbol = two_name + tree_name
                                            pre = get_symbol_info(two_name, tree_name)
                                            quantity = float(balance(two_name)['free']) * 0.999
                                            final = (math.floor(quantity * 10 ** pre) / 10 ** pre)
                                            order_market_sell(symbol, final)
                                            print(f'Купленно {tree_name} в количестве {final}')
                                        except Exception as r:
                                            print('Нет 2 0', r)
                                            check('BTC', two_name)
                                            continue
                                    else:
                                        print('Нет 2 1', e)
                                        check('BTC', two_name)
                                        continue

                                try:
                                    print('Стадия 3')
                                    symbol = four_name + tree_name
                                    pre = get_symbol_info(four_name, tree_name)
                                    quantity = float(balance(tree_name)['free']) / price(symbol)
                                    final = (math.floor(quantity * 10 ** pre) / 10 ** pre) * 0.999
                                    order_market_buy(symbol, final)
                                    print(f'Купленно {four_name} в количестве {final}')
                                except Exception as e:
                                    e = str(e)
                                    if ('Invalid' in e) or ('closed' in e) or (not pre):
                                        try:
                                            symbol = tree_name + four_name
                                            pre = get_symbol_info(tree_name, four_name)
                                            quantity = float(balance(tree_name)['free']) * 0.999
                                            final = (math.floor(quantity * 10 ** pre) / 10 ** pre)
                                            order_market_sell(symbol, final)
                                            print(f'Купленно {four_name} в количестве {final}')
                                        except Exception as r:
                                            print('Нет 3 0', r)
                                            check('BTC', tree_name)
                                            continue
                                    else:
                                        print('Нет 3 1', e)
                                        check('BTC', tree_name)
                                        continue

                                if four_name != 'BTC':
                                    try:
                                        print('Стадия 4')
                                        symbol = 'BTC' + four_name
                                        pre = get_symbol_info('BTC', four_name)
                                        quantity = float(balance(four_name)['free']) / price(symbol)
                                        final = (math.floor(quantity * 10 ** pre) / 10 ** pre) * 0.999
                                        order_market_buy(symbol, final)
                                        print(f'Купленно BTC в количестве {final}')
                                    except Exception as e:
                                        e = str(e)
                                        if ('Invalid' in e) or ('closed' in e) or (not pre):
                                            try:
                                                symbol = four_name + 'BTC'
                                                pre = get_symbol_info(four_name, 'BTC')
                                                quantity = float(balance(four_name)['free']) * 0.999
                                                final = (math.floor(quantity * 10 ** pre) / 10 ** pre)
                                                order_market_sell(symbol, final)
                                                print(f'Купленно BTC в количестве {final}')
                                            except Exception as r:
                                                print('Нет 4', r)
                                        else:
                                            print('Нет 4 1', e)
                                now2 = datetime.datetime.now()
                                print(now2 - now)
                                lis.append(pro)
    except Exception:
        return 0


def price(symbol):
    price = client.get_avg_price(symbol=symbol)['price']
    return float(price)


def balance(symbol):
    balance = client.get_asset_balance(asset=symbol, recvWindow=50000)
    return balance


def order_market_buy(symbol, quantity):
    client.order_market_buy(symbol=symbol, quantity=quantity, recvWindow=50000)


def order_market_sell(symbol, quantity):
    client.order_market_sell(symbol=symbol, quantity=quantity, recvWindow=50000)


def check(name_1, name_2):
    try:
        symbol = name_2 + name_1
        order_market_sell(symbol, float(balance(name_2)['free']))
        print('check')
    except Exception as e:
        print('нет check', e)


def get_symbol_info(n1, n2):
    try:
        one = client.get_symbol_info(n1 + n2)
        q = float(one['filters'][2]['stepSize'])
        precision = int(round(-math.log(q, 10), 0))
        return precision
    except Exception as e:
        pass
        # print('Нет get_symbol_info', e)

while True:
    binance_torg()
    time.sleep(1)
