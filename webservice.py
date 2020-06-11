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
    return render_template('simple.html')



@app.route('/')
def home():
    return render_template('moviehome.html')



#find specific movie by title 
@app.route('/findmoviebytitle' ,methods = ['GET' , 'POST'])
def find_movie_by_title():
    if request.method =='POST':
            movie = movies.find_one({"title":request.form['title']})
            if movie != None:
                 movie = {'_id': str(movie['_id']) , 'Title' : movie['title'] , 
                'Actors' : movie['actors'] , 'year' : movie , 'plot':movie['plot'] }
                 return ''' {% for key, value in movie.items() %}
                                  {{ value.item }} 
                            {% endfor %}  '''
    return render_template('movie-title.html')            

    
             


    




#if admin
@app.route('/insertmovie' , methods = ["POST"])
def insert_movie():

    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("Bad json content " , status = 500 , mimetype='application/json')
    if data == None:
        return Response("no data has been added",status = 500 , mimetype='application/json')
    if not "title" in data or not "actors" in data:
        return Response("Information incompleted", status = 500 , mimetype='application/json')
    if hashnumbers(data["actors"])==True:
        return Response("Insert valid actor names " ,status = 500 , mimetype='application/json')
    if movies.find({"title":data["title"]}).count()==0:
        movie = {"title": data["title"] , "actors" : data["actors"]}
        movies.insert_one(movie)
        return Response("Movie has been added . " ,status = 200 , mimetype='application/json')        
    else:
        return Response("Movie already exists . " ,status = 200 , mimetype='application/json')

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
            return 'Invalid email/password combination'
        return 'Invalid email'
    return render_template('login.html')            



@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('Email', None)
    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)