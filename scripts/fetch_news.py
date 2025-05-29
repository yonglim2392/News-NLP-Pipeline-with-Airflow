from newspaper import Article
import feedparser
import re
from datetime import datetime
import pandas as pd
import pytz

def get_full_text(url):
    try:
        article = Article(url, language='ko')
        article.download()
        article.parse()
        text = article.text

        # 1. 줄바꿈 제거
        text = text.replace('\n', ' ')

        # 2. 기자 이름 + 이메일 제거 (ex: 홍길동 기자 abc@domain.com)
        text = re.sub(r'\b[\w가-힣]+ 기자\s+[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}', '', text)

        # 3. 불필요한 다중 공백 정리
        text = re.sub(r'\s+', ' ', text).strip()

        return text
    except Exception as e:
        print(f"[오류] 기사 전문 크롤링 실패: {url} - {e}")
        return None
    
def fetch_news(**context):
    execution_date = context['execution_date']
    today          = execution_date.strftime('%Y%m%d_%H%M')
    
    rss_urls = {'정치': 'https://rss.etnews.com/Section901.xml',
                '경제': 'https://rss.etnews.com/Section902.xml',
                '사회': 'https://rss.etnews.com/Section903.xml',
                '생활/문화': 'https://rss.etnews.com/Section904.xml',
                '세계': 'https://rss.etnews.com/Section905.xml',
                'IT/과학': 'https://rss.etnews.com/Section906.xml',
                }

    all_news = []

    for category, url in rss_urls.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published_parsed = entry.get('published_parsed')
            if not published_parsed:
                continue

            pub_date = datetime(*published_parsed[:6], tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Seoul'))

            if pub_date.date() == datetime.now(pytz.timezone('Asia/Seoul')).date():
                content = get_full_text(entry.link)
                all_news.append({
                    'title': entry.title,
                    'summary': entry.summary,
                    'content': content,
                    'link': entry.link,
                    'category': category,
                    'published': pub_date
                })

    df = pd.DataFrame(all_news)
    df.to_csv(f'/opt/airflow/files/news/{today}/news_{today}.csv', index=False, encoding='utf-8-sig')
