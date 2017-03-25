from sqlalchemy import Column,Integer,String, Date, ForeignKey, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, func
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()

#PLACE YOUR TABLE SETUP INFORMATION HERE



class User(Base):
	__tablename__ = 'user'
	id = Column(Integer, primary_key=True)
	name = Column(String(255))
	email = Column(String(255))
	password = Column(String)
	country = Column(String)
	language = Column(String)
	dob = Column(Date)
	instructor = Column(Boolean)


	def hash_password(self, password):
		self.password = pwd_context.encrypt(password)

	def set_photo(self, photo):
		self.photo = photo

	def verify_password(self, password):
		return pwd_context.verify(password, self.password)

	def set_password(self, password):
		self.hash_password(password)

class Course(Base):
	__tablename__ = 'course'
	id = Column(Integer, primary_key=True)
	name = Column(String(255))
	subject = Column(String(255))
	lessons = Column(Integer)
	instructor = Column(Integer, ForeignKey('user.id'))
	attendees = Column(Integer)


class Lesson(Base):
	__tablename__ = 'lesson'
	id = Column(Integer, primary_key=True)
	title = Column(String)
	course = Column(Integer, ForeignKey('course.id'))
	date = Column(Date)
	number = Column(Integer)
	video = Column(String)



class CourseAttendee(Base):
	__tablename__='courseattendee'
	id=Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('user.id'))
	course_id = Column(Integer, ForeignKey('course.id'))


engine = create_engine('sqlite:///Basit.db')


Base.metadata.create_all(engine)
