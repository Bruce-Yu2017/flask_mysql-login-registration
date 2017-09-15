from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
app = Flask(__name__)
mysql = MySQLConnector(app,'login_regi')
app.secret_key = 'codingdojo'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/registration', methods = ['POST'])
def regi():
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    emailregi = request.form['email_regi']
    password = request.form['password_regi']
    passwordmd5 = md5.new(password).hexdigest()
    confirm = request.form['confirm']
    count = 0
    
    if firstname.isalpha() and len(firstname) >= 2 and lastname.isalpha() and len(lastname) >= 2:
        count += 1
    else:
        flash("Your name should be letters only, at least 2 characters.")
    
    if not EMAIL_REGEX.match(emailregi):
        flash('Invalid email address.')
    else:
        query = "SELECT email FROM user"
        regi_email = mysql.query_db(query)
        found_email = False
        for n in regi_email:
            if emailregi == n['email']:
                found_email = True
                flash('This email has been registered. Please use another one.')
        if not found_email:
            count += 1

    if password == confirm:
        count += 1
    else:
        flash('Please confirm your password.')

    if count == 3:
        query = "INSERT INTO user (first_name, last_name, email, password) VALUES (:first_name, :last_name, :email, :password)"
        data = {
              'first_name': firstname,
              'last_name': lastname,
              'email': emailregi,
              'password': passwordmd5
              }
        mysql.query_db(query, data)
        new_user = mysql.query_db('SELECT MAX(id) as id FROM user')
        session['id'] = new_user[0]['id']
        
        flash('Your registration is success!')
        return redirect('/success')
    return redirect('/')
    

@app.route('/login', methods = ['POST'])
def log():
    login_email = request.form['email_login']
    login_password = request.form['password_login']
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    email_found = False

    if len(login_email) < 1:
        flash('Your email can not be empty.')
    else:
        if not EMAIL_REGEX.match(login_email):
            flash('Invalid email address')
        else:
            query = "SELECT id, email FROM user"
            user_info = mysql.query_db(query)
            for n in user_info:
                if login_email == n['email']:
                    email_found = True
                    session['id'] = n['id']
    
    if email_found:
        if len(login_password) < 1:
            flash('Your password is empty')
        else:
            query = "SELECT password from user where id = :id"
            query_data = {'id': session['id']}
            user_info2 = mysql.query_db(query, query_data)
            hashed_password = md5.new(login_password).hexdigest()
            if hashed_password == user_info2[0]['password']:
                return redirect('/success')
            else:
                flash('Your password is incorrect!')
    return redirect('/')

@app.route('/success')
def success():
    query = "SELECT * FROM user WHERE id = :id"
    data = {'id': session['id']}
    newuser = mysql.query_db(query, data)
    return render_template('login.html', newuser = newuser)





app.run(debug = True)


