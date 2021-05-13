import requests
import json
import datetime
from binance.client import Client
import binance
from binance import exceptions
import math

api_key = 'ykVLRPI5KCDkp4lVLHa5Elyx4LR6h5mRJxlT5cE7TGxMEIcaEiRYKuoXPPktVfv4'
api_secret = 'BPLBXLJ0UmT8r0ijoVzxJ2KVyAwQOMjuAiDm5T730JC7iAkup6O8HdvcXjJjj6Iv'

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
            if block["status"] == "TRADING":
                Data.update({block["baseAsset"]: {}})
                Data.update({block["quoteAsset"]: {}})

        for block in Info_list["symbols"]:
            if block["status"] == "TRADING":
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
                            now = datetime.datetime.now()
                            pro = ((max(sum_end, sum_start) - min(sum_end, sum_start)) / min(sum_end, sum_start)) * 100
                            if pro >= 2 and pro not in lis:
                                print(f'{one_name} -> {two_name} -> {tree_name} -> {four_name} ----> {pro} {now.strftime("%H:%M:%S")}')
                                if float(balance(one_name)['free']) == 0:
                                    try:
                                        symbol = one_name + 'BTC'
                                        rou = get_symbol_info(symbol)
                                        q = round(float(balance('BTC')['free']) / 2, rou)
                                        order_market_buy(symbol, quantity=q)
                                        print(f"Купленно {one_name} в количестве {q}")
                                    except Exception as e:
                                        continue

                                try:
                                    symbol = two_name + one_name
                                    rou = get_symbol_info(symbol)
                                    quantity = round(float(balance(one_name)['free']) / price(symbol), rou)
                                    order_market_buy(symbol, quantity)
                                    print(f"Купленно {two_name} в количестве {quantity}")
                                except binance.exceptions.BinanceAPIException as e:
                                    if 'Invalid' in e.message:
                                        try:
                                            symbol = one_name + two_name
                                            rou = get_symbol_info(symbol)
                                            quantity = round(float(balance(one_name)['free']) / price(symbol), rou)
                                            order_market_sell(symbol, quantity)
                                            print(f"Купленно {two_name} в количестве {quantity}")
                                        except Exception as e:
                                            check('BTC', one_name)
                                            continue
                                    else:
                                        check('BTC', one_name)
                                        continue

                                except Exception:
                                    check('BTC', one_name)
                                    continue

                                try:
                                    symbol = tree_name + two_name
                                    rou = get_symbol_info(symbol)
                                    quantity = round(float(balance(two_name)['free']) / price(symbol), rou)
                                    order_market_buy(symbol, quantity)
                                    print(f'Купленно {tree_name} в количестве {quantity}')
                                except binance.exceptions.BinanceAPIException as e:
                                    if 'Invalid symbol' in e.message:
                                        try:
                                            symbol = two_name + tree_name
                                            rou = get_symbol_info(symbol)
                                            quantity = round(float(balance(two_name)['free']) / price(symbol), rou)
                                            order_market_sell(symbol, quantity)
                                            print(f'Купленно {tree_name} в количестве {quantity}')
                                        except Exception:
                                            check('BTC', two_name)
                                            continue
                                    else:
                                        check('BTC', two_name)
                                        continue
                                except Exception:
                                    check('BTC', two_name)
                                    continue

                                try:
                                    symbol = four_name + tree_name
                                    rou = get_symbol_info(symbol)
                                    quantity = round(float(balance(tree_name)['free']) / price(symbol), rou)
                                    order_market_buy(symbol, quantity)
                                    print(f'Купленно {four_name} в количестве {quantity}')
                                except binance.exceptions.BinanceAPIException as e:
                                    if 'Invalid' in e.message:
                                        try:
                                            symbol = tree_name + four_name
                                            rou = get_symbol_info(symbol)
                                            quantity = round(float(balance(tree_name)['free']) / price(symbol), rou)
                                            order_market_sell(symbol, quantity)
                                            print(f'Купленно {four_name} в количестве {quantity}')
                                        except Exception:
                                            check('BTC', tree_name)
                                            continue
                                    else:
                                        check('BTC', tree_name)
                                        continue
                                except Exception:
                                    check('BTC', tree_name)
                                    continue


                                try:
                                    symbol = 'BTC' + four_name
                                    rou = get_symbol_info(symbol)
                                    quantity = round(float(balance(four_name)['free']) / price(symbol), rou)
                                    order_market_buy(symbol, quantity)
                                    print(f'Купленно BTC в количестве {quantity}')
                                except binance.exceptions.BinanceAPIException as e:
                                    if 'Invalid' in e.message:
                                        try:
                                            symbol = four_name + 'BTC'
                                            rou = get_symbol_info(symbol)
                                            quantity = round(float(balance(four_name)['free']) / price(symbol), rou)
                                            order_market_sell(symbol, quantity)
                                            print(f'Купленно BTC в количестве {quantity}')
                                        except Exception as e:


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
    print(f'Успешно куплена валютная пара {symbol} в количестве {quantity}!')


def order_market_sell(symbol, quantity):
    client.order_market_sell(symbol=symbol, quantity=quantity)
    print(f'Успешно продана валютная пара {symbol} в количестве {quantity}!', recvWindow=50000)


def check(name_1, name_2):
    try:
        symbol = name_1 + name_2
        rou = get_symbol_info(symbol)
        quantity = round(balance(name_2)['free'] / price(symbol), rou)
        order_market_buy(symbol, quantity)
    except binance.exceptions.BinanceAPIException as e:
        if 'Invalid' in e.message:
            symbol = name_2 + name_1
            rou = get_symbol_info(symbol)
            quantity = round(balance(name_2)['free'] / price(symbol), rou)
            order_market_sell(symbol, quantity)


def get_symbol_info(symbol):
    one = client.get_symbol_info(symbol)
    q = float(one['filters'][2]['stepSize'])
    precision = int(round(-math.log(q, 10), 0))
    return precision


while True:
    binance_torg()
