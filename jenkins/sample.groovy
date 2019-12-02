/* https://jenkinsci.github.io/job-dsl-plugin */

def Repo1 = 'https://github.com/username/repo.git'
def Repo2 = 'https://username@bitbucket.org/username/repo.git'
def RepoCreds = 'Repo-Creds'

job('Basic-Creds') {
    logRotator {
        numToKeep(1)
        artifactNumToKeep(1)
    }
    scm {
        git {
            remote {
                url(Repo1)
                credentials(RepoCreds)
                branches('*/master')
            }
        }
    }
    wrappers {
        credentialsBinding {
            string('USERNAME','UN-admin')
            string('PASSWORD','PWD-admin')
        }
    }
    steps {
        shell('''
        python $WORKSPACE/SubDirectory/script.py
        ''')
    }
}
job('Paramters-Job') {
    logRotator {
        numToKeep(1)
        artifactNumToKeep(1)
    }
    parameters {
        choiceParam('ENVIRONMENT',['Production','Non-Production','Development','Test','DR','QA'], description = '')
        choiceParam('DEVICE',['PrimaryRouter','SecondaryRouter'], description = '')
        stringParam('HOSTNAME')
        stringParam('DEVICE_IP')
    }
    scm {
        git {
            remote {
                url(Repo1)
                credentials(RepoCreds)
                branches('*/master')
            }
        }
    }
    wrappers {
        credentialsBinding {
            string('USERNAME','UN-netdevice')
            string('PASSWORD','PWD-netdevice')
        }
    }
    steps {
        shell('''
        python $WORKSPACE/SubDirectory/script.py
        ''')
    }
}
job('Scheduled-Job') {
    logRotator {
        numToKeep(1)
        artifactNumToKeep(1)
    }
    scm {
        git {
            remote {
                url(Repo2)
                credentials(RepoCreds)
                branches('*/master')
            }
        }
    }
    triggers {
        cron("*/15 * * * *")
    }
    wrappers {
        credentialsBinding {
            string('USERNAME','UN-serviceaccount')
            string('PASSWORD','PWD-serviceaccount')
        }
    }
    steps {
        shell('''
        python $WORKSPACE/SubDirectory/script.py
        ''')
    }
    publishers {
        slackNotifier {
            notifyEveryFailure(true)
        }
    }
}