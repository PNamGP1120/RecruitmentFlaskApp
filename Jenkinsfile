pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.13.3'
        VENV_NAME = 'venv'
        FLASK_ENV = 'testing'
        PYTHONPATH = "${WORKSPACE}"
        PATH = "/var/lib/jenkins/.local/bin:${env.PATH}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    # Cài đặt pip và virtualenv ở user level
                    python3 -m pip install --user --upgrade pip
                    python3 -m pip install --user virtualenv

                    # Tạo và kích hoạt virtual environment
                    python3 -m virtualenv ${VENV_NAME}
                    . ${VENV_NAME}/bin/activate

                    # Cài đặt các dependencies
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    . ${VENV_NAME}/bin/activate
                    python -m unittest tests/test_job_posting.py -v
                '''
            }
        }

        stage('Code Quality') {
            steps {
                sh '''
                    . ${VENV_NAME}/bin/activate
                    mkdir -p reports

                    # Chạy flake8
                    python -m pip install flake8
                    flake8 app/ tests/ --output-file=reports/flake8.txt || true

                    # Chạy pylint
                    python -m pip install pylint
                    pylint app/ tests/ --output-format=text --output=reports/pylint.txt || true
                '''
            }
        }

        stage('Database Tests') {
            steps {
                sh '''
                    . ${VENV_NAME}/bin/activate
                    python -m unittest tests/test_job_posting.py -v
                '''
            }
        }

        stage('Build Package') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    . ${VENV_NAME}/bin/activate
                    python setup.py bdist_wheel
                '''
                archiveArtifacts artifacts: 'dist/*.whl', fingerprint: true
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline execution failed!'
        }
    }
}