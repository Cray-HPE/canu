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
        label "metal-gcp-builder"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: "10"))
        timestamps()
    }

    environment {
        SPEC_FILE = "canu.spec"
        IS_STABLE = "${getBuildIsStable()}"
        BUILD_METADATA = getRpmRevision(isStable: env.IS_STABLE)
    }

    stages {
        stage("Prepare") {
            steps {
                script {
                    runLibraryScript("addRpmMetaData.sh", env.SPEC_FILE)
                    sh "make prepare"
                }
            }
        }

        stage("Test") {
            steps {
                script {
                    sh "make test"
                }
            }
        }

        stage("Build Binary") {
            steps {
                script {
                    sh "make binary"
                }
            }
        }
        stage("Build RPM") {
            steps {
                script {
                    sh "make rpm"
                }
            }
        }

        stage('Publish ') {
            steps {
                script {
                    uploadCsmRpms(component: "canu", pattern: "dist/rpmbuild/RPMS/x86_64/*.rpm", arch: "x86_64", isStable: env.IS_STABLE)
                    uploadCsmRpms(component: "canu", pattern: "dist/rpmbuild/SRPMS/*.rpm", arch: "src", isStable: env.IS_STABLE)
                }
            }
        }
    }
    post {
        cleanup {
            // Own files so jenkins can clean them up later
            sh "sudo chown -R jenkins ${env.WORKSPACE}"
        }
    }
}
