from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
import pandas as pd

def sentiment_analysis(**context):
    # 뉴스 데이터 로드
    execution_date = context['execution_date']
    today          = execution_date.strftime('%Y%m%d_%H%M')
    df = pd.read_csv(f'/opt/airflow/files/news/{today}/news_{today}.csv')

    # 모델과 토크나이저 로드
    model_name = "nlpmhp/korean_sentiment_classification"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # 파이프라인 생성
    classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, device=-1)  # GPU 사용 시 device=0

    label_map = {'0': '부정',
                 '1': '긍정'}

    sentiments = []
    for text in df['content']:
        try:
            result = classifier(text[:512])[0]
            label = label_map.get(result['label'], 'unknown')  # 레이블 매핑
            score = result['score']
        except Exception as e:
            label = '중립'
            score = 0.0
        sentiments.append({'label': label, 'score': score})

    # 결과 병합
    df['sentiment'] = [s['label'] for s in sentiments]
    df['confidence'] = [s['score'] for s in sentiments]

    df.to_csv(f'/opt/airflow/files/news/{today}/news_with_sentiment_{today}.csv', index=False)
