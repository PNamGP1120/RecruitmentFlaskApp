pipeline {
    agent any

    environment {
        VENV_DIR = '.venv'
    }

    stages {
        stage('Clone') {
            steps {
                git branch: 'develop', url: 'https://github.com/PNamGP1120/RecruitmentFlaskApp.git'
            }
        }

        stage('Setup Virtualenv') {
            steps {
                sh 'python3 -m venv .venv'
                sh '.venv/bin/pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                sh '.venv/bin/python -m unittest discover'
            }
        }

        stage('Deploy (Dev only)') {
            steps {
                echo 'Deployment step here (e.g., run script, restart server)'
            }
        }
    }
}
