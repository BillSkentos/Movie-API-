from pymongo import MongoClient
from flask import Flask , request , Response , jsonify , redirect , render_template,url_for,flash,redirect , session
from pymongo.errors import DuplicateKeyError
import json
import os 
from flask_bcrypt import Bcrypt
from markupsafe import escape
import re



client = MongoClient('mongodb://localhost:27017/')
db = client['MovieFlixDB']

users = db['Users']
movies = db['Movies']





def hashnumbers(inputString):
    return any(char.isdigit() for char in inputString)



app = Flask(__name__)
bcrypt = Bcrypt(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/simpleuser')
def simpleuser():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        return render_template('simple.html')
    else:
        return redirect(url_for('login'))    

@app.route('/adminuser')
def adminuser():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        return render_template('admin.html')
    else:
        return redirect(url_for('login'))    
        



@app.route('/')
def home():
    return render_template('moviehome.html')



#find specific movie by title 
@app.route('/findmoviebytitle' ,methods = ['GET' , 'POST'])
def find_movie_by_title():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if request.method =='POST':
                movie = movies.count_documents({"title":request.form['title']})
                if movie != 0:
                    a_movie = movies.find({"title":request.form['title']}) 
                    return render_template('movie_details.html' , movie = a_movie )
        return render_template('movie-title.html')
    else:
        return redirect(url_for('login'))                



@app.route('/findmoviefromyear' , methods = ['GET' , 'POST'])
def find_movie_from_year():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if request.method=='POST':
            movie  = movies.count_documents({"year":request.form['year']})
            if movie != 0:
                a_movie = movies.find({"year":request.form['year']})
                return render_template('movie_details.html' , movie = a_movie)
        return render_template('movie-year.html') 
    else:
        return redirect(url_for('login'))   

@app.route('/findmoviefromactor' , methods = ['GET' , 'POST'])
def find_movie_from_actor():
    if 'Email' in session and 'User' in session:
        user = session['User']
        email = session['Email']
        if request.method=='POST':
            movie_list = movies.find( {"actors": {"$in": [ request.form['actor'] ] } } )
            if movie_list !=None:
                a_movie = movies.find( {"actors": {"$in": [ request.form['actor'] ] } } )    
                return render_template('movie_details.html' , movie = a_movie)
                
        return render_template('movie-actor.html') 
    else:
        return redirect(url_for('login'))   








@app.route('/ratemovie' ,methods = ['GET' , 'POST'])
def rate_movie():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if request.method == 'POST':
            movie = movies.find_one({"title":request.form['movie'] , "year":request.form['year']})
            if movie != None:
                usr = users.find_one({"Email":email})
                print("Entered")
                if not usr['ratings']:
                    print("empty")
                    users.update_one({"Email":email} , 
                    {"$push": { 'ratings':request.form['movie'] + ":" + request.form['rating']} } )
                    movies.update_one({"title":request.form['movie'] , "year":request.form['year']} , 
                    {'$set':{'ratings': find_average(request.form['movie'] , request.form['rating'])} } )

                else:
                    for i , rating in enumerate(usr['ratings']):

                        if request.form['movie'] in rating:
                            print("found")
                            old_rating = -int(re.findall(r"\d+", rating)[-1])
                            users.update_one({"Email":email} ,{"$pull":{'ratings':rating}} )
                            print("Old rating is " , old_rating)
                            movies.update_one({"title":request.form['movie'] , "year":request.form['year']} , 
                            {"$set": {'ratings':find_average(request.form['movie'] , old_rating)} } )

                            
                            users.update_one({"Email":email} , 
                            {"$push": {'ratings':request.form['movie'] + ":" + request.form['rating']}})

                            
                            movies.update_one({"title":request.form['movie'] , "year":request.form['year']} , 
                            {"$set": {'ratings':find_average(request.form['movie'] , request.form['rating'])} } )

                        elif i+1  == len(usr['ratings']):
                            print("not found I will update")
                            users.update_one({"Email":email} , 
                            {"$push": {'ratings':request.form['movie'] + ":" + request.form['rating']}})

                            movies.update_one({"title":request.form['movie'] , "year":request.form['year']} , 
                            {"$set": {'ratings':find_average(request.form['movie'] , request.form['rating'])} } )

                return '''  <h2> Movie has been rated  </h2> '''
        else:
            return render_template('movie-rate.html')        
    else:
        return redirect(url_for('login'))    
     



@app.route('/removerating' , methods = ['GET', 'POST'])
def remove_rating():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if request.method == 'POST':
            usr = users.find_one({"Email":email})
            movie = movies.find_one({"title":request.form['movie'] , "year":request.form['year']})
            if movie != None:
        
                for rating in usr['ratings']:
                    if request.form['movie'] in rating:

                        old_rating = -int(re.findall(r"\d+", rating)[-1])
                        users.update_one({"Email":email} , {"$pull": {"ratings":rating}}) 

                        movies.update_one({"title":request.form['movie'] , "year":request.form['year']} , 
                        {"$set": {'ratings':find_average(request.form['movie'] , old_rating)} } )
                return ''' <h2> Rating removed ! </h2> '''

            else:
                return ''' <h2> Movie not found  <h2> '''             

        else:
            return render_template('del-rate.html')    
    else:
        return redirect(url_for('login'))    



def find_average(movie,user_rating):
    ratings_list=[]
    average = 0
    for specific_user in users.find():
        for rating in specific_user['ratings']:
            if movie in rating:
                ratings_list.append(int(re.findall(r"\d+", rating)[-1]))

    average=sum(ratings_list)/len(ratings_list)
    for i in ratings_list:
        print(i)
    print("Average is :" , average)   
    return int(average)




@app.route('/commentmovie' , methods = ['GET' , 'POST'])
def comment_movie():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if request.method == 'POST':
            movie = movies.find_one({"title":request.form['movie'] , "year":request.form['year']})
            if movie != None:
                movies.update_one(  { "title":request.form['movie']  , "year":request.form['year']}, 
                {"$push":{"comments":email + ":" + request.form['comment']}})
                users.update_one({"Email":email}, 
                {"$push":{"Comments":request.form['movie'] + " " + request.form['year'] + ":" + request.form['comment']} })
                return '''  Comment has been added  '''
            else:
                return """  <h2> Movie not found   </h2> """    
        else:
            return render_template('movie-comment.html')    
    else:
        return redirect(url_for('login'))        
    
 
   





@app.route('/deletecomment' , methods = ['GET' , 'POST'])
def delete_comment():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if request.method == 'POST':
            usr = users.find_one({"Email":email})
            comment_num = request.form['comm-num']
            comment_num = int(comment_num)
            exists = False
            for i , value in enumerate(usr['Comments']):
                if i+1 == comment_num:
                    print("Comment number exists")
                    exists = True
                    users.update_one({"Email":email} , 
                    {"$pull":{"Comments":value}})
                elif i+1 == len(usr['Comments']) and exists == False:
                    print('Comment does not exist')
                    return ''' Comment with specific number in list does not exist '''

            return '''  Comment has been deleted '''

        else:
            return redirect(url_for('login'))       
    else:
        return redirect(url_for('login'))    

@app.route('/viewcommentsandratings' , methods = ['GET'])
def view_comments_and_ratings():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        usr = users.find_one({"Email":email})
        return render_template('view-comms-rates.html' , user = usr)
                
    else:
        return redirect(url_for('login'))    

@app.route('/deleteaccount' , methods = ['GET'])
def delete_account():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        users.delete_one({"Email":email})
        return render_template('moviehome.html' , message = 'Account has been deleted')
    else:
        return redirect(url_for('login'))    


# admin
@app.route('/insertmovie' , methods = ['GET' , 'POST'])
def insert_movie():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if user == 'Admin':
            if request.method == 'POST':
                movie = {"title":request.form['title'] , "actors":[] , "comments":[] , "plot": "not added yet" , "year":"not added yet", 
                "ratings":"0"}
                movies.insert_one(movie)
                movies.update_many({"title":request.form['title']}  ,  
                {"$push":{"actors":request.form['actors']}}  )
                return '''  <h1>  Movie has been inserted  <h1> '''
            else:
                return render_template('movie-insert.html') 
        else:
            return redirect(url_for('login'))        
    else:
        return redirect(url_for('login'))         

#admin    
@app.route('/deletemovie' , methods = ['GET' , 'POST'])
def delete_movie():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if user == 'Admin':
            if request.method == 'POST':
                minimum = movies.find_one({"title":request.form['title']})
                print(minimum['title'])
                if minimum != None:
                    print("Entered")
                    movie_list = movies.find({"title":request.form['title']})
                    for iterable in movie_list:
                        if iterable['year']<minimum['year']:
                            minimum=iterable
                    store_year = minimum['year'] #minimum will be deleted so store the movie year for later use 
                    movies.delete_one(minimum)
                    cur = users.find()
                    for xristis in cur:
                        for rating in xristis['ratings']:
                            if request.form['title'] in rating:
                                users.update_one( xristis  , {"$pull":{ 'ratings': rating }  } )
                    i = users.find()
                    for customer in i:
                        for comment in customer['Comments']:
                            if request.form['title'] in comment and store_year in comment:
                                print(comment) 
                                users.update_one( {"Comments": comment } ,
                                {"$pull": {"Comments": comment}})

                    
                    return '''  <h1>  Movie has been deleted   </h1>  '''
                else:
                    return '''  <h1> Movie does not exist  </h1>  '''           
            else:
                return render_template("movie-delete.html")
        else:
            return redirect(url_for('login'))          
    else:
        return redirect(url_for('login'))           


#admin
@app.route('/deleteuser' , methods = ['GET' , 'POST'])
def delete_user():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if user == 'Admin':
            if request.method == 'POST':
                usr = users.find_one({"Email":request.form['Email']})
                if usr != None:
                    if usr['User'] != 'Simple':
                        return ''' <h1> Deletion failed   </h1>  '''
                    else:
                        users.delete_one(usr)
                        return ''' <h1>  User has been deleted   </h1>   '''  
                else:
                    return '''  <h1>  User does not exist </h1>  '''
            else:
                return render_template('user-delete.html')
        else:
            return redirect(url_for('login'))        
    else:
        return redirect(url_for('login'))    




#admin
@app.route('/upgradeuser' , methods = ['GET', 'POST'])
def upgrade_user():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if user == 'Admin':
            if request.method == 'POST':
                specific_user = users.find_one({"Email":request.form['email']})
                if specific_user != None:
                    users.update_one({"Email":request.form['email']} , {'$set':{"User":"Admin"}})
                    return ''' <h1>  User has been updated to Admin .  </h1>   '''
                else:
                    return ''' <h1> User does not exist </h1>  '''
            else:
                return render_template('user-upgrade.html')        
            
        else:
            return redirect(url_for('login'))    
    else:
        return redirect(url_for('login'))






@app.route('/register' , methods = ['GET' ,'POST'])
def register():
        if request.method=='POST':
            usr = users.find_one({"Email":request.form['Email']})
            if usr == None:
                hashed_password = bcrypt.generate_password_hash(request.form['Password']).decode('utf-8')
                usr = {"Name":request.form['Name'],"Surname":request.form['Surname'],"Email":request.form['Email'],"Password":hashed_password,"User":"Simple"
                , "Comments":[] , "ratings":[]}
                users.insert_one(usr)
                session['Email'] = request.form['Email']
                session['User'] = "Simple"
                return redirect(url_for('home'))    

            return 'User with specific email already exists .'
        else:
            return render_template('register.html')


@app.route('/login' , methods = ['GET' , 'POST'])
def login():
        if request.method == 'POST':
            loginuser = users.find_one({"Email":request.form['Email']})
            if loginuser:
                if  bcrypt.check_password_hash(loginuser['Password'],request.form['Password']):
                    session['Email'] = request.form['Email']
                    if loginuser["User"]=="Simple":
                        session['User'] = "Simple"
                        return redirect(url_for('simpleuser'))
                    elif loginuser["User"]=="Admin":
                        session['User'] = "Admin"
                        return redirect(url_for('adminuser'))
                return 'Invalid email/password combination'
            return 'Invalid email'
        else:
            return render_template('login.html')            
     


@app.route('/logout')
def logout():
    # remove the email and user from the session if it's there
    session.pop('Email', None)
    session.pop('User' , None)
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)