import requests
import json
import datetime
from binance.client import Client
import binance
from binance import exceptions

api_key = 'API_КЛЮЧ'
api_secret = 'SECRET_API_КЛЮЧ'

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
                                        order_market_buy(symbol, quantity=float(balance('BTC')['free']) / 2)
                                    except:
                                        continue

                                try:
                                    symbol = two_name + one_name
                                    quantity = round(float(balance(one_name)['free']) / price(symbol), 8)
                                    order_market_buy(symbol, quantity)
                                except binance.exceptions.BinanceAPIException as e:
                                    if 'Invalid' in e.message:
                                        try:
                                            symbol = one_name + two_name
                                            quantity = round(float(balance(one_name)['free']) / price(symbol), 8)
                                            order_market_sell(symbol, quantity)
                                        except Exception:
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
                                    quantity = round(float(balance(two_name)['free']) / price(symbol), 8)
                                    client.order_market_buy(symbol, quantity)
                                except binance.exceptions.BinanceAPIException as e:
                                    if 'Invalid symbol' in e.message:
                                        try:
                                            symbol = two_name + tree_name
                                            quantity = round(float(balance(two_name)['free']) / price(symbol), 8)
                                            order_market_sell(symbol, quantity)
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
                                    quantity = round(float(balance(tree_name)['free']) / price(symbol), 8)
                                    client.order_market_buy(symbol, quantity)
                                except binance.exceptions.BinanceAPIException as e:
                                    if 'Invalid' in e.message:
                                        try:
                                            symbol = tree_name + four_name
                                            quantity = round(float(balance(tree_name)['free']) / price(symbol), 8)
                                            order_market_sell(symbol, quantity)
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
                                    quantity = round(float(balance(four_name)['free']) / price(symbol), 8)
                                    client.order_market_buy(symbol, quantity)
                                except binance.exceptions.BinanceAPIException as e:
                                    if 'Invalid' in e.message:
                                        try:
                                            symbol = four_name + 'BTC'
                                            quantity = round(float(balance(four_name)['free']) / price(symbol), 8)
                                            order_market_sell(symbol, quantity)
                                        except Exception as e:
                                            print(e, 41)


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


def check(name_1, name_2):
    try:
        symbol = name_1 + name_2
        quantity = round(balance(name_2)['free'] / price(symbol), 8)
        order_market_buy(symbol, quantity)
    except binance.exceptions.BinanceAPIException as e:
        if 'Invalid' in e.message:
            symbol = name_2 + name_1
            quantity = round(balance(name_2)['free'] / price(symbol), 8)
            order_market_sell(symbol, quantity)


while True:
    binance_torg()
