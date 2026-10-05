pipeline {

    agent any

    environment {
        APP_NAME = 'cloudops-dashboard'
        IMAGE_NAME = 'cloudops-dashboard'
        IMAGE_TAG = "${BUILD_NUMBER}"
        SECURITY_VENV = '/var/lib/jenkins/security-venv'
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
                    test -f SECURITY.md

                    deactivate
                    rm -rf test-venv
                '''
            }
        }


        stage('Dependency Security Scan') {
            steps {
                echo 'Scanning Python dependencies for known vulnerabilities...'

                sh '''
                    ${SECURITY_VENV}/bin/pip-audit \
                        -r requirements.txt
                '''
            }
        }


        stage('Security Policy Validation') {
            steps {
                echo 'Validating DevSecOps security policy...'

                sh '''
                    test -f SECURITY.md

                    grep -q "Source Code Security" SECURITY.md
                    grep -q "Dependency Security" SECURITY.md
                    grep -q "Container Security" SECURITY.md
                    grep -q "Application Security" SECURITY.md
                    grep -q "Kubernetes Security" SECURITY.md
                    grep -q "Deployment Security" SECURITY.md

                    echo "Security policy validation passed."
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
                    kubectl apply \
                        -f k8s/green-deployment.yaml

                    kubectl rollout status \
                        deployment/cloudops-green \
                        --timeout=120s
                '''
            }
        }


        stage('Verify Green Environment') {
            steps {
                echo 'Verifying Green environment health and security...'

                sh '''
                    kubectl get deployment cloudops-green

                    kubectl get pods \
                        -l version=green

                    GREEN_POD=$(kubectl get pod \
                        -l version=green \
                        -o jsonpath='{.items[0].metadata.name}')

                    echo "Green application health:"

                    kubectl exec ${GREEN_POD} -- \
                        python -c "import urllib.request; r=urllib.request.urlopen('http://localhost:5000/health'); print(r.read().decode())"

                    echo "Green environment verified successfully."
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

                    echo "Service:"
                    kubectl get service cloudops-dashboard-service

                    echo "Production Endpoints:"
                    kubectl get endpoints cloudops-dashboard-service

                    GREEN_POD=$(kubectl get pod \
                        -l version=green \
                        -o jsonpath='{.items[0].metadata.name}')

                    echo "Green application health:"

                    kubectl exec ${GREEN_POD} -- \
                        python -c "import urllib.request; r=urllib.request.urlopen('http://localhost:5000/health'); print(r.read().decode())"

                    echo "Production traffic verification passed."
                '''
            }
        }

    }


    post {

        success {
            echo '''
========================================
DEVSECOPS PIPELINE SUCCESSFUL
========================================
Security validation passed.
Dependency scan passed.
Application tests passed.
Container test passed.
Green deployment passed.
Production traffic switched successfully.
========================================
'''
        }

        failure {
            echo '''
========================================
DEVSECOPS PIPELINE FAILED
========================================
A security or deployment validation failed.
Production deployment must be reviewed.
========================================
'''
        }

        always {
            sh '''
                docker rm -f ${APP_NAME}-test 2>/dev/null || true
            '''
        }
    }
}
