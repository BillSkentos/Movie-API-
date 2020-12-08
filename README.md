# MovieFlix  2020 Web Service

This is a web service built in flask and mongodb that lets a user interact with a movie information website using a RESTFUL API .
***RUNS ONLY ON LINUX 

## Instructions 

* Install <code>Docker</code> from your terminal 
    
    Docker is an app that helps you create in image of your program and deploy it using a docker container so that  users can run  the app through Docker without worrying  about package or infrastructure independencies .
    
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
                add - (one line command)
                4. sudo add-apt-repository -y "deb [arch=amd64]
                https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
                5. sudo apt-get update
                6. sudo apt install docker-ce

  2. To run our docker image paired with a mongodb image we also need <code>docker-compose</code> which can be installed with the steps below :

                1. sudo curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-`uname
                    -s`-`uname -m` -o /usr/local/bin/docker-compose (one line command)
                2. sudo chmod +x /usr/local/bin/docker-compose

* Now that Docker and docker-compose are install you have to download this repository from your terminal and go to that directory.

        1. git clone https://github.com/BillSkentos/MovieFlix2020_E17136_SKENTOS_VASILIS.git
        
        2. cd MovieFlix2020_E17136_SKENTOS_VASILIS


* Run flask image paired with a mongodb database as an image to store our data  by typing <code> sudo docker-compose up -d  </code> in your terminal .


    1. Enter a web browser and type <code> localhost:5000 </code> to access the web service using port 5000

    2. You have now accessed the home page . You can either click <code>Register</code> to create an account or click login and enter with email :<code>admin@gmail.com</code> and password : <code>admin</code> , as a default admin is created on the home page if no admin exists in our database .

    3. 
        1. If you are a simple user you can now access all of the functionalities of the API for a simple user like entering a title to get a list of information about all movies with the same title(same applies for entering a year or an actor name ) . You can also write a comment on a movie or rate a movie but you have to know the year the movie has been published . A movie that has been inserted by an admin is automatically published in <code>2020</code> unless the admin upgrades it . 

        2. You can also view all your comments , rate a movie from a scale of 1-10 and see all your ratings.

        3. You can lastly log out or delete your account . 

        4. In case you type information like for example a movie that does not exist or a wrong year of publishment and get a message 
        like <code> Movie not found </code> you can either go pages back using the <code><-</code> arrow button on top left or click on the message displayed to go to your user page immediatelly.



    4. If you have logged in using the default admin account or a different admin account you access the admin user page . An admin 
    has all the options a simple user has (except of deleting his account) and some new that are listed below . 
            
        1. Insert a new movie . You enter a movie name and a protagonist for a movie . The year is set to 2020 as default 

        2. Update a movie . Change the title , year of publish , delete or insert an actor or change the movie plot.

        3. Delete a  movie . If 2 movies with same title exist the one with the oldest year will be deleted .  

        4. Upgrade a  simple user to admin user or delete a simple user account . An admin cannot delete his account or other admins !!

        5. Delete user comments . You can access a list of all users comments for every movie and type a number to delete a comment from the list corresponding to that number . 


        * When a movie , a user or a comment is deleted the instance is deleted in every field it exists . For example if an admin     deletes a  movie , then all comments on that movie will also be deleted from the user comments


* You can close the web service by typing <code>sudo docker-compose down</code> in your terminal . In case our container is deleted we have included a file called <code>data</code> inside our <code>docker-compose.yml </code> that has all our mongodb database instances (users , movies) stored as backup and can be accessed if we rebuild our image by repeating this proccess .              
