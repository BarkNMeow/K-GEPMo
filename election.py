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

def get_district_election_list(election_id):
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

def get_district_election_result(election_list_row):
    if election_list_row['sgTypecode'] != '2':
        type_code = election_list_row['sgTypecode']
        raise Exception(f'Expected sgTypeCode 2, found {type_code}')
    
    params = dict.copy(election_list_row)
    
    # del params['num']
    params['serviceKey'] = API_KEY
    params['numOfRows'] = str(100)
    params['pageNo'] = str(1)

    data = []
    page = 0
        
    result = requests.get('http://apis.data.go.kr/9760000/VoteXmntckInfoInqireService2/getXmntckSttusInfoInqire', params=params)

    if result.status_code != 200:
        print('Status code not 200')
        return

    tree = etree.fromstring(str(result.content, encoding='UTF-8'))
    header = tree.find('header')

    if header.find('resultCode').text != 'INFO-00':
        return

    item = tree.find('body/items/item')

    for i in range(1, 51):
        party = item.find('jd%02d' % (i, ))

        if party.text == None:
            break
        
        party_name = party.text
        cand_name = item.find('hbj%02d' % (i, )).text
        votes_recv = int(item.find('dugsu%02d' % (i, )).text)

        data.append((party_name, cand_name, votes_recv))

    page += 1

    return data    


if __name__ == '__main__':

    # codes = check_election_code()

    # for e in codes:
    #     print(e)

    districts = get_district_election_list('20200415')

    for d in districts:
        print(d)
        print(get_district_election_result(d))
        time.sleep(0.25)