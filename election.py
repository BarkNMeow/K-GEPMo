import requests
import json

if __name__ == '__main__':
    api_key = 
    election_id = '20220415'
    page = 1
    rows = 100 # Max: 100
    election_code = 2 # General election

    # params = {'serviceKey': api_key, 'pageNo': str(page), 'numOfRows': str(rows), 'resultType': 'json', 'sgId': str(election_code), 'sgTypecode': str(election_id) }
    # result = requests.get('http://apis.data.go.kr/9760000/CommonCodeService/getCommonSggCodeList', params=params)

    for i in range(3):
        params = {'serviceKey': api_key, 'pageNo': str(page), 'numOfRows': str(rows) }
        result = requests.get('http://apis.data.go.kr/9760000/CommonCodeService/getCommonSgCodeList', params=params)

        if result.status_code != 200:
            break

        content = json.
        print(str(result.content, encoding='UTF-8'))