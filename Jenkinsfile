pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        GIT_SSH_CREDENTIALS_ID = 'OPS'
        WORKSPACE_DIR = "/tmp/jenkins-workspace"
    }
    
    stages {
        stage('Clone') {
            steps {
                git credentialsId: "${GIT_SSH_CREDENTIALS_ID}", url: 'git@github.com:quaziadib/bangla-translator.git', branch: 'main'
            }
        }

        stage('Build & Run') {
            steps {
                sh 'mkdir -p $WORKSPACE_DIR'

                dir("$WORKSPACE_DIR") {
                        withCredentials([string(credentialsId: 'OPENAI_API_KEY', variable: 'OPENAI_API_KEY')]) {
                        sh """
                            echo OPENAI_API_KEY=$OPENAI_API_KEY > .env
                            docker compose -f $DOCKER_COMPOSE_FILE up --build -d
                        """
                    }
                }
                

            }
        }
    }

    post {
        failure {
            echo "Build failed!"
        }
    }
}
