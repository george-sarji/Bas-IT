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


@app.route('/acp')
def admincp():
	if ('email' not in login_session):
		flash("You must be logged in to perform this.")
		return redirect(url_for('login'))
	else:
		user = dbsession.query(User).filter_by(email=login_session['email']).first()
		if (user.instructor == False):
			flash("Access denied.")
			return redirect(url_for('home'))
		else:
			latestuser= dbsession.query(User).order_by(User.id.desc()).first()
			return render_template('admincp.html', user=latestuser)


@app.route('/logout')
def logout():
	if ('email' not in login_session):
		flash("You must be logged in to perform this.")
		return redirect(url_for('login'))
	else:
		user = dbsession.query(User).filter_by(email=login_session['email']).first()
		del login_session['email']
		del login_session['name']
		del login_session['language']
		del login_session['instructor']
		flash("Good bye, "+user.name)
		return redirect(url_for('home'))


@app.route('/acp/addcourse', methods=['POST', 'GET'])
def addcourse():
	if ('email' not in login_session):
		flash("You must be logged in to perform this.")
		return redirect(url_for('login'))
	else:
		user=dbsession.query(User).filter_by(email = login_session['email']).first()
		if (user.instructor==False):
			flash("Access denied.")
			return redirect(url_for('home'))
		else:
			if (request.method=='GET'):
				return render_template('addcourse.html')
			else:
				name = request.form['name']
				subject = request.form['subject']
				lessons = 0
				instructor=user.id
				attendees=0
				newcourse = Course(name = name, subject = subject, lessons=lessons, instructor=instructor, attendees=attendees)
				dbsession.add(newcourse)
				dbsession.commit()
				flash("Course added successfully.")
				return redirect(url_for('admincp'))

@app.route('/acp/course/<int:id>')
def managecourse(id):
	if ('email' not in login_session):
		flash("You must be logged in to perform this.")
		return redirect(url_for('login'))
	else:
		user=dbsession.query(User).filter_by(email = login_session['email']).first()
		if (user.instructor==False):
			flash("Access denied.")
			return redirect(url_for('home'))
		else:
			currentcourse = dbsession.query(Course).filter_by(id=id).first()
			if (currentcourse is None):
				flash("Invalid course")
				return redirect(url_for('admincp'))
			else:
				return render_template('managecourse.html', course=currentcourse)



@app.route('/acp/user/<int:id>', methods=['POST', 'GET'])
def manageuser(id):
	if ('email' not in login_session):
		flash("You must be logged in to perform this.")
		return redirect(url_for('login'))
	else:
		user=dbsession.query(User).filter_by(email = login_session['email']).first()
		if (user.instructor==False):
			flash("Access denied.")
			return redirect(url_for('home'))
		else:
			currentuser = dbsession.query(User).filter_by(id=id).first()
			if (currentuser is None):
				flash("Invalid user.")
				return redirect(url_for('admincp'))
			else:
				if (request.method=='GET'):
					return render_template('manageuser.html', user=currentuser)
				else:

					name = request.form['name']
					email = request.form['email']
					country = request.form['country']
					language = request.form['language']
					dob = datetime(year=(int)(request.form['dob'].split('-')[0]), month=(int)(request.form['dob'].split('-')[1]), day=(int)(request.form['dob'].split('-')[2]))
					instructor = request.form['instructor']
					if (name != currentuser.name):
						currentuser.name=name
					if (email != currentuser.email):
						currentuser.email=email
					if (country != currentuser.country):
						currentuser.country=country
					if (dob != currentuser.dob):
						currentuser.dob=dob
					if (instructor == "True"):
						currentuser.instructor=True
					elif (instructor == "False"):
						currentuser.instructor=False
					if (language != currentuser.language):
						currentuser.language=language
					dbsession.commit()
					if (user.id==currentuser.id):
						login_session['email']=email
						login_session['name']=name
						login_session['language']=language
						login_session['instructor']=currentuser.instructor
					flash("User edited successfully.")
					return redirect(url_for('manageuser', id=currentuser.id))


@app.route('/acp/course/<int:course_id>/add', methods=['POST', 'GET'])
def addlesson(course_id):
	if ('email' not in login_session):
		flash("You must be logged in to perform this.")
		return redirect(url_for('login'))
	else:
		user=dbsession.query(User).filter_by(email = login_session['email']).first()
		if (user.instructor==False):
			flash("Access denied.")
			return redirect(url_for('home'))
		else:
			if (request.method=='GET'):
				return render_template('addcourse.html')
			else:
				course = dbsession.query(Course).filter_by(id=course_id).first()
				if (course is None):
					flash("Invali course.")
					return redirect(url_for('managecourses'))

				lessons = dbsession.query(Lesson).filter_by(course=course_id).order_by(Lesson.number.desc()).first()
				title = request.form['title']
				date = datetime(year=(int)(request.form['date'].split('-')[0]), month=(int)(request.form['date'].split('-')[1]), day=(int)(request.form['date'].split('-')[2]))
				video = request.form['video']
				if (lessons is None):
					# We have no lessons for this course; add the first one.
					newlesson = Lesson(title=title, date=date, video=video, number=0, course=course_id)
					course.lessons=course.lessons+1
					dbsession.add(newlesson)
					dbsesion.commit()
					flash("Lesson added successfully to course.")
					return redirect(url_for('managecourse', id=course_id))
				else:
					# We have a previous lesson, use the last number + 1
					newlesson = Lesson(title=title, date=date, video=video, number=lessons.number+1, course=course_id)
					dbsession.add(newlesson)
					course.lessons=course.lessons+1
					dbsesion.commit()
					flash("Lesson added successfully to course.")
					return redirect(url_for('managecourse', id=course_id))

@app.route('/acp/course/<int:id>/erase')
def erasecourse(id):
	if ('email' not in login_session):
		flash("You must be logged in to perform this.")
		return redirect(url_for('login'))
	else:
		user=dbsession.query(User).filter_by(email = login_session['email']).first()
		if (user.instructor==False):
			flash("Access denied.")
			return redirect(url_for('home'))
		else:
			course = dbsession.query(Course).filter_by(id=id).first()
			if (course is None):
				flash("Invalid course.")
				return redirect(url_for('managecourses'))
			else:
				mylessons = dbsession.query(Lesson).filter_by(course=id).all()
				for lesson in mylessons:
					dbsession.delete(lesson)
				dbsession.delete(course)
				dbsession.commit()
				flash("Course and lessons deleted successfully.")
				return redirect(url_for('managecourses'))



if __name__ == '__main__':
	app.run(debug=True)
