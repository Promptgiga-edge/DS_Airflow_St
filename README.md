# DS_Airflow_St

This Airflow DAG (amazon_books_etl_v2) implements an ETL (Extract, Transform, Load) pipeline that scrapes data engineering books from Amazon and stores the information in a PostgreSQL database. The pipeline runs daily and includes robust error handling, rate limiting, and duplicate detection.

## 📋 Overview

This repository contains Apache Airflow DAGs (Directed Acyclic Graphs) and related configurations for managing data science workflows. The project aims to automate data ingestion, processing, analysis, and reporting tasks in a scalable and maintainable way.

## 🚀 Architecture
The DAG consists of three main tasks:

- create_books_table: Creates the PostgreSQL table if it doesn't exist
- fetch_book_data: Scrapes Amazon for book information
- insert_book_data: Inserts/updates book data in the database

## 🛠️ Prerequisites

Before running this project, ensure you have:

- Python 3.12.2
- Apache Airflow 3.0.2
- Docker (for containerized deployment)
- PostgreSQL 
- Required Python packages (see `requirements.txt`)

## 📦 Installation

### Local Setup

1. **Initialize Airflow database**
   ```bash
   airflow db init
   ```

2.. **Create admin user**
   ```bash
   airflow users create \
     --username admin \
     --firstname Admin \
     --lastname User \
     --role Admin \
     --email admin@example.com
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

## 🏃‍♂️ Usage

### Starting Airflow

1. **Start the web server**
   ```bash
   airflow webserver --port 8080
   ```

2. **Start the scheduler** (in a new terminal)
   ```bash
   airflow scheduler
   ```

3. **Access the Airflow UI**
   - Open your browser and go to `http://localhost:8080`
   - Login with your admin credentials

### Running DAGs

1. Navigate to the Airflow UI
2. Enable the DAGs you want to run
3. Trigger DAGs manually or let them run on schedule
4. Monitor task execution and logs

## 📁 Project Structure

```
DS_Airflow_St/
├── dags/                   # Airflow DAG files
│   ├── amazon_books_etl_v2.py
├── plugins/                # Custom Airflow plugins
├── config/                 # Configuration files
├── scripts/                # Utility scripts
├── tests/                  # Unit tests
├── docker-compose.yml      # Docker configuration
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker image definition
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

Set the following environment variables:

```bash
export AIRFLOW_HOME=/path/to/airflow
export AIRFLOW__CORE__DAGS_FOLDER=/path/to/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
```

### Airflow Configuration

Key configuration settings in `airflow.cfg`:

- **Executor**: LocalExecutor, CeleryExecutor, or KubernetesExecutor
- **Database**: PostgreSQL for production
- **Logging**: Configure log levels and storage

## 📊 DAGs Overview

### Data Ingestion DAG
- Fetches data from various sources
- Validates data quality
- Stores raw data in staging area

### Data Processing DAG
- Cleans and transforms raw data
- Applies business logic
- Generates processed datasets


## 📚 Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [DAG Writing Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/howto/writing-dags.html)
