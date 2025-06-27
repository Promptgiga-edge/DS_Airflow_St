# DS_Airflow_St

A Data Science pipeline orchestration project using Apache Airflow for automated data processing, analysis, and workflow management.

## 📋 Overview

This repository contains Apache Airflow DAGs (Directed Acyclic Graphs) and related configurations for managing data science workflows. The project aims to automate data ingestion, processing, analysis, and reporting tasks in a scalable and maintainable way.

## 🚀 Features

- **Automated Data Pipelines**: Orchestrated data workflows using Apache Airflow
- **Data Processing**: ETL/ELT operations for data transformation
- **Scheduling**: Time-based and dependency-based task scheduling
- **Monitoring**: Built-in monitoring and alerting capabilities
- **Scalability**: Distributed task execution support
- **Error Handling**: Robust error handling and retry mechanisms

## 🛠️ Prerequisites

Before running this project, ensure you have:

- Python 3.12.2
- Apache Airflow 3.0.2
- Docker (for containerized deployment)
- Required Python packages (see `requirements.txt`)

## 📦 Installation

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Promptgiga-edge/DS_Airflow_St.git
   cd DS_Airflow_St
   ```

2. **Create virtual environment**
   ```bash
   python -m venv airflow_env
   source airflow_env/bin/activate  # On Windows: airflow_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Airflow database**
   ```bash
   airflow db init
   ```

5. **Create admin user**
   ```bash
   airflow users create \
     --username admin \
     --firstname Admin \
     --lastname User \
     --role Admin \
     --email admin@example.com
   ```

### Docker Setup (Alternative)

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
│   ├── data_ingestion.py
│   ├── data_processing.py
│   └── ml_pipeline.py
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

### ML Pipeline DAG
- Trains machine learning models
- Evaluates model performance
- Deploys models to production

## 🧪 Testing

Run unit tests:
```bash
python -m pytest tests/
```

Run DAG validation:
```bash
python dags/your_dag.py
```

## 📈 Monitoring

- **Airflow UI**: Monitor DAG runs, task status, and logs
- **Alerts**: Configure email/Slack notifications for failures
- **Metrics**: Track pipeline performance and SLA compliance

## 📚 Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [DAG Writing Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/howto/writing-dags.html)
