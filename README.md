# NYC Yellow Taxi Big Data Pipeline

[![CI/CD](https://github.com/MustafaEfeTamer/nyc-taxi-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/MustafaEfeTamer/nyc-taxi-pipeline/actions/workflows/ci.yml)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=MustafaEfeTamer_nyc-taxi-pipeline&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=MustafaEfeTamer_nyc-taxi-pipeline)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=MustafaEfeTamer_nyc-taxi-pipeline&metric=coverage)](https://sonarcloud.io/summary/new_code?id=MustafaEfeTamer_nyc-taxi-pipeline)

End-to-end big data project for NYC Yellow Taxi trip records. The pipeline replays historical TLC Parquet data through Kafka as a pseudo-stream, processes it with Spark, stores curated layers in Delta Lake, and tracks fare prediction experiments with MLflow.

## Project Scope

- Dataset: NYC TLC Yellow Taxi Trip Records
- Initial data target: `yellow_tripdata_2023-01.parquet`
- Lookup data: `taxi_zone_lookup.csv`
- Main prediction target: `fare_amount`
- Optional second target: `trip_duration_minutes`

## Architecture

```text
NYC Yellow Taxi Parquet
        |
        v
Kafka Producer
        |
        v
Kafka topic: yellow_taxi_trips
        |
        v
Spark Structured Streaming
        |
        v
Delta Bronze
        |
        v
Spark batch cleaning + zone lookup join
        |
        v
Delta Silver
        |
        v
Spark batch feature engineering
        |
        v
Delta Gold
        |
        v
ML training + MLflow tracking
```

## Repository Layout

```text
producer/       Kafka producer that replays Parquet rows as JSON messages
spark_jobs/     Spark jobs for Bronze, Silver, and Gold Delta layers
ml_pipeline/    Fare prediction training and MLflow logging
scripts/        Helper scripts for local pipeline execution
docs/           Architecture and presentation notes
data/           Local-only raw, lookup, and Delta data folders
```

## Data Files

Large data files are not included in this GitHub repository. To run the project, please download the required data from the Google Drive link below:

- **Google Drive Data Folder**: [https://drive.google.com/drive/folders/10pVzS5B5Qz2yVWvjL8gz1azIYZ4DQ-8l]

Once downloaded, place the files into their respective directories as follows:

- Place `yellow_tripdata_2023-01.parquet` -> into `data/raw/`
- Place `taxi_zone_lookup.csv` -> into `data/lookup/`

These large files are tracked by `.gitignore` to prevent accidental commits to GitHub.

## Quick Start (End-to-End Execution)

To run the entire pipeline from scratch, follow these sequential steps:

### 1. Docker & Environment Setup

Start by cleaning up any old containers, installing local dependencies, and starting the new infrastructure (using `--build` to ensure Spark requirements are installed):

```powershell
docker compose down 
pip install -r requirements.txt
docker compose up -d --build
docker compose --profile pipeline up -d producer
```

### 2. Data Processing (Bronze, Silver, Gold Layers)

Run the Spark jobs to process the data through the medallion architecture. 

```powershell
# Ingest data from Kafka to Bronze layer
docker compose exec spark python spark_jobs/stream_to_bronze.py

# Clean and enrich data from Bronze to Silver layer
docker compose exec spark python spark_jobs/bronze_to_silver.py

# Create ML features from Silver to Gold layer
docker compose exec spark python spark_jobs/silver_to_gold.py
```

### 3. Model Training

Train the machine learning model using the features in the Gold layer. Metrics and models are logged to MLflow.

```powershell
docker compose exec spark python ml_pipeline/model_training.py
```
*(You can view MLflow tracking at `http://localhost:5000`)*

### 4. Dashboard

Finally, launch the local Streamlit dashboard to visualize the predictions and data:

```powershell
streamlit run ml_pipeline/dashboard.py
```

## CI/CD Pipeline (GitHub Actions)

Bu repo, GitHub Actions ile tam otomatik CI/CD pipeline'ına sahiptir.
Her `push` ve `pull_request` olayında pipeline otomatik tetiklenir.

### Pipeline Aşamaları

| # | Job | Açıklama |
|---|-----|----------|
| 1 | 🔍 **Lint** | `flake8` ile Python sözdizimi ve kritik hata kontrolü |
| 2 | 🧪 **Test** | `pytest` + coverage raporu (JUnit XML artifact) |
| 3 | 📊 **SonarCloud** | Kod kalitesi ve güvenlik analizi (test'ten sonra çalışır) |
| 4 | 🐳 **Build** | `spark` ve `producer` Docker image'larını build eder |
| 5 | 🚀 **Deploy** | Sadece `main` branch'te çalışır |

### Gerekli GitHub Secret'lar

Repo ayarlarında (`Settings → Secrets → Actions`) şu secret'ı ekleyin:

| Secret | Açıklama |
|--------|----------|
| `SONAR_TOKEN` | [sonarcloud.io](https://sonarcloud.io) → My Account → Security → Generate Token |

### SonarCloud Kurulumu

1. [sonarcloud.io](https://sonarcloud.io) adresine GitHub hesabınla giriş yap
2. `+` → **Analyze new project** → repoyu seç → import et
3. Oluşturulan token'ı GitHub Secret olarak ekle (`SONAR_TOKEN`)
4. `sonar-project.properties` içindeki `sonar.organization` değerini kendi SonarCloud org adınla güncelle

### Workflow Dosyası

Pipeline tanımı: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
