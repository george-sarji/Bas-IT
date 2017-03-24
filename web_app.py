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
		checker = dbsession.query(User).filter_by(email=email).first()
		if (checker is not None):
			flash("Email is already in use.")
			return redirect(url_for('signup'))
		if (password != confirmpass):
			flash("Your passwords do not match.")
			return redirect(url_for('signup'))
		else:
			newuser = User(email = email, name =name, country=country, dob =birth, instructor = False)
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
			user = dbsession.query(User).filter_by(email=email).first()
			flash("Successfully logged in. Welcome back, "+user.name+"!")
			login_session['email'] = email
			login_session['name'] = user.name
			login_session['language'] = user.language
			login_session['instructor'] = user.instructor
			return redirect(url_for('home'))
		else:
			flash("Wrong credentials.")
			return redirect(url_for('login'))

@app.route('/courses')
def courses():
	if ('email' not in login_session):
		flash("You must be logged in to perform this.")
		return redirect(url_for('login'))
	else:
		currentuser = dbsession.query(User).filter_by(email = login_session['email']).first()
		allcourses = dbsession.query(Course).all()
		availablecourses =[]
		i=0
		for course in allcourses:
			isavailable = dbsession.query(CourseAttendee).filter_by(course_id=course.id).filter_by(user_id=currentuser.id).first()
			if (isavailable is None):	
				availablecourses.append(course)
				i=i+1
		return render_template('courses.html', courses=availablecourses)


@app.route('/courses/<int:id>')
def coursesignup(id):
	if ('email' not in login_session):
		flash("You must be logged in to perform this.")
		return redirect(url_for('login'))
	else:
		email = login_session['email']
		user = dbsession.query(User).filter_by(email=login_session['email']).first()
		course = dbsession.query(Course).filter_by(id=id).first()
		if (course is None):
			flash("Invalid course.")
			return redirect(url_for('courses'))
		else:
			course.attendees = course.attendees+1
			attendeeslist = dbsession.query(CourseAttendee).filter_by(user_id=user.id).filter_by(course_id=id).first()
			if (attendeeslist is not None):
				flash("You are already signed up for this course!")
				return redirect(url_for('courses'))
			attendee = CourseAttendee(user_id=user.id, course_id=course.id)
			flash("Successfully signed up!")
			dbsession.add(attendee)
			dbsession.commit()
			return redirect(url_for('courses'))


@app.route('/lesson/<int:course>/<int:id>')
def lesson(course, id):
	if ('email' not in login_session):
		flash("You must be logged in to perform this.")
		return redirect(url_for('login'))
	else:
		course =dbsession.query(Course).filter_by(id=course).first()
		lesson = dbsession.query(Lesson).filter_by(id=id).filter_by(course=course).first()
		if (course is None or lesson is None):
			flash("Invalid course/lesson.")
			return redirect(url_for('courses'))
		else:
			return render_template('lesson.html', lesson=lesson, course=course)

@app.route('/mycourses')
def mycourses():
	if ('email' not in login_session):
		flash("You must be logged in to perform this.")
		return redirect(url_for('login'))
	else:
		user = dbsession.query(User).filter_by(email=login_session['email']).first()
		courseid = dbsession.query(CourseAttendee).filter_by(user_id=user.id).all()
		courses =[]
		for course in courseid:
			currentcourse = dbsession.query(Course).filter_by(id=course.course_id).first()
			courses.append(currentcourse)
		return render_template('mycourses.html', courses=courses)

@app.route('/mycourses/<int:id>')
def deletecourse(id):
	if ('email' not in login_session):
		flash("You must be logged in to perform this.")
		return redirect(url_for('login'))
	else:
		user = dbsession.query(User).filter_by(email=login_session['email']).first()
		courseid = dbsession.query(CourseAttendee).filter_by(user_id=user.id).filter_by(course_id=id).first()
		if courseid is not None:
			dbsession.delete(courseid)
			dbsession.commit()
			flash("You have successfully unsubscribed from this course.")
			return redirect(url_for('mycourses'))
		else:
			flash("You are not signed up to this course!")
			return redirect(url_for('mycourses'))


if __name__ == '__main__':
	app.run(debug=True)

