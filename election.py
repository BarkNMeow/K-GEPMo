import requests
import json
import xml.etree.ElementTree as etree

import time

from apiKey import API_KEY

'''
    <Election code>
    District Election: 2
    PR election: 7
'''

def check_election_code():
    rows = 100 # Max: 100
    
    # result = requests.get('http://apis.data.go.kr/9760000/CommonCodeService/getCommonSggCodeList', params=params)

    data = []
    page = 1

    while True:
        params = {'serviceKey': API_KEY, 'pageNo': str(page), 'numOfRows': str(rows) }
        result = requests.get('http://apis.data.go.kr/9760000/CommonCodeService/getCommonSgCodeList', params=params)

        if result.status_code != 200:
            print('Status code not 200')
            break

        tree = etree.fromstring(str(result.content, encoding='UTF-8'))
        header = tree.find('header')

        if header.find('resultCode').text != 'INFO-00':
            break

        items = tree.find('body/items')

        for item in items:
            item_dict = {}
            for element in item:
                item_dict[element.tag] = element.text

            data.append(item_dict)

        page += 1
        time.sleep(0.5)

    return data

def get_election_districts(election_id):
    election_code = 2
    rows = 100 # Max: 100
    
    data = []
    page = 1

    while True:
        params = {'serviceKey': API_KEY, 'pageNo': str(page), 'numOfRows': str(rows), 'resultType': 'json', 'sgId': str(election_id), 'sgTypecode': str(election_code) }
        result = requests.get('http://apis.data.go.kr/9760000/CommonCodeService/getCommonSggCodeList', params=params)

        if result.status_code != 200:
            break

        content = json.loads(str(result.content, encoding='UTF-8'))['response']

        if content['header']['resultCode'] != 'INFO-00':
            break

        items = content['body']['items']['item']
        data.extend(items)

        page += 1
        time.sleep(0.5)

    return data

def get_election_result(election_list_row, is_district):
    params = dict.copy(election_list_row)
    
    params['serviceKey'] = API_KEY
    params['numOfRows'] = 100
    params['pageNo'] = 1
    params['sgTypecode'] = 2 if is_district else 7

    if not is_district:
        del params['sggName']

    data = []
        
    result = requests.get('http://apis.data.go.kr/9760000/VoteXmntckInfoInqireService2/getXmntckSttusInfoInqire', params=params)

    if result.status_code != 200:
        print('Status code not 200')
        return data

    tree = etree.fromstring(str(result.content, encoding='UTF-8'))
    header = tree.find('header')

    if header.find('resultCode').text != 'INFO-00':
        print(str(result.content, encoding='UTF-8'))
        return data

    item = tree.find('body/items/item')

    for i in range(1, 51):
        party = item.find('jd%02d' % (i, ))

        if party.text == None:
            break
        
        party_name = party.text
        cand_name = item.find('hbj%02d' % (i, )).text
        votes_recv = int(item.find('dugsu%02d' % (i, )).text)

        data.append((party_name, cand_name, votes_recv))

    return data



if __name__ == '__main__':
    # codes = check_election_code()

    # for e in codes:
    #     print(e)

    districts = get_election_districts('20200415')
    for d in districts:
        # print(d)
        # print('지역구:', get_election_result(d, True))
        time.sleep(0.5)
        print('비례대표:', get_election_result(d, False))
        time.sleep(0.25)