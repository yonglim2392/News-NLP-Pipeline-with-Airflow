import os
import pandas as pd
from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 불용어 리스트 예시 (필요시 추가, 조정 가능)
stopwords = {'통해', '이번', '대한', '경우', '것', '수', '등', '및', '위해', '및', '더욱', '많은', '또한'}


def trend_analysis_and_visualization(**context):
    # 데이터 불러오기
    execution_date = context['execution_date']
    today          = execution_date.strftime('%Y%m%d_%H%M')
    df = pd.read_csv(f'/opt/airflow/files/news/{today}/news_with_sentiment_{today}.csv')

    okt = Okt()
    all_nouns = []

    for content in df['content']:
        try:
            nouns = okt.nouns(str(content))
            filtered = [word for word in nouns if len(word) > 1 and word not in stopwords]
            all_nouns.extend(filtered)
        except:
            continue

    # 단어 빈도 수 계산
    word_freq = Counter(all_nouns)
    top_words = word_freq.most_common(100)  # 상위 100개 키워드

    # 워드클라우드 생성
    font_path = os.path.join(os.path.dirname(__file__), '../fonts/malgun.ttf')
    wc = WordCloud(
                    font_path=font_path,  # 또는 다른 한글 폰트 경로
                    width=800,
                    height=400,
                    background_color='white'
                )
    wc.generate_from_frequencies(dict(top_words))

    # 시각화
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f'/opt/airflow/files/news/{today}/wordcloud_{today}.png')
    plt.close()