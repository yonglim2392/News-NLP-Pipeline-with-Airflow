from konlpy.tag import Okt
import re
import pandas as pd
from collections import Counter
import json

# 불용어 리스트 예시 (필요시 추가, 조정 가능)
stopwords = {'통해', '이번', '대한', '경우', '것', '수', '등', '및', '위해', '및', '더욱', '많은', '또한'}

def preprocess_and_extract_keywords(**context):
    execution_date = context['execution_date']
    today          = execution_date.strftime('%Y%m%d_%H%M')

    df    = pd.read_csv(f'/opt/airflow/files/news/{today}/news_{today}.csv')

    okt = Okt()
    all_nouns = []

    for idx, row in df.iterrows():
        text = f"{row['title']} {row['content']}"
        # 특수문자 제거
        text = re.sub(r'[^\w\s]', '', text)
        # 형태소 분석 및 명사 추출
        nouns = okt.nouns(text)
        # 길이가 너무 짧은 (1자) 명사 및 불용어 제거
        nouns = [noun for noun in nouns if len(noun) > 1 and noun not in stopwords]
        all_nouns.extend(nouns)

    # 명사 빈도 계산
    counter = Counter(all_nouns)
    common_keywords = counter.most_common(50)

    # 결과 저장
    with open(f'/opt/airflow/files/news/{today}/keywords_{today}.json', 'w', encoding='utf-8') as f:
        json.dump(common_keywords, f, ensure_ascii=False, indent=2)