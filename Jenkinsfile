pipeline {
    agent any

    environment {
        DOCKERHUB_REPO = 'YOUR_DOCKERHUB_USERNAME/simple-api'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Test') {
            steps {
                dir('app') {
                    sh 'python3 -m venv .venv'
                    sh '.venv/bin/pip install -r requirements.txt'
                    sh '.venv/bin/pytest -v'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${DOCKERHUB_REPO}:${IMAGE_TAG} app'
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_TOKEN'
                )]) {
                    sh 'echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USER" --password-stdin'
                    sh 'docker push ${DOCKERHUB_REPO}:${IMAGE_TAG}'
                    sh 'docker tag ${DOCKERHUB_REPO}:${IMAGE_TAG} ${DOCKERHUB_REPO}:latest'
                    sh 'docker push ${DOCKERHUB_REPO}:latest'
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
    }
}
