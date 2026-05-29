pipeline {
    agent any

    options {
        skipDefaultCheckout()
    }

    triggers {
        // GitHub'dan webhook sinyali geldiğinde her zaman build başlat
        // Yerel workspace değişiklik kontrolü yapmadan direkt tetiklenir
        githubPush()
    }


    environment {
        COMPOSE_PROJECT_NAME = "nyc-taxi-pipeline-ci"
        PYTHON_VERSION = "3.11"
        // SonarQube sunucusu: Jenkins konteyneri içinden Docker iç ağı üzerinden erişir
        SONAR_HOST_URL = "http://nyc-taxi-sonarqube:9000"
    }


    stages {
        stage('Lint') {
            steps {
                echo 'Running Python Linter...'
                sh '''
                    # Install flake8 and run it
                    pip install flake8 --break-system-packages
                    flake8 ml_pipeline/ spark_jobs/ producer/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube Code Quality Analysis...'
                withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        # sonar-scanner sadece yoksa indir, varsa atla
                        if [ ! -f /usr/local/bin/sonar-scanner ]; then
                            apt-get install -y unzip 2>/dev/null || true
                            curl -sSLo /tmp/sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-6.2.1.4610-linux-x64.zip
                            unzip -qo /tmp/sonar-scanner.zip -d /opt/
                            ln -sf /opt/sonar-scanner-6.2.1.4610-linux-x64/bin/sonar-scanner /usr/local/bin/sonar-scanner
                        fi

                        # Analizi calistir
                        sonar-scanner \
                            -Dsonar.host.url=$SONAR_HOST_URL \
                            -Dsonar.token=$SONAR_TOKEN
                    '''
                }
            }
        }

        stage('Build') {
            steps {
                echo 'Building Docker Images...'
                sh '''
                    # Sadece spark ve producer imajlarini insa et
                    # jenkins imaji dahil edilmiyor: zaten calisiyor ve gereksiz yere rebuild yapar
                    docker compose -f docker-compose.yml build spark producer
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running Unit Tests...'
                sh '''
                    # Install test dependencies and run pytest
                    pip install -r tests/requirements-test.txt --break-system-packages
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
