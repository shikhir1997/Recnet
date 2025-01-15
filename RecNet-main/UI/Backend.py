from flask import Flask,render_template,request,redirect,session
from flask_session import Session
import os



import pymysql.cursors
import re

from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#connection to database
conn = pymysql.connect(host='localhost',
                        user='root',
                        password='',
                        database='Recnet-keystone',
                        )

#universal path where we are storing images 
app.config["IMAGE_UPLOADS"]="/Users/ruchikakukreja/Desktop/KeyStone/UI/static/profile_photos"
app.config["ALLOWED_EXTENSIONS"]=["PNG","JPG","JPEG"]

cur = conn.cursor()
cur.execute("select * from user_sign_details")
output = cur.fetchall()
for i in output:
    print(i)


def allowed_files(file_name):
    return '.' in file_name and file_name.rsplit('.',1)[1].upper() in app.config["ALLOWED_EXTENSIONS"]

@app.route("/", methods=['GET', 'POST'])
def start():
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    msg=""
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        password = request.form['password']
        email = request.form['email']

        cur = conn.cursor()
        sql="SELECT * from `accounts` where `email`=%s and `password`=%s"
        cur.execute(sql,(email,password))
        account = cur.fetchone()
        if account:
            session["email"]=email
            msg="Logged In successfully"
            return render_template('check.html',msg=msg)
        else:
            msg="EMail id or Password is incorrect"
            return render_template('index.html',msg=msg)

    elif request.method == 'POST' and 'email' not in request.form:
        msg="Please enter email"
        return render_template('index.html',msg=msg)
    elif request.method == 'POST' and 'password' not in request.form:
        msg="Please enter password"
        return render_template('index.html',msg=msg)


    return render_template('index.html')



@app.route("/register",methods=['GET', 'POST'])
def register():
    print("POST received")
    msg=''
    print(request.method)
    if request.method=="POST":
        print("ALALALA")
        print(request.form)
    if  request.method=="POST" and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'agree' in request.form and 'insta_handle' in request.form:
        print("Inside if")
        username = request.form['name']
        password = request.form['password']
        email = request.form['email']
        insta=request.form['insta_handle']
        print(username,password,email,insta)


        
        

        #testing for already existing username
        cur = conn.cursor()
        sql="SELECT * from `user_sign_details` where `username`=%s"
        cur.execute(sql,(username))
        account = cur.fetchone()
        if account:
            msg = 'This username is already taken'
            print(msg)
            return render_template('register.html',msg=msg)

        #testing if the mail-id already exists
        cur = conn.cursor()
        sql="select * from user_sign_details WHERE `email`=%s"
        cur.execute(sql,(email))
        account = cur.fetchone()
        if account:
            msg = 'This mail-id is already taken'
            return render_template('register.html',msg=msg)
      
        
        #testing if proper mail address
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if  not re.fullmatch(regex,email):
            msg = 'Invalid email address!'
            return render_template('register.html',msg=msg)

        #testing if userame proper
        regex_username="^[A-Za-z][A-Za-z0-9_]{4,12}$"
        if not re.match(regex_username, username):
            msg = 'Username should start with an alphabet and can contain alphabets,numbers or underscore and length should be between 5 and 13 '
            return render_template('register.html',msg=msg)

        #testing if instagram_handle proper
        regex_instagram="/(?:(?:http|https):\/\/)?(?:www.)?(?:instagram.com|instagr.am|instagr.com)\/(\w+)/igm"
        if not re.match(regex_instagram,insta):
            msg="Enter valid Instagram URL"
            return render_template('register.html',msg=msg)



        
        #testing for profile picture
        if request.files:
            print("File aaya")
            image=request.files['profile_photo']
            if image.filename=="":
                msg="Image must have a name"
                return render_template('index.html',msg=msg)
            if not allowed_files(image.filename):
                msg="That extension is not allowed"
                return render_template('index.html',msg=msg)
            else:
                filename=secure_filename(image.filename)
                image.save(os.path.join(app.config["IMAGE_UPLOADS"],filename) )
                print("Image Saved")
    

        #registering new user
        print(username,password,email)
        cur=conn.cursor()
        sql="INSERT INTO `user_sign_details` VALUES (%s, %s, %s,%s,%s)"
        cur.execute(sql,(username,email,password,insta,filename))
        conn.commit()
        msg = 'You have successfully registered!'
        return render_template("check.html",msg=msg)

    elif 'name' not in request.form:
        msg="Please enter you user name"
        return render_template("register.html",msg=msg)
    elif 'password' not in request.form:
        msg="Please enter password"
        return render_template("register.html",msg=msg)
    elif 'email' not in request.form:
        msg="Please enter email"
        return render_template("register.html",msg=msg)
    elif 'agree' not in request.form:
        msg="Please agree to terms and conditions"
        return render_template("register.html",msg=msg)
    return render_template('register.html')

@app.route("/loginnew",methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        print("ahaaa")
        session["email"] = None
        return render_template("index.html")

    
if __name__ == '__main__':
    app.run(debug=True)