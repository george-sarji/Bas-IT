from flask import Flask, url_for, flash, render_template, redirect, request, g, send_from_directory
from flask import session as login_session
# from model import *
from werkzeug.utils import secure_filename
import locale, os
app = Flask(__name__)
app.secret_key="this is my project"
# SQLAlchemy stuff
### Add your tables here!
# For example:
# from database_setup import Base, Potato, Monkey
from database_setup import *	

from datetime import datetime

from sqlalchemy import create_engine, desc, asc

from sqlalchemy.orm import sessionmaker
# from model import *
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
engine = create_engine('sqlite:///Basit.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
dbsession = DBSession()


def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def verify_login(email, password):
	user=dbsession.query(User).filter_by(email=email).first()
	if (user is None):
		return False
	elif (user.verify_password(password)):
		return True
	return False


@app.route	('/')
def home():
	return render_template('main_page.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
	if (request.method=='GET'):
		return render_template('signup.html')
	elif request.method=='POST':
		name = request.form['name']
		email = request.form['email']
		password = request.form['password']
		confirmpass = request.form['confpassword']
		country = request.form['country']
		dob = request.form['dob'].split('-')
		birth = datetime(year = (int)(dob[0]), month=(int)(dob[1]), day = (int)(dob[2]))
		if (password != confirmpass):
			flash("Your passwords do not match.")
			return redirect(url_for('signup'))
		else:
			newuser = User(email = email, name =name, country=country, dob =birth)
			newuser.hash_password(password)
			dbsession.add(newuser)
			dbsession.commit()
			flash("You have signed up successfully. Welcome aboard, "+name)
			return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	if (request.method=='GET'):
		return render_template('login.html')
	elif request.method=='POST':
		email = request.form['email']
		password = request.form['password']
		if (verify_login(email, password)):
			flash("Successfully logged in. Welcome back!")
			return redirect(url_for('home'))
		else:
			flash("Wrong credentials.")
			return redirect(url_for('login'))



if __name__ == '__main__':
	app.run(debug=True)

