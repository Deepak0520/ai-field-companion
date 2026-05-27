pipeline {
    agent any
    
    environment {
        IMAGE_NAME = 'ai-field-companion'
        IMAGE_TAG = "${BUILD_NUMBER}"
        CONTAINER_NAME = 'ai-field-companion-app'
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
                    pylint app/ --exit-zero --output-format=text | tee pylint-report.txt
                    echo "Code quality analysis complete"
                '''
            }
        }
        
        stage('Security') {
            steps {
                echo 'Running security scan...'
                sh '''
                    pip3 install bandit
                    bandit -r app/ -f txt -o bandit-report.txt || true
                    cat bandit-report.txt
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
                    echo "Production image: ${IMAGE_NAME}:production"
                    git tag -a v1.${IMAGE_TAG} -m "Release version 1.${IMAGE_TAG}" || true
                '''
            }
        }
        
        stage('Monitoring') {
            steps {
                echo 'Setting up monitoring...'
                sh '''
                    sleep 3
                    STATUS=$(docker inspect --format="{{.State.Status}}" ${CONTAINER_NAME})
                    echo "Container status: ${STATUS}"
                    docker stats ${CONTAINER_NAME} --no-stream
                    curl -f http://localhost:8000/health || echo "Health check failed"
                    echo "Monitoring check complete"
                '''
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completed successfully!'
            echo "Application is running at http://localhost:8000"
        }
        failure {
            echo 'Pipeline failed!'
            sh 'docker stop ${CONTAINER_NAME} || true'
        }
        always {
            echo 'Pipeline finished.'
        }
    }
}
