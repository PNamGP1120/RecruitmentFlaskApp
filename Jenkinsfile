pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.13.3'
        VENV_NAME = 'venv'
        FLASK_ENV = 'testing'
        PYTHONPATH = "${WORKSPACE}"
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
                    # Create virtual environment
                    python3 -m venv ${VENV_NAME}

                    # Activate virtual environment and install packages
                    . ${VENV_NAME}/bin/activate
                    ${VENV_NAME}/bin/python -m pip install --upgrade pip
                    ${VENV_NAME}/bin/pip install -r requirements.txt
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
                    flake8 app/ tests/ --output-file=reports/flake8.txt || true
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