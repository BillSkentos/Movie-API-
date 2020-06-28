from pymongo import MongoClient
from flask import Flask , request , Response , jsonify , redirect , render_template,url_for,redirect , session
from pymongo.errors import DuplicateKeyError
import json
import os 
from flask_bcrypt import Bcrypt
from markupsafe import escape
import re




mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')
db = client['MovieFlixDB']

users = db['Users']
movies = db['Movies']





def hashnumbers(inputString):
    return any(char.isdigit() for char in inputString)






app = Flask(__name__)
bcrypt = Bcrypt(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY







#returns the simple user page or admin page if user is an admin
@app.route('/simpleuser')
def simpleuser():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if user == 'Simple':
            return render_template('simple.html')
        elif user == 'Admin':
            return redirect(url_for('adminuser'))   
    else:
        return redirect(url_for('login'))    


#returns the admin page if the user is an admin 
@app.route('/adminuser')
def adminuser():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if user == 'Admin':
            return render_template('admin.html')
        else:
            return redirect(url_for('login'))    
    else:
        return redirect(url_for('login'))    
        


#home page
@app.route('/')
def home():
    
    #if no admin exists insert default one 
    admn = users.find_one({"Email":"admin@gmail.com"})
    if admn == None:
        admin_password = bcrypt.generate_password_hash("admin") #hash user password 
        admn = {"Name":"admin" , "Surname":"admin", "Email":"admin@gmail.com" ,  "Password":admin_password ,
        "Comments":[] , "ratings":[] , "User":"Admin"}
        users.insert_one(admn)

    return render_template('moviehome.html')



#find specific movie by title 
@app.route('/findmoviebytitle' ,methods = ['GET' , 'POST'])
def find_movie_by_title():
    if 'Email' in session and 'User' in session: #check if user is logged in 
        email = session['Email']
        user = session['User']
        if request.method =='POST':
                movie = movies.count_documents({"title":request.form['title']}) #find total of movies with the title
                if movie != 0:
                    a_movie = movies.find({"title":request.form['title']}) 
                    return render_template('movie_details.html' , movie = a_movie ) #return the movies 
                else:
                    return render_template('movie-title.html')  #else try again
        return render_template('movie-title.html')
    else:
        return redirect(url_for('login'))                


#find movies with same year of publish
@app.route('/findmoviefromyear' , methods = ['GET' , 'POST'])
def find_movie_from_year():
    if 'Email' in session and 'User' in session: #check if user is logged in
        email = session['Email']
        user = session['User']
        if request.method=='POST':
            movie  = movies.count_documents({"year":request.form['year']}) #find total of movies with same year
            if movie != 0:
                a_movie = movies.find({"year":request.form['year']})
                return render_template('movie_details.html' , movie = a_movie) #return all the movies
            else:
                return render_template('movie-year.html') #else try again
        return render_template('movie-year.html') 
    else:
        return redirect(url_for('login'))   


#find movies with the same actors
@app.route('/findmoviefromactor' , methods = ['GET' , 'POST'])
def find_movie_from_actor():
    if 'Email' in session and 'User' in session: #if user is logged in
        user = session['User']
        email = session['Email']
        if request.method=='POST':
            movie_list = movies.find( {"actors": {"$in": [ request.form['actor'] ] } } ) #find all movies where actor plays 
            if movie_list !=None:
                a_movie = movies.find( {"actors": {"$in": [ request.form['actor'] ] } } )    
                return render_template('movie_details.html' , movie = a_movie) #return the movies
            else:
                return render_template('movie-actor.html') #else try again
        return render_template('movie-actor.html') 
    else:
        return redirect(url_for('login'))   







#rate a movie
@app.route('/ratemovie' ,methods = ['GET' , 'POST'])
def rate_movie():
    if 'Email' in session and 'User' in session: #if user is logged in
        email = session['Email']
        user = session['User']
        if request.method == 'POST': #find requested movie
            movie = movies.find_one({"title":request.form['movie'] , "year":request.form['year']})
            if movie != None: 
                usr = users.find_one({"Email":email}) #find the logged user 
                if not usr['ratings']:   #if user has not rated a movie
                    
                    #insert a rating to the user ratings array
                    users.update_one({"Email":email} , 
                    {"$push": { 'ratings':request.form['movie'] + ":" + request.form['rating']} } )

                    #update average rating of specific movie 
                    movies.update_one({"title":request.form['movie'] , "year":request.form['year']} , 
                    {'$set':{'ratings': find_average(request.form['movie'] , request.form['rating'])} } )

                else: #if user has rated movies
                    for i , rating in enumerate(usr['ratings']): #iterate through the ratings of the user  

                        if request.form['movie'] in rating: #if user has already rated the movie 

                            old_rating = -int(re.findall(r"\d+", rating)[-1]) #extract the old rating from the rating string 
                            users.update_one({"Email":email} ,{"$pull":{'ratings':rating}} ) #remove the rating from the user 
                            
                            #find new average rating of movie after removing the rating 
                            movies.update_one({"title":request.form['movie'] , "year":request.form['year']} , 
                            {"$set": {'ratings':find_average(request.form['movie'] , old_rating)} } )

                            #insert new rating in user ratings 
                            users.update_one({"Email":email} , 
                            {"$push": {'ratings':request.form['movie'] + ":" + request.form['rating']}})

                            #find new movie average after inserting new rating
                            movies.update_one({"title":request.form['movie'] , "year":request.form['year']} , 
                            {"$set": {'ratings':find_average(request.form['movie'] , request.form['rating'])} } )

                        elif i+1  == len(usr['ratings']): #if user has not rated the movie 

                            users.update_one({"Email":email} , 
                            {"$push": {'ratings':request.form['movie'] + ":" + request.form['rating']}})

                            movies.update_one({"title":request.form['movie'] , "year":request.form['year']} , 
                            {"$set": {'ratings':find_average(request.form['movie'] , request.form['rating'])} } )

                return ''' <h2> Movie has been updated . Type "/" for home or "/simpleuser" to go to start page </h2> '''

            return render_template('movie-rate.html')

        else:
            return render_template('movie-rate.html')        
    else:
        return redirect(url_for('login'))    
     



@app.route('/removerating' , methods = ['GET', 'POST'])
def remove_rating():
    if 'Email' in session and 'User' in session: #check if user is logged in 
        email = session['Email']
        user = session['User']
        if request.method == 'POST':
            usr = users.find_one({"Email":email}) #find specific user 
            movie = movies.find_one({"title":request.form['movie'] , "year":request.form['year']}) #find specific movie 

            if movie != None: #if movie exists 
        
                for rating in usr['ratings']:
                    if request.form['movie'] in rating: #if a user has rated the movie

                        old_rating = -int(re.findall(r"\d+", rating)[-1]) #extract the rating value  from the rating string 
                        users.update_one({"Email":email} , {"$pull": {"ratings":rating}}) #remove the rating from user 
                   
                        #find new movie average rating  after removing the user's rating
                        movies.update_one({"title":request.form['movie'] , "year":request.form['year']} , 
                        {"$set": {'ratings':find_average(request.form['movie'] , old_rating)} } )

                return ''' <h2> Rating has removed . Type  '/simpleuser' to return to your page </h2> '''

            else:
                return render_template('del-rate.html')             

        else:
            return render_template('del-rate.html')    
    else:
        return redirect(url_for('login'))    



#function to find the average rating of a movie 
def find_average(movie,user_rating):
    ratings_list=[] 
    average = 0
    for specific_user in users.find(): #append all ratings of users to a list 
        for rating in specific_user['ratings']:
            if movie in rating:
                ratings_list.append(int(re.findall(r"\d+", rating)[-1]))

    length = len(ratings_list)
    if length==0: #if only one user in list make length : 1 to avoid division by zero  
        length=1

    average=sum(ratings_list)/(int(length))  #compute average
    return int(average)




#write a comment on a movie 
@app.route('/commentmovie' , methods = ['GET' , 'POST'])
def comment_movie():
    if 'Email' in session and 'User' in session: #check if user is logged in 
        email = session['Email']
        user = session['User']
        if request.method == 'POST':

            movie = movies.find_one({"title":request.form['movie'] , "year":request.form['year']}) #find specific movie

            if movie != None: #if movie exists 

                movie_and_year = request.form['movie'] + " " + request.form['year'] #insert movie and year to a string 
                
                #insert comment for specific movie and year with user email and his comment
                movies.update_one(  { "title":request.form['movie']  , "year":request.form['year']}, 
                {"$push":{"comments":movie_and_year + " " + email + ":" + request.form['comment']}})
                 
                #update the user's comments  
                users.update_one({"Email":email}, 
                {"$push":{"Comments":request.form['movie'] + " " + request.form['year'] + ":" + request.form['comment']} })

                return ''' <h2>  Comment has been added . Type '/simpleuser' to return to your page  </h2> '''
            else:
                return render_template('movie-comment.html')    
        else:
            return render_template('movie-comment.html')    
    else:
        return redirect(url_for('login'))        
    
 
   




#delete a comment 
@app.route('/deletecomment' , methods = ['GET' , 'POST'])
def delete_comment():
    if 'Email' in session and 'User' in session: #if user is logged in 
        email = session['Email']
        user = session['User']
        if request.method == 'POST':

            usr = users.find_one({"Email":email}) #find specific user 
            comment_num = request.form['comm-num'] #get index of comment in the comments list 
            comment_num = int(comment_num) 
            exists = False #suppose index of comment does not exist 

            for i , value in enumerate(usr['Comments']): #iterate comments of user 
                if i+1 == comment_num: #if index corresponds to a comment
                    exists = True #index exists

                    #remove comment from user  
                    users.update_one({"Email":email} , 
                    {"$pull":{"Comments":value}})
                    
                    #remove the comment from the movie 
                    iterable = movies.find() 
                    for tainia in iterable: #iterate through the comments of every movie to find it 
                        for comment in tainia['comments']:
                            in_str = all(x in comment for x in value.replace(":", " ").split(" "))
                            if in_str == True: #if user comment exists in movie comments delete it from the movie
                                movies.update_one(tainia , {"$pull": {"comments":comment} } )
                    
                elif i+1 == len(usr['Comments']) and exists == False:  #if index not found
                    return ''' <h2> Comment with specific number in list does not exist . Type '/simpleuser' to return to your page </h2>'''

            return ''' <h2> Comment has been deleted . Type '/simpleuser' to return to your page </h2> '''

        else:
            return redirect(url_for('login'))       
    else:
        return redirect(url_for('login'))    


#view your comments and ratings
@app.route('/viewcommentsandratings' , methods = ['GET'])
def view_comments_and_ratings():
    if 'Email' in session and 'User' in session: #if user is logged in 
        email = session['Email']
        user = session['User']    
        usr = users.find_one({"Email":email}) #find specifc user and return his comments and ratings 
        return render_template('view-comms-rates.html' , user = usr)
                
    else:
        return redirect(url_for('login'))    


#delete your account 
@app.route('/deleteaccount' , methods = ['GET'])
def delete_account():
    if 'Email' in session and 'User' in session: #if user is logged in 
        email = session['Email']
        user = session['User']
        if user == 'Simple':  #if user is not an admin 

            users.delete_one({"Email":email}) #delete specific user 
            user_movies = movies.find()

            for movie in user_movies: #delete all the user's comments from a movie 
                for comment in movie['comments']:
                    if email in comment:
                        movies.update_one( {"comments": comment } ,
                        {"$pull": {"comments": comment}})
            return render_template('moviehome.html' , message = 'Account has been deleted')
        else:
            return redirect(url_for('login'))    
    else:
        return redirect(url_for('login'))    


# admin inserts a movie 
@app.route('/insertmovie' , methods = ['GET' , 'POST'])
def insert_movie():
    if 'Email' in session and 'User' in session: 
        email = session['Email']
        user = session['User']
        if user == 'Admin': #if user is logged in and is an admin 
            if request.method == 'POST': 
                #insert new movie with default year 2020
                movie = {"title":request.form['title'] , "actors":[] , "comments":[] , "plot": "not added yet" , "year":"2020", 
                "ratings":"0"}

                movies.insert_one(movie)
                
                #insert the actor in the movie 
                movies.update_many({"title":request.form['title']}  ,  
                {"$push":{"actors":request.form['actors']}}  )

                return '''  <h2>  Movie has been inserted . Type '/adminuser' to return to your page <h2> '''
            else:
                return render_template('movie-insert.html') 

        else: #non admin users redirected to login
            return redirect(url_for('login'))        
    else:
        return redirect(url_for('login'))         

#admin deletes a movie 
@app.route('/deletemovie' , methods = ['GET' , 'POST'])
def delete_movie():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if user == 'Admin': #if user is logged in and user is an admin
            if request.method == 'POST':
                 
                #if multiple movies of same title exist delete the oldest one  
                minimum = movies.find_one({"title":request.form['title']}) 
                if minimum != None:
                    movie_list = movies.find({"title":request.form['title']})
                    for iterable in movie_list:
                        if iterable['year']<minimum['year']: #find the movie with the smallest year
                            minimum=iterable
                    store_year = minimum['year'] #minimum will be deleted so store the movie year for later use 
                    movies.delete_one(minimum) #delete the movie with the oldest year 

                    cur = users.find()
                    for xristis in cur: #delete movie rating from user ratings if movie is deleted 
                        for rating in xristis['ratings']:
                            if request.form['title'] in rating:
                                users.update_one( xristis  , {"$pull":{ 'ratings': rating }  } )

                    i = users.find()
                    for customer in i: #delete the user comments where the movie was 
                        for comment in customer['Comments']:
                            if request.form['title'] in comment and store_year in comment:
                                users.update_one( {"Comments": comment } ,
                                {"$pull": {"Comments": comment}})

                    
                    return '''  <h2>  Movie has been deleted . Type '/adminuser' to return to your page  </h2>  '''
                else:
                    return render_template('movie-delete.html')      
            else: 
                return render_template("movie-delete.html")
        else: #if user is not admin redirect to login 
            return redirect(url_for('login'))          
    else:
        return redirect(url_for('login'))           


#admin deletes a simple user account 
@app.route('/deleteuser' , methods = ['GET' , 'POST'])
def delete_user():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if user == 'Admin': #if user is logged in and is an admin 
            if request.method == 'POST':
                usr = users.find_one({"Email":request.form['Email']}) #find specific user 
                if usr != None: 
                    if usr['User'] != 'Simple': #non admin users cannot be deleted 
                        return render_template('user-delete.html')
                    else:
                        users.delete_one(usr) #delete the user 
                        return ''' <h2>  User has been deleted . Type '/adminuser' to return to your page  </h2>   '''  
                else:
                    return render_template('user-delete.html')
            else:
                return render_template('user-delete.html')
        else: #if user is not an admin redirects to login 
            return redirect(url_for('login'))        
    else:
        return redirect(url_for('login'))    




#admin upgrades a user to admin 
@app.route('/upgradeuser' , methods = ['GET', 'POST'])
def upgrade_user():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if user == 'Admin': #if user is logged in and user is an admin
            if request.method == 'POST':
                specific_user = users.find_one({"Email":request.form['email']}) #check if user exists 
                if specific_user != None:
                    users.update_one({"Email":request.form['email']} , {'$set':{"User":"Admin"}}) #upgrade to admin
                    return ''' <h1>  User has been updated to Admin . Type '/adminuser' to return to your page </h1>   '''
                else:
                    return render_template('user-upgrade.html')
            else:
                return render_template('user-upgrade.html')        
            
        else: #if the user logged is not admin redirect to login 
            return redirect(url_for('login'))    
    else:
        return redirect(url_for('login'))







#admin view all comments and deletes a comment 
@app.route('/viewanddelete' , methods = ['GET', 'POST'])
def view_and_delete():
    if 'Email' in session and 'User' in session:
        email=session['Email']
        user = session['User']
        if user == 'Admin': #if logged user is admin

            movie_list = list(movies.find({})) #create a list of all movies in collection 

            if request.method == 'POST':

                comment_num = request.form['comm-number'] #get given index 
                comment_num = int(comment_num)
                comment_list = [] #list will store all comments 
                exists = False #suppose index does not exist in comment list

                for movie in movie_list: #append all movie comments to the new list 
                    for idxc , comment in enumerate(movie['comments']):
                        comment_list.append(comment) 

                for l , com in enumerate(comment_list): #iterate the new list where all comments are stored 
                    if l+1 == comment_num: #if submitted index corresponds to a comment in the list 
                        comment_list.remove(com)  
                        exists = True #index exists

                        for movie in movie_list: #iterate through the comments of every movie 
                            for sxolio in movie['comments']:
                                if com in sxolio: #if  comment is found in movie comment list delete the movie comment
                                    movies.update_one( movie , {"$pull":{"comments":sxolio}})   

                                    user_list = users.find()
                                    for xristis in user_list: #iterate through all users comments  
                                        for c in xristis['Comments']: 
                                            in_str = all(x in sxolio for x in c.replace(":", " ").split(" "))
                                            if in_str == True: #if comment is found in user comment delete the user comment 
                                                users.update_one(xristis , {"$pull":{'Comments':c}})
                                                return '''<h2> Comment has been succesfully deleted . Type '/adminuser' to return to your page </h2> '''

                    elif l+1==len(comment_list) and exists == False: #if index not found 
                        return ''' Comment not found .  Type '/adminuser' to return to your page '''                            



                return ''' Comment deleted . Type '/adminuser' to return to your page '''        

            else:
                return render_template('delete-user-comment.html' , movies = movie_list)    

        else: #if user not admin redirect to login 
            return redirect(url_for('login'))    
    else:
        return redirect(url_for('login'))    





#admin selects  movie to update and redirects to new page after submitting 
@app.route('/selectmovietoupdate' , methods = ['GET' , 'POST'])
def select_movie_to_update():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if user == 'Admin': #if user is logged and user is admin 
            if request.method == 'POST':

                #find requested movie 
                tainia = movies.find_one({'title':request.form['movie'] , "year":request.form['year']}  )
                if tainia != None:
                    session['Movie'] = request.form['movie'] #insert movie title year and plot to session 
                    session['Movie_year'] = request.form['year']
                    session['Movie_plot'] = tainia['plot']
                    return render_template('movie-update.html' , movie = tainia) #return the movie 
                else:
                    return '''  Movie not found . Type '/adminuser' to return to your page '''
            return render_template('admin.html')    

        else: #if user not admin redirect to login 
            return redirect(url_for('login'))    
    else:
        return redirect(url_for('login'))    



@app.route('/executemovieupdate' , methods = ['GET', 'POST'])
def execute_movie_update():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if user == 'Admin': #if user is admin 
            if 'Movie' in session and 'Movie_year' in session and 'Movie_plot' in session: #check if movie in session 

                movie = session['Movie']
                old_movie  = str(movie) #store old movie title 
                year = session['Movie_year']
                old_year = str(year) #store old year 
                plot = session['Movie_plot']

                tainia = movies.find_one({'title':movie , "year":year}) #find requested movie

                if request.method == 'POST':

                    new_title = request.form.get('new-title') #get submitted fields 
                    new_plot = request.form.get('new-plot')
                    new_year = request.form.get('new-year')
                    new_actor = request.form.get('new-actor')
                    old_actor = request.form.get('old-actor')

                    if new_title: #update the title 
                        movies.update_one({"title":movie , "year":year} , {"$set":{"title":new_title} } )

                        session['Movie'] = new_title #update the session 
                        movie = session['Movie']

                        movie_list = list(movies.find({})) #change old title in the movie comments 
                        for mv in movie_list:
                            for index , sxolio in enumerate(mv['comments']):
                                if old_movie in sxolio:
                                    mv['comments'][index] = sxolio.replace(old_movie,new_title)
                            movies.update_one({"_id":mv['_id']} , {"$set":{"comments":mv['comments']}})       
                             
                        user_list = list(users.find({}))
                        for usr in user_list: #change old title in the user comments 
                            for idxc , comment in enumerate(usr['Comments']):
                                if old_movie in comment:
                                    usr['Comments'][idxc]=comment.replace(old_movie,new_title)
                            users.update_one({"_id": usr['_id']}, {"$set": {"Comments": usr['Comments']}})

                        for xr in user_list: #change old title in the user ratings 
                            for r , rating in enumerate(xr['ratings']):
                                if old_movie in rating:
                                    xr['ratings'][r] = rating.replace(old_movie,new_title)
                            users.update_one({"_id": xr['_id']} , {"$set":{"ratings":xr['ratings']}})            


                    if  new_year : #update the year 
                        movies.update_one({"title":movie , "year":year} , {"$set": {"year":new_year}}) 
                        session['Movie_year']=new_year
                        year = session['Movie_year'] #update the session 

                        movie_list= list(movies.find({}))
                        for mv in movie_list: #change the year in the comments of the movie 
                            for index , sxolio in enumerate(mv['comments']):
                                if str(movie) in sxolio and old_year in sxolio:
                                    mv['comments'][index] = sxolio.replace(old_year,new_year)
                            movies.update_one({"_id":mv['_id']} , {"$set":{"comments":mv['comments']}}) 

                        user_list = list(users.find({}))
                        for usr in user_list: #change the year in the user comments on the movie 
                            for idxc , comment in enumerate(usr['Comments']):
                                if old_movie in comment:
                                    usr['Comments'][idxc]=comment.replace(old_year,new_year)
                            users.update_one({"_id": usr['_id']}, {"$set": {"Comments": usr['Comments']}})    
                            

                    if new_plot: #update movie plot 
                        movies.update_one({"title":movie , "year":year} , {"$set":{"plot":new_plot}})
                        session['Movie-plot'] = new_plot
                        plot = session['Movie-plot'] 

                    if new_actor: #insert new actor 
                        movies.update_one({"title":movie , "year":year} , {"$push":{"actors":new_actor}})

                    if old_actor: #delete an actor 
                        mv = movies.find_one({"title":movie , "year":year})
                        exists = False #suppose actor does not exist 
                        for i , iterable in enumerate(mv['actors']):
                            if old_actor in iterable:
                                movies.update_one({"title":movie, "year":year} , {"$pull":{"actors":old_actor}})
                                exists = True #actor exists and is deleted  
                            elif i+1 == len(mv['actors']) and exists == False: #if actor does not exist in list 
                                return ''' Actor does not exist in movie . All other updates are done. Type '/adminuser' to return to your page  '''

 
  
                    return ''' Movie has been updated  . Type '/adminuser' to return to your page  '''
                                                                                                          
                else:
                    return render_template('movie-update.html' , movie = tainia)        
            else:
                return redirect(url_for('admin.html'))    

        else: #if user is simple redirect to login 
            return redirect(url_for('login')) 
    else:
        return redirect(url_for('login'))    


#register 
@app.route('/register' , methods = ['GET' ,'POST'])
def register():
        if request.method=='POST':
            
            usr = users.find_one({"Email":request.form['Email']})

            if usr == None: #if user with specific email does not already exist 
                hashed_password = bcrypt.generate_password_hash(request.form['Password']) #hash user password 
                usr = {"Name":request.form['Name'],"Surname":request.form['Surname'],"Email":request.form['Email'],"Password":hashed_password,"User":"Simple"
                , "Comments":[] , "ratings":[]} 
                users.insert_one(usr) #insert created user to collection 
                session['Email'] = request.form['Email']
                session['User'] = "Simple" #insert user to session 
                return render_template('simple.html')

            return '''  <h2>  User with specific email already exists . Type '/register' to register again or go back  </h2> '''
        else:
            return render_template('register.html')


#login 
@app.route('/login' , methods = ['GET' , 'POST'])
def login():
        if request.method == 'POST':
            loginuser = users.find_one({"Email":request.form['Email']})
            
            if loginuser: #if user with specific email exists 
                if  bcrypt.check_password_hash(loginuser['Password'],request.form['Password']): #if hashed password matches with password 
                    
                    session['Email'] = request.form['Email']

                    if loginuser["User"]=="Simple": #if user is simple redirect to simple page 
                        session['User'] = "Simple"
                        return redirect(url_for('simpleuser'))

                    elif loginuser["User"]=="Admin": #if user is admin redirect to admin page 
                        session['User'] = "Admin"
                        return redirect(url_for('adminuser'))
                

                return '''<h2>Invalid email/password combination Type '/login' to try again</h2> '''
            return '''<h2> Invalid email .Type '/login' to try again </h2> '''
        else:
            return render_template('login.html')            
     


#logout 
@app.route('/logout')
def logout():
    # remove everything from session and redirect to login 
    session.pop('Email', None)
    session.pop('User' , None)
    if 'Movie' in session and 'Movie_year' in session and 'Movie_plot' in session:
        session.pop('Movie' , None)
        session.pop('Movie_year' , None)
        session.pop('Movie_plot' , None)
    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
