pipeline {
  agent any

  environment {
    APP_NAME   = 'antifraude-app'
    IMAGE_TAG  = "jenkins-${env.BUILD_NUMBER}"
    CHART_PATH = 'helm/antifraude'
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build image en Minikube') {
      steps {
        sh '''
          # aseguramos que minikube esté OK
          minikube status

          # build directo dentro del daemon de minikube (simple y seguro)
          minikube image build -t ${APP_NAME}:${IMAGE_TAG} .

          # opcional: también etiquetar "latest" para ArgoCD/Helm por defecto
          minikube image tag ${APP_NAME}:${IMAGE_TAG} ${APP_NAME}:latest
        '''
      }
    }

    stage('Deploy / Restart pods') {
      steps {
        sh '''
          # Si desplegás con ArgoCD/Helm:
          # - El chart usa image: antifraude-app:latest y pullPolicy: IfNotPresent.
          #   Como actualizamos la imagen dentro de minikube, solo reiniciamos los pods
          kubectl -n default rollout restart deploy/${APP_NAME}

          # Esperar a que queden listos
          kubectl -n default rollout status deploy/${APP_NAME} --timeout=180s
        '''
      }
    }

    stage('Smoke tests') {
      steps {
        sh '''
          # Llamada interna al Service (ClusterIP) con port-forward efímero
          kubectl -n default port-forward svc/${APP_NAME} 18080:8080 >/tmp/pf.log 2>&1 &
          PF_PID=$!
          sleep 2

          set -e
          curl -fsS http://127.0.0.1:18080/health
          curl -fsS -X POST http://127.0.0.1:18080/api/transaction \
            -H 'Content-Type: application/json' \
            -d '{"amount": 1234, "from_account":"user1","to_account":"user2","ip":"1.2.3.4"}'
          curl -fsS http://127.0.0.1:18080/api/stats
          kill $PF_PID || true
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: '*/**', onlyIfSuccessful: false
    }
  }
}
