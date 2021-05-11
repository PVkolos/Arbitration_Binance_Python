import requests
import json
import time
import datetime
from binance.client import Client
import binance
from binance import exceptions


ass = []


def binance_torg():
    try:
        global ass
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
                                if not balance(one_name):
                                    try:
                                        order_market_buy(f'{one_name}BTC', quantity=balance('BTC') / 2)
                                    except:
                                        print('НЕт денег даже на биток!')
                                        continue

                                try:
                                    symbol = two_name + one_name
                                    quantity = round(balance(one_name) / price(symbol), 8)
                                    client.order_market_buy(symbol, quantity)
                                except binance.exceptions.BinanceAPIException as e:
                                    if 'Invalid' in e.message:
                                        try:
                                            print(f'{one_name}{two_name}')
                                            symbol = one_name + two_name
                                            quantity = round(balance(one_name) / price(symbol), 8)
                                            order_market_sell(symbol, quantity)
                                        except Exception as e:
                                            print(e, 1)
                                            try:
                                                symbol = 'BTC' + one_name
                                                quantity = round(balance(one_name) / price(symbol), 8)
                                                order_market_buy(symbol, quantity)
                                            except:
                                                symbol = one_name + 'BTC'
                                                quantity = round(balance(one_name) / price(symbol), 8)
                                                order_market_buy(symbol, quantity)
                                            continue
                                    else:
                                        order_market_buy(f'BTC{one_name}', quantity)
                                        print(e.message, '2')
                                        continue

                                except Exception as e:
                                    print(e, 10)
                                    order_market_buy(f'BTC{one_name}', quantity)
                                    continue


                                try:
                                    print(2)
                                    symbol = tree_name + two_name
                                    print(symbol)
                                    print(balance(two_name))
                                    quantity = round((balance(two_name)) / price(symbol), 8)
                                    client.order_market_buy(symbol, quantity)
                                except binance.exceptions.BinanceAPIException as e:
                                    if 'Invalid symbol' in e.message:
                                        try:
                                            print(e)
                                            symbol = two_name + tree_name
                                            quantity = round((balance(two_name)) / price(symbol), 8)
                                            order_market_sell(symbol, quantity)
                                        except Exception as e:
                                            print(e, 21)
                                    else:
                                        print(e.message, 22)
                                except Exception as e:
                                    print(e, 20)

                                try:
                                    print(3)
                                    symbol = four_name + tree_name
                                    quantity = round((balance(tree_name)) / price(symbol), 8)
                                    client.order_market_buy(symbol, quantity)
                                except binance.exceptions.BinanceAPIException as e:
                                    if 'Invalid' in e.message:
                                        try:
                                            symbol = tree_name + four_name
                                            quantity = round((balance(tree_name)) / price(symbol), 8)
                                            order_market_sell(symbol, quantity)
                                        except Exception as e:
                                            print(e, 31)
                                    else:
                                        print(e.message, 32)
                                except Exception as e:
                                    print(e, 30)


                                try:
                                    print(4)
                                    symbol = 'BTC' + four_name
                                    quantity = round((balance(four_name)) / price(symbol), 8)
                                    client.order_market_buy(symbol, quantity)
                                except binance.exceptions.BinanceAPIException as e:
                                    if 'Invalid' in e.message:
                                        try:
                                            symbol = four_name + 'BTC'
                                            quantity = round((balance(four_name)) / price(symbol), 8)
                                            order_market_sell(symbol, quantity)
                                        except Exception as e:
                                            print(e, 41)
                                    else:
                                        print(e.message, 42)
                                except Exception as e:
                                    print(e, 40)

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
    client.order_market_buy(symbol=symbol, quantity=quantity)
    print(f'Успешно куплена валютная пара {symbol} в количестве {quantity}!')


def order_market_sell(symbol, quantity):
    client.order_market_sell(symbol=symbol, quantity=quantity)
    print(f'Успешно продана валютная пара {symbol} в количестве {quantity}!')


api_key = 'oifo5bGgAopbUJ3EKpuY2Yi7PyjgBUx2icW3J3ll1tCrDKqmzoLuq8AtddcZtXXv'
api_secret = 'IAk7W62HovboVfYgt5FirDHZ2r9uowRxDe9cJ31yx0rukSjqGtHIkQO9MGMu5Ejr'

client = Client(api_key, api_secret)

while True:
    binance_torg()
