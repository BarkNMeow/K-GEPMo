from pytrends.request import TrendReq


if __name__ == '__main__':
    pytrends = TrendReq()

    kw_list = ["Blockchain"]
    pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='', gprop='')
    print(pytrends.interest_over_time())