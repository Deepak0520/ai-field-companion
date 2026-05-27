pipeline {
    agent any

    environment {
        IMAGE_NAME = 'ai-field-companion'
        IMAGE_TAG = "${BUILD_NUMBER}"
        CONTAINER_NAME = 'ai-field-companion-app'
        PROMETHEUS_CONTAINER = 'prometheus-monitor'
    }

    stages {

        stage('Build') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
                sh 'docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest'
                echo "Built image: ${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
                    pip3 install -r requirements.txt
                    python3 -m pytest tests/ -v --cov=app --cov-report=term-missing
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo 'Running code quality analysis...'
                sh '''
                    pip3 install pylint
                    python3 -m pylint app/ --exit-zero --output-format=text | tee pylint-report.txt
                    echo "Code quality analysis complete"
                '''
            }
        }

        stage('Security') {
            steps {
                echo 'Running security scan...'
                sh '''
                    pip3 install pbr bandit
                    python3 -m bandit -r app/ -f txt -o bandit-report.txt || true
                    cat bandit-report.txt || true
                    echo "Security scan complete"
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying to test environment...'
                sh '''
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p 8000:8000 \
                        ${IMAGE_NAME}:${IMAGE_TAG}
                    echo "Waiting for app to start..."
                    sleep 5
                    docker ps | grep ${CONTAINER_NAME}
                    echo "App deployed successfully"
                '''
            }
        }

        stage('Release') {
            steps {
                echo 'Releasing to production...'
                sh '''
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:production
                    echo "Released version ${IMAGE_TAG} to production"
                    git tag -a v1.${IMAGE_TAG} -m "Release version 1.${IMAGE_TAG}" || true
                '''
            }
        }

        stage('Monitoring') {
            steps {
                echo 'Setting up Prometheus monitoring...'
                sh '''
                    # Stop any existing Prometheus container
                    docker stop ${PROMETHEUS_CONTAINER} || true
                    docker rm ${PROMETHEUS_CONTAINER} || true

                    # Start Prometheus with our scrape config
                    docker run -d \
                        --name ${PROMETHEUS_CONTAINER} \
                        -p 9090:9090 \
                        -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
                        prom/prometheus:latest

                    echo "Waiting for Prometheus to initialise..."
                    sleep 10

                    # Verify the app container is still running
                    STATUS=$(docker inspect --format="{{.State.Status}}" ${CONTAINER_NAME})
                    echo "App container status: ${STATUS}"

                    # Confirm the app metrics endpoint is live
                    echo "--- App /metrics sample ---"
                    curl -sf http://localhost:8000/metrics | head -20
                    echo ""

                    # Confirm Prometheus itself is healthy
                    curl -sf http://localhost:9090/-/healthy && echo "Prometheus: healthy"

                    # Allow Prometheus time to scrape, then query its API
                    sleep 8
                    echo "--- Prometheus scrape status ---"
                    curl -s "http://localhost:9090/api/v1/query?query=up{job=\\"ai-field-companion\\"}" \
                        | python3 -c "
import sys, json
d = json.load(sys.stdin)
results = d.get('data', {}).get('result', [])
if results:
    val = results[0]['value'][1]
    print('Prometheus target UP =', val, '(1=healthy, 0=down)')
else:
    print('Prometheus: target not yet scraped — check after build')
"
                    echo "Monitoring complete — Prometheus dashboard: http://localhost:9090"
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
            echo "Application running at http://localhost:8000"
            echo "Prometheus dashboard at http://localhost:9090"
        }
        failure {
            echo 'Pipeline failed!'
            sh 'docker stop ${CONTAINER_NAME} || true'
            sh 'docker stop ${PROMETHEUS_CONTAINER} || true'
        }
        always {
            echo 'Pipeline finished.'
        }
    }
}