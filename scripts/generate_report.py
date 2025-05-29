from datetime import datetime
import pandas as pd
import json
import base64
from jinja2 import Template

def generate_report(**context):
    execution_date = context['execution_date']
    today          = execution_date.strftime('%Y%m%d_%H%M')
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 데이터 로드
    news_df = pd.read_csv(f'/opt/airflow/files/news/{today}/news_with_sentiment_{today}.csv')
    with open(f'/opt/airflow/files/news/{today}/keywords_{today}.json', 'r', encoding='utf-8') as f:
        top_keywords = json.load(f)

    # 키워드 TOP 10
    keyword_section = ''.join([f"<li>{keyword} ({count}회)</li>" for keyword, count in top_keywords[:10]])

    # 감성 분석 요약
    sentiment_counts = news_df['sentiment'].value_counts().to_dict()
    sentiment_summary = ''.join([f"<li>{label}: {count}건</li>" for label, count in sentiment_counts.items()])

    # 분야별 분석
    category_stats = news_df.groupby('category').agg({
        'title': 'count',
        'sentiment': lambda x: x.value_counts(normalize=True).to_dict()
    }).reset_index()
    
    category_section = ""
    for _, row in category_stats.iterrows():
        category = row['category']
        count = row['title']
        sentiments = ', '.join([f"{k}: {round(v*100, 1)}%" for k, v in row['sentiment'].items()])
        keywords = news_df[news_df['category'] == category]['summary'].str.cat(sep=' ')
        category_section += f"<tr><td>{category}</td><td>{count}</td><td>{sentiments}</td></tr>"

    # 워드클라우드 이미지 삽입 (base64 인코딩)
    with open(f'wordcloud_{today}.png', 'rb') as img_file:
        wordcloud_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    # 뉴스 요약 텍스트 (앞부분 5개만)
    top_keywords = [k[0] for k in top_keywords[:10]]

    # 뉴스 데이터프레임(news_df)에 'content'와 'title' 컬럼이 있다고 가정
    filtered_news = news_df[
        news_df.apply(lambda row: any(kw in row['title'] or kw in row['content'] for kw in top_keywords), axis=1)
    ]

    # 최대 10개 기사만 선택
    filtered_news = filtered_news.head(10)

    summary_list = ''.join([
        f"<li><a href='{row.link}' target='_blank'>{row.title}</a><br><small>{row.summary}</small></li>"
        for _, row in filtered_news.iterrows()
    ])

    with open('../templates/report_template.html', 'r', encoding='utf-8') as file:
        template_str = file.read()

    template = Template(template_str)
    html_content = template.render(
        date_str=date_str,
        keyword_section=keyword_section,
        sentiment_summary=sentiment_summary,
        wordcloud_base64=wordcloud_base64,
        category_section=category_section,
        summary_list=summary_list
    )

    report_path = f"/opt/airflow/files/news/news_report_{today}.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)