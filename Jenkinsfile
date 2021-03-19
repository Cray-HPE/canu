// (C) Copyright [2020] Hewlett Packard Enterprise Development LP
//
// Permission is hereby granted, free of charge, to any person obtaining a
// copy of this software and associated documentation files (the "Software"),
// to deal in the Software without restriction, including without limitation
// the rights to use, copy, modify, merge, publish, distribute, sublicense,
// and/or sell copies of the Software, and to permit persons to whom the
// Software is furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
// THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
// OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
// ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
// OTHER DEALINGS IN THE SOFTWARE.

@Library('csm-shared-library@feature/CASMINST-1369') _

pipeline {
    agent {
        node { label 'metal-gcp-builder' }
    }

    // Configuration options applicable to the entire job
    options {
        // This build should not take long, fail the build if it appears stuck
        timeout(time: 30, unit: 'MINUTES')

        // Don't fill up the build server with unnecessary cruft
        buildDiscarder(logRotator(numToKeepStr: '5'))

        timestamps()
    }

    environment {
        RELEASE_NAME = 'canu'
    }

    stages {
        stage('Set Version') {
            steps {
                script {
                    env.VERSION = sh(returnStdout: true, script: "cat .version").trim()
                    if (env.GIT_BRANCH != "master") {
                        env.VERSION = "${env.VERSION}-${env.GIT_COMMIT[0..6]}"
                        env.ARTIFACTORY_REPO = "http://car.dev.cray.com/artifactory/csm/MTL/sle15_sp2_ncn/x86_64/${env.GIT_BRANCH}/metal-team/"
                    } else {
                        env.ARTIFACTORY_REPO = "http://car.dev.cray.com/artifactory/csm/MTL/sle15_sp2_ncn/x86_64/dev/master/metal-team/"
                    }
                }
            }
        }
        stage('Record Environment') {
            steps {
                sh '''
                   env
                '''
            }
        }
        stage('Build') {
            steps {
                script {
                    def env = [
                        "RELEASE_VERSION=${env.RELEASE_VERSION}"
                    ]
                    withEnv(env) {
                        sh '''
                            docker run --rm -v $(pwd):/workspace python:3.9-slim bash -c '
                              cd /workspace
                              apt update
                              apt install -y libc-bin binutils
                              pip install pyinstaller

                              pyinstaller --clean -y canu.spec
                            '
                        '''
                    }
                }
            }
        }
        stage('Publish ') {
            steps {
                script {
                    sh """
                      ls -lh dist/*
                    """

                    rtServer (
                        id: 'ARTI_DOCKER_REGISTRY',
                        url: "https://${ARTI_DOCKER_REGISTRY}/artifactory",
                        credentialsId: 'artifact-server',
                        deploymentThreads: 10
                    )

                    rtUpload (
                        serverId: 'ARTI_DOCKER_REGISTRY',
                        failNoOp: true,
                        spec: """{
                            "files": [
                                {
                                "pattern": "dist/canu",
                                "target": "${env.ARTIFACTORY_REPO}/canu-${env.VERSION}"
                                }
                            ]
                        }""",
                    )
                }
            }
        }
    }
}
