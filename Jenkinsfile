pipeline {
    agent any

    stages {
        stage('Clone project') {
            steps {
                git branch: 'main', url: 'https://github.com/PNamGP1120/RecruitmentFlaskApp.git'
            }
        }

        stage('Setup Python & Virtualenv') {
            steps {
                sh '''#!/bin/bash
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''#!/bin/bash
                    source venv/bin/activate
                    pytest
                '''
            }
        }

        stage('Deploy (Optional)') {
            when {
                branch 'main'
            }
            steps {
                echo "Triển khai nếu cần."
            }
        }
    }

    post {
        failure {
            echo 'Có lỗi trong Pipeline!'
        }
        success {
            echo 'Build & test thành công!'
        }
    }
}
