pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    stages {
        stage('Clone project') {
            steps {
                git branch: 'main', url: 'https://github.com/PNamGP1120/RecruitmentFlaskApp.git'
            }
        }

        stage('Setup Python & Virtualenv') {
            steps {
                sh '''
                    python3 -m venv $VENV_DIR
                    source $VENV_DIR/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    source $VENV_DIR/bin/activate
                    pytest tests/
                '''
            }
        }

        stage('Deploy (Optional)') {
            when {
                branch 'main'  // chỉ deploy khi push lên nhánh main
            }
            steps {
                echo 'Đang deploy...'
                // ví dụ: copy file lên server, restart service,...
            }
        }
    }

    post {
        success {
            echo '🎉 Pipeline chạy thành công!'
        }
        failure {
            echo '❌ Có lỗi trong Pipeline!'
        }
    }
}
