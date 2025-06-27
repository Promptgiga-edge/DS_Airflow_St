from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.hooks.base import BaseHook
import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import time
import random
import psycopg2
from psycopg2.extras import execute_values

# Updated headers with more recent user agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def get_postgres_connection():
    """Get PostgreSQL connection using Airflow connection."""
    try:
        # Try to get connection from Airflow
        conn = BaseHook.get_connection('books_connection')
        return psycopg2.connect(
            host=conn.host,
            database=conn.schema,
            user=conn.login,
            password=conn.password,
            port=conn.port or 5432
        )
    except Exception as e:
        logging.error(f"Failed to get connection from Airflow: {e}")
        # Fallback to environment variables or default values
        return psycopg2.connect(
            host="localhost",
            database="airflow",
            user="airflow",
            password="airflow",
            port=5432
        )

def create_books_table(**context):
    """Create the books table if it doesn't exist."""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL UNIQUE,
            authors TEXT,
            price TEXT,
            rating TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
        CREATE INDEX IF NOT EXISTS idx_books_created_at ON books(created_at);
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        logging.info("Books table created/verified successfully")
        
    except Exception as e:
        logging.error(f"Error creating table: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_amazon_data_books(num_books: int, **context) -> None:
    """
    Scrape Amazon for data engineering books with improved error handling and rate limiting.
    """
    ti = context['ti']
    base_url = "https://www.amazon.com/s"
    params = {
        'k': 'data engineering books',
        'ref': 'sr_pg_'
    }
    
    books = []
    seen_titles = set()
    page = 1
    max_pages = 10  # Prevent infinite loops
    
    logging.info(f"Starting to fetch {num_books} books from Amazon")
    
    while len(books) < num_books and page <= max_pages:
        try:
            params['page'] = page
            
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(base_url, headers=HEADERS, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Updated selectors - Amazon frequently changes these
            book_containers = soup.find_all("div", {"data-component-type": "s-search-result"})
            
            if not book_containers:
                logging.warning(f"No book containers found on page {page}")
                break
            
            books_found_on_page = 0
            
            for container in book_containers:
                try:
                    # More robust selectors
                    title_elem = container.find("h2", class_="a-size-mini") or container.find("span", class_="a-text-normal")
                    author_elem = container.find("a", class_="a-size-base") or container.find("span", class_="a-size-base")
                    price_elem = container.find("span", class_="a-price-whole") or container.find("span", class_="a-offscreen")
                    rating_elem = container.find("span", class_="a-icon-alt")
                    
                    if title_elem:
                        book_title = title_elem.get_text(strip=True)
                        
                        # Skip if we've seen this title or if it's too short
                        if book_title in seen_titles or len(book_title) < 3:
                            continue
                            
                        seen_titles.add(book_title)
                        
                        book_data = {
                            "title": book_title,
                            "author": author_elem.get_text(strip=True) if author_elem else "Unknown",
                            "price": price_elem.get_text(strip=True) if price_elem else "N/A", 
                            "rating": rating_elem.get_text(strip=True) if rating_elem else "No rating",
                        }
                        
                        books.append(book_data)
                        books_found_on_page += 1
                        
                        if len(books) >= num_books:
                            break
                            
                except Exception as e:
                    logging.warning(f"Error parsing book container: {e}")
                    continue
            
            logging.info(f"Page {page}: Found {books_found_on_page} books, total: {len(books)}")
            
            if books_found_on_page == 0:
                logging.info("No more books found, stopping")
                break
                
            page += 1
            
        except requests.RequestException as e:
            logging.error(f"Request failed on page {page}: {e}")
            break
        except Exception as e:
            logging.error(f"Unexpected error on page {page}: {e}")
            break
    
    if not books:
        raise ValueError("No books were successfully scraped")
    
    # Convert to DataFrame and clean
    df = pd.DataFrame(books)
    df.drop_duplicates(subset="title", inplace=True)
    
    logging.info(f"Successfully scraped {len(df)} unique books")
    
    # Push to XCom
    ti.xcom_push(key='book_data', value=df.to_dict('records'))


def insert_book_data_into_postgres(**context) -> None:
    """
    Insert scraped book data into PostgreSQL with better error handling.
    """
    ti = context['ti']
    book_data = ti.xcom_pull(key='book_data', task_ids='fetch_book_data')
    
    if not book_data:
        raise ValueError("No book data found in XCom")
    
    logging.info(f"Inserting {len(book_data)} books into PostgreSQL")
    
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Use batch insert for better performance
        insert_query = """
        INSERT INTO books (title, authors, price, rating, created_at)
        VALUES %s
        ON CONFLICT (title) DO UPDATE SET
            authors = EXCLUDED.authors,
            price = EXCLUDED.price,
            rating = EXCLUDED.rating,
            updated_at = CURRENT_TIMESTAMP
        """
        
        current_time = datetime.now()
        values = [
            (book['title'], book['author'], book['price'], book['rating'], current_time)
            for book in book_data
        ]
        
        execute_values(cursor, insert_query, values)
        conn.commit()
        logging.info(f"Successfully inserted/updated {len(values)} books")
        
    except Exception as e:
        logging.error(f"Database insertion failed: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# Updated default args with current date
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 23),  # Today's date
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
    'catchup': False,  # Don't run for past dates
}

# DAG definition
dag = DAG(
    'amazon_books_etl_v2',
    default_args=default_args,
    description='ETL pipeline to fetch Amazon book data and store in PostgreSQL',
    schedule_interval='@daily',  # More readable than timedelta
    max_active_runs=1,  # Prevent overlapping runs
    tags=['etl', 'books', 'amazon', 'postgres'],
)

# Task definitions
create_table_task = PythonOperator(
    task_id='create_books_table',
    python_callable=create_books_table,
    dag=dag,
)

fetch_books_task = PythonOperator(
    task_id='fetch_book_data',
    python_callable=get_amazon_data_books,
    op_kwargs={'num_books': 50},
    dag=dag,
)

insert_books_task = PythonOperator(
    task_id='insert_book_data',
    python_callable=insert_book_data_into_postgres,
    dag=dag,
)

# Task dependencies
create_table_task >> fetch_books_task >> insert_books_task