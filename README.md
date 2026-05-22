# NYC Yellow Taxi Big Data Pipeline

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
$env:DELTA_GOLD_PATH = "data/delta/gold/fare_features"
$env:MLFLOW_TRACKING_URI = "http://localhost:5000"
streamlit run ml_pipeline/dashboard.py
```

## Team Workflow

Suggested feature branches:

- `feature/kafka-producer`
- `feature/spark-bronze-silver`
- `feature/mlflow-training`
- `feature/docker-docs`

Each member should make real, explainable commits in their own branch.
