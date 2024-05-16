import requests
import json
import xml.etree.ElementTree as etree

import time
import os

from apiKey import API_KEY

'''
    <Election code>
    District Election: 2
    PR election: 7
'''
def get_xml_content(url, params):
    timeout = 1
    while True:
        try:
            result = requests.get(url, params=params, timeout=5)
        except Exception:
            print(f'\nConnection timed out, Trying again ...')
            continue

        if result.status_code != 200:
            print(f'\nStatus code not 200, Trying again after {timeout} second(s)...')
            time.sleep(timeout)
            timeout <<= 1
            continue

        tree = etree.fromstring(str(result.content, encoding='UTF-8'))
        header = tree.find('header')

        if header is None:
            print(f'\nInvalid response, Trying again {timeout} second(s)...')
            time.sleep(timeout)
            timeout <<= 1
            continue
        
        result_code = header.find('resultCode').text
        if result_code != 'INFO-00':
            print(f'\nResult code {result_code}, Trying again after {timeout} second(s)...')
            print(params)
            print(str(result.content, encoding='UTF-8'))
            time.sleep(timeout)
            timeout <<= 1
            continue

        return tree


def check_election_code():
    rows = 100 # Max: 100
    data = []
    page = 0
    totalCount = 1

    while page * rows < totalCount:
        page += 1
        params = {'serviceKey': API_KEY, 'pageNo': page, 'numOfRows': rows }
        tree = get_xml_content('http://apis.data.go.kr/9760000/CommonCodeService/getCommonSgCodeList', params)

        totalCount = int(tree.find('body/totalCount').text)
        items = tree.find('body/items')

        for item in items:
            item_dict = {}
            for element in item:
                item_dict[element.tag] = element.text

            data.append(item_dict)

        time.sleep(0.5)

    return data
    

def get_election_districts(election_id):
    election_code = 2
    rows = 100 # Max: 100
    
    data = []
    page = 1

    while True:
        params = {'serviceKey': API_KEY, 'pageNo': str(page), 'numOfRows': str(rows), 'resultType': 'json', 'sgId': election_id, 'sgTypecode': election_code }
        result = requests.get('http://apis.data.go.kr/9760000/CommonCodeService/getCommonSggCodeList', params=params)

        if result.status_code != 200:
            print('page %d: Status code not 200, Trying again in 1 second...' % (page, ))
            time.sleep(1)
            continue
        
        try:
            content = json.loads(str(result.content, encoding='UTF-8'))['response']
        except Exception:
            print('page %d: Error decoding into json format, Trying again in 1 second...' % (page, ))
            time.sleep(1)
            continue

        if content['header']['resultCode'] != 'INFO-00':
            break

        items = content['body']['items']['item']
        data.extend(items)

        page += 1
        time.sleep(0.5)

    return data

def get_party_code(election_id):
    rows = 100
    data = []
    page = 0
    totalCount = 1

    while page * rows < totalCount:
        page += 1
        params = {'serviceKey': API_KEY, 'pageNo': page, 'numOfRows': rows, 'sgId': election_id }
        tree = get_xml_content('http://apis.data.go.kr/9760000/CommonCodeService/getCommonPartyCodeList', params)

        totalCount = int(tree.find('body/totalCount').text)
        items = tree.find('body/items')

        for item in items:
            item_dict = {}
            for element in item:
                item_dict[element.tag] = element.text

            data.append(item_dict)

        time.sleep(0.5)

    return data

def get_election_result_single(election_list_row, is_district):
    params = dict.copy(election_list_row)
    
    params['serviceKey'] = API_KEY
    params['numOfRows'] = 1
    params['pageNo'] = 1
    params['sgTypecode'] = 2 if is_district else 7
    params['wiwName'] = '합계'

    if not is_district:
        del params['sggName']

    data = []

    tree = get_xml_content('http://apis.data.go.kr/9760000/VoteXmntckInfoInqireService2/getXmntckSttusInfoInqire', params)
    item = tree.find('body/items/item')

    for i in range(1, 51):
        party = item.find('jd%02d' % (i, ))

        if party.text == None:
            break
        
        party_name = party.text
        cand_name = item.find('hbj%02d' % (i, )).text
        votes_recv = int(item.find('dugsu%02d' % (i, )).text)

        if is_district:
            data.append((party_name, cand_name, votes_recv))
        else:
            data.append((party_name, votes_recv))

    return data

def get_election_result(district_info):
    districts_cnt = len(district_info)
    district_accumul = []
    pr_accumul = {}

    blacklist = [(242, '20160413'), (46, '20200415')]

    for d in district_info:
        # Exception for general election in 2016, where there was only one candidate
        if (int(d['num']), d['sgId']) in blacklist:
            district_accumul.append([])
        else:
            print("Fetching district %d / %d (%.2f%%)..." % (int(d['num']), districts_cnt, int(d['num']) * 100 / districts_cnt), end='\r')
            district_accumul.append(get_election_result_single(d, True))
            

        pr_result = get_election_result_single(d, False)
        for name, votes in pr_result:
            if not name in pr_accumul.keys():
                pr_accumul[name] = 0

            pr_accumul[name] += votes

    return district_accumul, pr_accumul



if __name__ == '__main__':
    # codes = check_election_code()

    # for e in codes:
    #     print(e)

    download_dir = os.path.dirname(os.path.realpath(__file__)) + '\\election_data'
    try:
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
    except OSError:
        print('Error occurred while making data directory')
        exit()

    dates = ['20120411', '20160413', '20200415', '20240410']

    for date in dates:
        print("Fetching district info...", end='\r')
        district_info = get_election_districts(date)
        print("Fetching district info... Done")

        # print("Fetching party info...", end='\r')
        # party_info = get_party_code(date)
        # print("Fetching party info... Done")

        # party_code = {}
        # for row in party_info:
        #     party_code[row['jdName']] = row['pOrder']

        district, pr = get_election_result(district_info)

        district_file = open(f'{download_dir}\\{date}-district.csv', 'w')
        pr_file = open(f'{download_dir}\\{date}-pr.csv', 'w')

        for i in range(len(district)):
            row = []
            row.append(district_info[i]['sdName'])
            row.append(district_info[i]['sggName'])

            total_votes = 0
            for (party, name, votes) in district[i]:
                total_votes += votes

            for (party, name, votes) in district[i]:
                row.append(party)
                row.append(name)
                row.append('%.2f' % (votes / total_votes * 100))
            
            district_file.write(','.join(row) + '\n')

        for party, vote in pr.items():
            pr_file.write(f'{party}, {vote}\n')
        
        district_file.close()
        pr_file.close()
        print()