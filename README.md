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

## CI/CD Pipeline (Jenkins)

This repository is equipped with a declarative Jenkins CI/CD pipeline. The pipeline automates the code validation, image building, testing, and deployment processes.

### Jenkins Pipeline Stages

1. **Checkout**: Clones the latest code from the repository.
2. **Lint**: Uses `flake8` to perform syntax and style checks on Python files to ensure code quality.
3. **Build**: Builds the Docker images (`spark` and `producer`) defined in `docker-compose.yml`.
4. **Test**: Runs Python unit tests inside a temporary environment using `pytest`. Test reports are generated as JUnit XML.
5. **Deploy**: Simulates a staging deployment by bringing up the infrastructure containers via `docker compose up -d`.

### Prerequisites for Jenkins
- Jenkins node must have `docker` and `docker compose` installed.
- Python 3.x and `pip` must be available on the Jenkins agent.
- Ensure the Jenkins user has permissions to run docker commands (e.g., added to the `docker` group).

### Running Jenkins Locally

We have included a customized Jenkins container in the `docker-compose.yml` that supports Docker-out-of-Docker (DooD), allowing it to build and run containers on your host machine.

To start Jenkins along with the rest of the infrastructure:
```powershell
docker compose up -d jenkins
```

**Accessing Jenkins::**
1. Navigate to `http://localhost:8081` in your web browser.
2. To get the initial admin password, check the Jenkins container logs:
```powershell
docker compose logs jenkins
```
3. Look for the block of text containing the password (e.g., `Please use the following password to proceed to installation:`).
4. Paste the password, install suggested plugins, and set up your admin user.
5. Create a new Pipeline job, point it to your repository (or use the "Pipeline script from SCM" option if you have committed the changes), and Jenkins will automatically read the `Jenkinsfile` and execute the CI/CD stages.
