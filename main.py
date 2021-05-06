import requests
import json
import time
import datetime


def binance():
    try:
        v = 2.8
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
                    for four_nema in Data[tree_name]:
                        if four_nema == one_name:
                            sum_start = 1
                            tr_1 = Data[one_name][two_name] * sum_start
                            tr_2 = Data[two_name][tree_name] * tr_1
                            sum_end = Data[tree_name][four_nema] * tr_2
                            now = datetime.datetime.now()
                            pro = ((max(sum_end, sum_start) - min(sum_end, sum_start)) / min(sum_end, sum_start)) * 100
                            if pro >= v and pro not in lis:
                                print(f"{one_name} -> {two_name} -> {tree_name} -> {four_nema} ----> {pro}", now.strftime("%H:%M:%S"))
                                lis.append(pro)
    except Exception:
        return 0


while True:
    a = binance()
    time.sleep(0.001)
