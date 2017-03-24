from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from sqlalchemy import create_engine

from database_setup import *

engine = create_engine('sqlite:///Basit.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# You can add some starter data for your database here.
firstcourse = Course(name="MS Office", subject="Microsoft Office Package", lessons = 5, instructor=1, attendees=0)
admin = User(name="Admin", email="admin@admin.com", instructor=True)
admin.hash_password("admin")
lesson = Lesson(course=1, date=datetime(year=2017, month=03, day=24), number=1, video="1Ge7f94Be_Q")
session.add(lesson)
session.add(firstcourse)
session.add(admin)
session.commit()
