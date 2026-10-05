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
                echo 'Running application tests...'

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
                        -t ${IMAGE_NAME}:green \
                        .
                '''
            }
        }

        stage('Docker Container Test') {
            steps {
                echo 'Testing Docker container health...'

                sh '''
                    docker rm -f ${APP_NAME}-test 2>/dev/null || true

                    docker run -d \
                        --name ${APP_NAME}-test \
                        -p 5050:5000 \
                        -e APP_VERSION=2.0.0 \
                        -e DEPLOYMENT_COLOR=GREEN \
                        -e ENVIRONMENT=Production \
                        ${IMAGE_NAME}:green

                    sleep 5

                    curl --fail \
                        http://localhost:5050/health

                    docker rm -f ${APP_NAME}-test
                '''
            }
        }

        stage('Load Green Image into Minikube') {
            steps {
                echo 'Loading Green Docker image into Minikube...'

                sh '''
                    docker save ${IMAGE_NAME}:green | \
                    docker exec -i minikube ctr -n k8s.io images import -
                '''
            }
        }

        stage('Deploy Green Environment') {
            steps {
                echo 'Deploying Green environment...'

                sh '''
                    kubectl apply -f k8s/green-deployment.yaml

                    kubectl rollout status \
                        deployment/cloudops-green \
                        --timeout=120s
                '''
            }
        }

        stage('Verify Green Environment') {
            steps {
                echo 'Verifying Green environment health...'

                sh '''
                    kubectl get deployment cloudops-green
                    kubectl get pods -l version=green

                    GREEN_POD=$(kubectl get pod \
                         -l version=green \
                         -o jsonpath='{.items[0].metadata.name}')

                    kubectl exec ${GREEN_POD} -- \
                       python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"
                '''
            }
        }

        stage('Switch Traffic to Green') {
            steps {
                echo 'Switching production traffic from Blue to Green...'

                sh '''
                    kubectl patch service cloudops-dashboard-service \
                        -p '{"spec":{"selector":{"app":"cloudops-dashboard","version":"green"}}}'
                '''
            }
        }

        stage('Verify Production Traffic') {
            steps {
                echo 'Verifying production traffic is serving Green...'

                sh '''
                    sleep 5

                    curl --fail \
                        http://$(minikube ip):30080/health

                    kubectl get endpoints cloudops-dashboard-service
                '''
            }
        }

    }

    post {

        success {
            echo '========================================'
            echo 'BLUE-GREEN DEPLOYMENT SUCCESSFUL'
            echo 'Production traffic is now on GREEN'
            echo '========================================'
        }

        failure {
            echo '========================================'
            echo 'BLUE-GREEN DEPLOYMENT FAILED'
            echo 'Production traffic was not switched'
            echo '========================================'
        }

        always {
            sh '''
                docker rm -f ${APP_NAME}-test 2>/dev/null || true
            '''
        }
    }
}
