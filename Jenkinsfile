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
                    python3 -m pip install --upgrade pip
                    python3 -m pip install virtualenv
                    python3 -m virtualenv ${VENV_NAME}
                    . ${VENV_NAME}/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    . ${VENV_NAME}/bin/activate
                    # Chạy test_job_posting.py
                    python -m unittest tests/test_job_posting.py -v

                    # Tạo thư mục cho test reports
                    mkdir -p test-reports

                    # Chạy với coverage để có báo cáo độ bao phủ
                    coverage run -m unittest discover tests/
                    coverage xml -o test-reports/coverage.xml
                    coverage html -d test-reports/coverage_html
                '''
            }
            post {
                always {
                    // Lưu báo cáo coverage
                    cobertura coberturaReportFile: 'test-reports/coverage.xml'

                    // Lưu trữ báo cáo HTML
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: false,
                        keepAll: true,
                        reportDir: 'test-reports/coverage_html',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        stage('Code Quality') {
            steps {
                sh '''
                    . ${VENV_NAME}/bin/activate

                    # Kiểm tra code style với flake8
                    flake8 app/ tests/ --output-file=test-reports/flake8.txt

                    # Phân tích code với pylint
                    pylint app/ tests/ --output-format=parseable --output=test-reports/pylint.txt
                '''
            }
            post {
                always {
                    recordIssues(
                        tools: [
                            flake8(pattern: 'test-reports/flake8.txt'),
                            pyLint(pattern: 'test-reports/pylint.txt')
                        ]
                    )
                }
            }
        }

        stage('Database Tests') {
            steps {
                sh '''
                    . ${VENV_NAME}/bin/activate

                    # Chạy migrations nếu cần
                    flask db upgrade

                    # Chạy database tests
                    python -m unittest tests/test_job_posting.py -v
                '''
            }
        }

        stage('Build Package') {
            when {
                branch 'main'  // Chỉ build package trên nhánh main
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
            // Cleanup workspace
            cleanWs()
        }
        success {
            // Gửi thông báo khi build thành công
            emailext (
                subject: "Pipeline Succeeded: ${currentBuild.fullDisplayName}",
                body: "Your pipeline has completed successfully.",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
        failure {
            // Gửi thông báo khi build thất bại
            emailext (
                subject: "Pipeline Failed: ${currentBuild.fullDisplayName}",
                body: "Your pipeline has failed. Please check the Jenkins console output.",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
    }
}