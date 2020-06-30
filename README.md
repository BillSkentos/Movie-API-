# MovieFlix  2020 Web Service

This is a web service built in flask that lets a user interact with a movie information website using a RESTFUL API 

## Instructions 

* Install Docker from your terminal 
    
    Docker is an app that helps you create in image of your program and deploy it using a docker container so that  users can run  the app through Docker without worrying  about package or infrastructure 
    independencies .
    
    To install Docker Engine, you need the 64-bit version of one of these Ubuntu versions:

        *Ubuntu Focal 20.04 (LTS)
        *Ubuntu Eoan 19.10
        *Ubuntu Bionic 18.04 (LTS)
        *Ubuntu Xenial 16.04 (LTS)


  1. Use following commands to install Docker  .

                1. sudo apt-get update
                2. sudo apt install -y apt-transport-https ca-certificates curl
                software-properties-common
                3. curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key
                add -
                4. sudo add-apt-repository -y "deb [arch=amd64]
                https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
                5. sudo apt-get update
                6. sudo apt install docker-ce

  2. To run our docker image paired with a mongodb image we also need '''docker-compose''' which can be installed with the steps below :

                1. sudo curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-`uname
                    -s`-`uname -m` -o /usr/local/bin/docker-compose
                2. sudo chmod +x /usr/local/bin/docker-compose
