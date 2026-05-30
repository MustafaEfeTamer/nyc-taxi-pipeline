pipeline {
    agent any

    options {
        // Workspace'i temizle ama checkout'u otomatik yap (skipDefaultCheckout kaldırıldı)
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    triggers {
        // ⚠️  Bu trigger'ın çalışması için Jenkins job ayarlarında:
        //     Build Triggers → "GitHub hook trigger for GITScm polling" kutusunu işaretleyin!
        githubPush()
    }

    environment {
        COMPOSE_PROJECT_NAME = "nyc-taxi-pipeline-ci"
        PYTHON_VERSION       = "3.11"
        // Jenkins container içinden Docker iç ağı üzerinden SonarQube'a erişilir
        SONAR_HOST_URL       = "http://nyc-taxi-sonarqube:9000"
        REPORTS_DIR          = "reports"
    }

    stages {

        // ──────────────────────────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm
                sh 'mkdir -p ${REPORTS_DIR}'
            }
        }

        // ──────────────────────────────────────────────────────────────────────
        stage('Lint') {
            steps {
                echo '🔍 Running Python Linter (flake8)...'
                sh '''
                    pip install flake8 --break-system-packages -q
                    flake8 ml_pipeline/ spark_jobs/ producer/ tests/ \
                        --count \
                        --select=E9,F63,F7,F82 \
                        --show-source \
                        --statistics \
                        --output-file=${REPORTS_DIR}/flake8-report.txt || true
                    cat ${REPORTS_DIR}/flake8-report.txt
                '''
            }
        }

        // ──────────────────────────────────────────────────────────────────────
        stage('Test') {
            steps {
                echo '🧪 Running Unit Tests with Coverage...'
                sh '''
                    pip install -r tests/requirements-test.txt --break-system-packages -q
                    pytest tests/ \
                        --junitxml=${REPORTS_DIR}/test-results.xml \
                        --cov=ml_pipeline \
                        --cov=spark_jobs \
                        --cov=producer \
                        --cov-report=xml:${REPORTS_DIR}/coverage.xml \
                        --cov-report=term-missing \
                        -v
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: "${REPORTS_DIR}/test-results.xml"
                }
            }
        }

        // ──────────────────────────────────────────────────────────────────────
        stage('SonarQube Analysis') {
            steps {
                echo '📊 Running SonarQube Code Quality Analysis...'
                withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        # SonarQube'un hazır olmasını bekle (max 3 dakika)
                        echo "⏳ Waiting for SonarQube to be ready..."
                        RETRIES=18
                        COUNT=0
                        until wget -qO- "${SONAR_HOST_URL}/api/system/status" 2>/dev/null | grep -q '"status":"UP"'; do
                            COUNT=$((COUNT + 1))
                            if [ "$COUNT" -ge "$RETRIES" ]; then
                                echo "❌ SonarQube did not become ready in time!"
                                exit 1
                            fi
                            echo "   SonarQube not ready yet (attempt ${COUNT}/${RETRIES}), waiting 10s..."
                            sleep 10
                        done
                        echo "✅ SonarQube is ready!"

                        # sonar-scanner imaja gömülü, doğrudan çalıştır
                        sonar-scanner \
                            -Dsonar.host.url="${SONAR_HOST_URL}" \
                            -Dsonar.token="${SONAR_TOKEN}" \
                            -Dsonar.working.directory="${WORKSPACE}/.scannerwork"
                    '''
                }
            }
        }

        // ──────────────────────────────────────────────────────────────────────
        stage('Build') {
            steps {
                echo '🐳 Building Docker Images...'
                sh '''
                    # Sadece uygulama imajlarını build et (jenkins/sonarqube değil)
                    docker compose -f docker-compose.yml build spark producer
                '''
            }
        }

        // ──────────────────────────────────────────────────────────────────────
        stage('Deploy') {
            // Sadece main branch'te deploy yap
            when {
                branch 'main'
            }
            steps {
                echo '🚀 Deploying to Local Docker (main branch only)...'
                sh '''
                    # Altyapı servislerini başlat (jenkins ve sonarqube hariç)
                    docker compose -f docker-compose.yml up -d zookeeper kafka mlflow spark
                '''
            }
        }
    }

    post {
        always {
            echo '🏁 Pipeline finished.'
            // Workspace'i temizle (bir sonraki build için)
            cleanWs(
                cleanWhenSuccess: true,
                cleanWhenFailure: false,
                cleanWhenAborted: true
            )
        }
        success {
            echo '✅ All stages completed successfully!'
            echo "🔗 SonarQube Dashboard: ${SONAR_HOST_URL}/dashboard?id=nyc-taxi-pipeline"
        }
        failure {
            echo '❌ Pipeline failed! Check the stage logs above.'
        }
    }
}
