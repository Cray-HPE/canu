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

@Library('csm-shared-library') _

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

    stages {
        stage('Set Version') {
            steps {
                script {
                    // If building from tag use that as version
                    // otherwise append branch name to version
                    if (env.TAG_NAME != null) {
                        env.VERSION = env.TAG_NAME
                    } else {
                        env.VERSION=readFile(file: '.version').trim()
                        env.VERSION+="~" + env.BRANCH_NAME.replace("/","_")
                    }

                    sh "echo '${env.VERSION}' > .version"
                    echo "Buildling for ${env.VERSION}"
                }
            }
        }
        stage('Record Environment') {
            steps {
                sh "env"
            }
        }
        stage('Test') {
            steps {
                script {
                    sh "docker run --rm -v \$(pwd):/src cdrx/pyinstaller-linux:python3 nox"
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    sh "docker run --rm -v \$(pwd):/src cdrx/pyinstaller-linux:python3 ./pyinstaller.sh"
                    sh "rpmbuild -bb canu.rpm.spec"
                }
            }
        }
        stage('Publish ') {

            steps {
                script {
                    sh "ls -lhR dist"

                    if (env.BRANCH_NAME == "master") {
                        env.ARTIFACTORY_PATH="dev/master"
                    } else if(!env.BRANCH_NAME.contains("/")) {
                        env.ARTIFACTORY_PATH="predev"
                    } else {
                        env.ARTIFACTORY_PATH=env.BRANCH_NAME
                    }

                    env.ARTIFACTORY_REPO = "csm/MTL/sle15_sp2_ncn/x86_64/${env.ARTIFACTORY_PATH}/metal-team/"
                    rtUpload (
                        serverId: 'ARTIFACTORY_CAR',
                        failNoOp: true,
                        spec: """{
                            "files": [
                                {
                                "pattern": "dist/linux/x86_64/canu-${env.VERSION}-1.x86_64.rpm",
                                "target": "${env.ARTIFACTORY_REPO}/canu-${env.VERSION}"
                                }
                            ]
                        }""",
                    )
                }
            }
        }
    }
    post {
        cleanup {
            // Own files so jenkins can clean them up later
            sh "sudo chown -R jenkins *"
        }
    }
}
