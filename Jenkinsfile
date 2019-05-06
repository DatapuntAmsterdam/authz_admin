#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block()
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t
    }
    finally {
        if (tearDown) {
            tearDown()
        }
    }
}


node {
    stage("Checkout") {
        checkout scm
    }

    stage('Test') {
        tryStep "test", {
            sh "docker-compose -p authz_admin -f ./docker-compose.yml build --no-cache --pull && " +
               "docker-compose -p authz_admin -f ./docker-compose.yml run -u root --rm authz_admin bash -c 'make jenkinstest'"
        }, {
            sh "docker-compose -p authz_admin -f ./docker-compose.yml down"
        }
    }

    stage("Build image") {
        tryStep "build", {
            docker.withRegistry('https://repo.data.amsterdam.nl','docker-registry') {
                def image = docker.build("datapunt/authz_admin:${env.BUILD_NUMBER}", "--build-arg http_proxy=${JENKINS_HTTP_PROXY_STRING} --build-arg https_proxy=${JENKINS_HTTP_PROXY_STRING} .")
                image.push()
            }
        }
    }
}


String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "develop") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                docker.withRegistry('https://repo.data.amsterdam.nl','docker-registry') {
                    def image = docker.image("datapunt/authz_admin:${env.BUILD_NUMBER}")
                    image.pull()
                    image.push("acceptance")
                }
            }
        }
    }

    node {
        stage("Deploy to ACC") {
        tryStep "deployment", {
            build job: 'Subtask_Openstack_Playbook',
            parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-authz-admin.yml'],
                ]
            }
        }
    }

    stage('Waiting for approval') {
        slackSend channel: '#ci-channel', color: 'warning', message: 'OAuth2 service is waiting for Production Release - please confirm'
        input "Deploy to Production?"
    }

    node {
        stage('Push production image') {
            tryStep "image tagging", {
                docker.withRegistry('https://repo.data.amsterdam.nl','docker-registry') {
                def image = docker.image("datapunt/authz_admin:${env.BUILD_NUMBER}")
                    image.pull()
                    image.push("production")
                    image.push("latest")
                }
            }
        }
    }

    node {
        stage("Deploy") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-authz-admin.yml'],
                ]
            }
        }
    }
}
