from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from database_setup import *

engine = create_engine('sqlite:///Basit.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# You can add some starter data for your database here.
firstcourse = Course(name="MS Office", subject="Microsoft Office Package", lessons = 5, instructor=1, attendees=0)
session.add(firstcourse)
session.commit()
