from pymongo import MongoClient
from flask import Flask , request , Response , jsonify , redirect , render_template,url_for,flash,redirect , session
from pymongo.errors import DuplicateKeyError
import json
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired ,Length , Email ,EqualTo , ValidationError
import os 
from flask_bcrypt import Bcrypt
from flask_login import LoginManager , UserMixin ,login_user , login_manager ,current_user ,logout_user , login_required
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
    if 'Email' in session:
        email = session['Email']
        return render_template('simple.html')
    else:
        return redirect(url_for('login'))    

@app.route('/adminuser')
def adminuser():
    if 'Email' in session:
        email = session['Email']
        return render_template('admin.html')
    else:
        return redirect(url_for('login'))    
        





@app.route('/')
def home():
    return render_template('moviehome.html')



#find specific movie by title 
@app.route('/findmoviebytitle' ,methods = ['GET' , 'POST'])
def find_movie_by_title():
    if 'Email' in session:
        email = session['Email']
        if request.method =='POST':
                movie = movies.find({"title":request.form['title']}).count()
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
            movie  = movies.find({"year":request.form['year']}).count()
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
            movie  = movies.find({"actors":request.form['actors']}).count()
            if movie != 0:
                a_movie = movies.find({"actors":request.form['actors']})
                return render_template('movie_details.html' , movie = a_movie)
        return render_template('movie-year.html') 
    else:
        return redirect(url_for('login'))   



#if admin
@app.route('/insertmovie' , methods = ['GET' , 'POST'])
def insert_movie():
    if 'Email' in session:
        email = session['Email']
        if request.method == 'POST':
            movie = {"title":request.form['title'] , "actors":request.form['actors']}
            movies.insert(movie)
            return '''  <h1>  Movie has been inserted  <h1> '''
        else:
            return render_template('movie-insert.html') 
    else:
        return redirect(url_for('login'))         

    
    



@app.route('/register' , methods = ['GET' ,'POST'])
def register():
    if request.method=='POST':
        user = users.find_one({"Email":request.form['Email']})
        if user == None:
            hashed_password = bcrypt.generate_password_hash(request.form['Password']).decode('utf-8')
            user = {"Name":request.form['Name'],"Surname":request.form['Surname'],"Email":request.form['Email'],"Password":hashed_password,"User":"Simple"
            , "Comments":[]}
            users.insert_one(user)
            session['Name'] = request.form['Name']
            return redirect(url_for('home'))    

        return 'User with specific email already exists .'

    return render_template('register.html')            


@app.route('/login' , methods = ['GET' , 'POST'])
def login():
    if request.method == 'POST':
        loginuser = users.find_one({"Email":request.form['Email']})
        if loginuser:
            if  bcrypt.check_password_hash(loginuser['Password'],request.form['Password']):
                session['Email'] = request.form['Email']
                if loginuser["User"]=="Simple":
                    return redirect(url_for('simpleuser'))
                elif loginuser["User"]=="Admin":
                        return redirect(url_for('adminuser'))
            return 'Invalid email/password combination'
        return 'Invalid email'
    return render_template('login.html')            



@app.route('/logout')
def logout():
    # remove the email from the session if it's there
    session.pop('Email', None)
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)