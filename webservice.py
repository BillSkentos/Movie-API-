from pymongo import MongoClient
from flask import Flask , request , Response , jsonify , redirect , render_template,url_for,flash,redirect , session
from pymongo.errors import DuplicateKeyError
import json
import os 
from flask_bcrypt import Bcrypt
from markupsafe import escape




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
    if 'Email' in session:
        email = session['Email']
        if request.method=='POST':
            movie  = movies.count_documents({"year":request.form['year']})
            if movie != 0:
                a_movie = movies.find({"year":request.form['year']})
                return render_template('movie_details.html' , movie = a_movie)
        return render_template('movie-year.html') 
    else:
        return redirect(url_for('login'))   

#run it 
@app.route('/findmoviefromactor' , methods = ['GET' , 'POST'])
def find_movie_from_actor():
    if 'Email' in session:
        email = session['Email']
        if request.method=='POST':
            movie  = movies.count_documents({"actors":request.form['actors']})
            if movie != 0:
                a_movie = movies.find({"actors":request.form['actors']})
                return render_template('movie_details.html' , movie = a_movie)
        return render_template('movie-actor.html') 
    else:
        return redirect(url_for('login'))   






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
    
 










# admin
@app.route('/insertmovie' , methods = ['GET' , 'POST'])
def insert_movie():
    if 'Email' in session and 'User' in session:
        email = session['Email']
        user = session['User']
        if user == 'Admin':
            if request.method == 'POST':
                movie = {"title":request.form['title'] , "actors":request.form['actors'] , "comments":[] , "plot": "not added yet" , 
                "ratings":"0"}
                movies.insert_one(movie)
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
                if minimum != None:
                    movie_list = movies.find({"title":request.form['title']})
                    for iterable in movie_list:
                        if iterable['year']<minimum['year']:
                            minimum=iterable
                    movies.delete_one(minimum)
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
                , "Comments":[]}
                users.insert_one(usr)
                session['Name'] = request.form['Name']
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