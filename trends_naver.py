import urllib.request
from random import random
from time import sleep
from datetime import datetime, timedelta
import os.path
import json
import pandas as pd

from openai import OpenAI
from apiKey import OPENAI_KEY, NAVER_ID, NAVER_PSWD

openai = OpenAI(api_key=OPENAI_KEY)

dates = ['20160413', '20200415', '20240410']
dates_start = ['20160314', '20200316', '20240311']

def format_date(date: str) -> str:
    return "%s-%s-%s" % (date[:4], date[4:6], date[6:])

def get_naver_trends(startDate, endDate, kw_list):    
    body = {}
    body['startDate'] = format_date(startDate)
    body['endDate'] = format_date(endDate)
    body['timeUnit'] = 'date'
    body['keywordGroups'] = [{'groupName': x, 'keywords': [x]} for x in kw_list]
    body = json.dumps(body)
    
    request = urllib.request.Request("https://openapi.naver.com/v1/datalab/search")
    request.add_header("X-Naver-Client-Id",NAVER_ID)
    request.add_header("X-Naver-Client-Secret",NAVER_PSWD)
    request.add_header("Content-Type","application/json")

    while True:
        response = urllib.request.urlopen(request, data=body.encode("utf-8"))
        rescode = response.getcode()

        if rescode != 200:
            print(rescode)
            raise Exception
        else:
            break
    
    response_body = str(response.read().decode('utf-8'))
    response_body = json.loads(response_body)
    data = response_body['results']

   # Initialize a dictionary to hold the data
    df_dict = {}

    # Extract the periods to ensure the rows align correctly
    periods = [record['period'] for record in data[0]['data']]

    # Populate the dictionary with titles as keys and ratios as values
    for entry in data:
        title = entry['title']
        df_dict[title] = [record['ratio'] for record in entry['data']]

    # Create the DataFrame
    df = pd.DataFrame(df_dict)
    return df

def get_sentiment(name: str, date_start:str, search_volume:list[int]):
    dt = datetime.strptime(date_start, '%Y%m%d')
    score_result = []

    for sv in search_volume:
        after_date = dt.strftime('%Y-%m-%d')
        before_dt = dt + timedelta(days=1)
        before_date = before_dt.strftime('%Y-%m-%d')

        if sv > 1:
            results = get_successful_news(name, after_date, before_date)
            sleep_total = 20
            scores = []

            for result in results:
                if result['title'] == '':
                    continue

                title = result['title']
                text = result['text']

                chat_completion = openai.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": f"이건 {name} 국회의원 후보에 대한 글의 제목과 본문 앞부분이야. 이 글이 {name} 후보의 지지율에 어떤 영향을 줄 거 같은지 -10점에서 10점 사이의 정수로 평가해. 10은 최고 긍정, -10은 최고 부정이야. 반드시 설명이나 단위 없이 숫자로만 답변해야돼. 만약 {name} 후보와 관련이 없다고 여겨지면 정수나 설명 없이 무조건 None이라고만 대답해. {title} {text}",
                        }
                    ],
                    model="gpt-3.5-turbo-0125",
                )
                
                # Stupid ChatGPT makes some problem
                content = chat_completion.choices[0].message.content
                content = content.replace('\n', ' ')
                content = content.split(' ')[0].replace('.', '')
                print(f'<{title}>\n{text}\n점수: {content}')
                
                if content != 'None':
                    number = int(content)
                    scores.append(int(number))
                        
                sleep_total -= 1.5
                sleep(1.5)

            avg_score = 0 if len(scores) == 0 else (sum(scores) / len(scores))
            score_result.append(avg_score)
            sleep(sleep_total + 5 * random())
        else:
            score_result.append(0)
        
        dt = before_dt

    return score_result

if __name__ == '__main__':
    for date, date_start in zip(dates, dates_start):
        timeframe = format_date(date_start) + ' ' + format_date(date)
        f = open(f'election_data\\{date}-district.csv', 'r')

        for line in f:
            line = line.split(',')
            
            city = line[0]
            district_name = line[1]

            if os.path.exists(f'sentiment_naver\\{date}_{city}_{district_name}.csv'):
                continue
            
            print(f'Investigating: {date} {city} {district_name}')
            line = line[2:]
            i = 0
            kw_list = []

            while i < len(line):
                party, name, vote = line[i:i+3]
                if float(vote) > 10:
                    kw_list.append(name)
                i += 3

            print('Fetching Naver Trends data...')

            backoff_rate = 1
            while True:
                try:
                    trends = get_naver_trends(date_start, date, kw_list)
                    break
                except Exception:
                    # Exponential backoff whenever fetch fails (mostly due to 429: Too many requests)
                    print(f'Trying to get Naver Trends again... (backoff rate: {backoff_rate})')
                    sleep((10 + random() * 10) * backoff_rate)
                    if backoff_rate < 8:
                        backoff_rate *= 2
                    continue
            
            print(trends)
            if trends.empty:
                # If empty, make next request 5~10 seconds later
                sleep(5 + random() * 5)
                continue

            for i, name in enumerate(kw_list):
                scores = get_sentiment(name, date_start, list(trends[name]))
                trends.insert(2*i + 1, f'{name}_sentiment', scores)

            trends.to_csv(f'sentiment_naver\\{date}_{city}_{district_name}.csv', index=False)