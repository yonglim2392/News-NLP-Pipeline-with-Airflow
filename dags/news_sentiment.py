from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pendulum


from scripts.fetch_news import *
from scripts.extract_keywords import *
from scripts.sentiment_analysis import *
from scripts.trend_visualization import *
from scripts.generate_report import *

# 지역 시간대
kst = pendulum.timezone("Asia/Seoul")


# DAG 정의
def create_dag():
    with DAG(
        dag_id="news_sentiment_trend_dag",
        start_date=datetime(2025, 5, 20, tzinfo=kst),
        schedule_interval="0 8 * * *",  # 매일 08시 KST 실행
        catchup=False,
        default_args={
            "retries": 1,
            "retry_delay": timedelta(minutes=5),
        },
        tags=["NLP", "Airflow", "News"],
    ) as dag:

        task_fetch_news = PythonOperator(
            task_id="fetch_news",
            python_callable=fetch_news,
        )

        task_preprocess = PythonOperator(
            task_id="preprocess_and_extract_keywords",
            python_callable=preprocess_and_extract_keywords,
        )

        task_sentiment = PythonOperator(
            task_id="sentiment_analysis",
            python_callable=sentiment_analysis,
        )

        task_trend = PythonOperator(
            task_id="trend_analysis_and_visualization",
            python_callable=trend_analysis_and_visualization,
        )

        task_report = PythonOperator(
            task_id="generate_report",
            python_callable=generate_report,
        )

        # Task 순서 정의
        task_fetch_news >> task_preprocess >> task_sentiment >> task_trend >> task_report

    return dag

globals()["news_sentiment_trend_dag"] = create_dag()
