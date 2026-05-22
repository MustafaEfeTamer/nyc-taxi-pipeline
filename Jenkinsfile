pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = "nyc-taxi-pipeline-ci"
        PYTHON_VERSION = "3.11"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                echo 'Running Python Linter...'
                sh '''
                    # Install flake8 and run it
                    pip install flake8
                    flake8 ml_pipeline/ spark_jobs/ producer/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'Building Docker Images...'
                sh '''
                    # Build all necessary images with docker compose
                    docker compose -f docker-compose.yml build
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running Unit Tests...'
                sh '''
                    # Install test dependencies and run pytest
                    pip install -r tests/requirements-test.txt
                    pytest tests/ --junitxml=reports/test-results.xml
                '''
            }
            post {
                always {
                    junit 'reports/test-results.xml'
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying to Staging (Local Docker)...'
                sh '''
                    # Start the infrastructure
                    docker compose -f docker-compose.yml up -d
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Cleaning up workspace if necessary.'
        }
        success {
            echo 'All stages completed successfully!'
        }
        failure {
            echo 'Pipeline failed! Please check the logs.'
        }
    }
}
