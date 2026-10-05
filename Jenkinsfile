pipeline {

    agent any

    environment {
        APP_NAME = 'cloudops-dashboard'
        IMAGE_NAME = 'cloudops-dashboard'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out application source code...'
                checkout scm
            }
        }

        stage('Application Test') {
            steps {
                echo 'Installing dependencies and running application checks...'

                sh '''
                    python3 -m venv test-venv
                    . test-venv/bin/activate
                    pip install --quiet -r requirements.txt

                    python3 -m py_compile app.py

                    test -f templates/index.html
                    test -f Dockerfile

                    deactivate
                    rm -rf test-venv
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}"

                sh '''
                    docker build \
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${IMAGE_NAME}:latest \
                        .
                '''
            }
        }

        stage('Docker Container Test') {
            steps {
                echo 'Starting temporary container for health testing...'

                sh '''
                    docker rm -f ${APP_NAME}-test 2>/dev/null || true

                    docker run -d \
                        --name ${APP_NAME}-test \
                        -p 5050:5000 \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    sleep 5

                    curl --fail \
                        http://localhost:5050/health

                    docker rm -f ${APP_NAME}-test
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying application to Kubernetes...'

                sh '''
                   minikube image load ${IMAGE_NAME}:latest

                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    kubectl set image \
                        deployment/${APP_NAME} \
                        ${APP_NAME}=${IMAGE_NAME}:latest

                    kubectl rollout status \
                        deployment/${APP_NAME} \
                        --timeout=120s
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                echo 'Verifying Kubernetes deployment...'

                sh '''
                    kubectl get deployment ${APP_NAME}
                    kubectl get pods -l app=${APP_NAME}
                    kubectl get service ${APP_NAME}-service

                    kubectl rollout status \
                        deployment/${APP_NAME} \
                        --timeout=120s
                '''
            }
        }
    }

    post {

        success {
            echo '========================================'
            echo 'CI/CD PIPELINE COMPLETED SUCCESSFULLY'
            echo '========================================'
        }

        failure {
            echo '========================================'
            echo 'CI/CD PIPELINE FAILED'
            echo 'Check the Jenkins console output.'
            echo '========================================'
        }

        always {
            sh '''
                docker rm -f ${APP_NAME}-test 2>/dev/null || true
            '''
        }
    }
}
