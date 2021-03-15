from sqlalchemy import Column, Integer, String, Text, DateTime
from models.database import Base
from datetime import datetime

class Class(Base):
    __tablename__ = 'class'
    id = Column('id', Integer, primary_key=True)
    day = Column('day', Integer, unique=False)
    time = Column('time', Integer, unique=False)
    campus = Column('campus', String(10), unique=False)
    semester = Column('semester', String(10), unique=False)
    title = Column('title', String(128), unique=False)
    instructer = Column('instructer', String(128), unique=False)
    detail = Column('detail', String(128), unique=False)
    date = Column(DateTime, default=datetime.now())

    def __init__(self, day, time, campus, semester, title, instructer, detail, date):
        self.day = day
        self.time = time
        self.campus = campus
        self.semester = semester
        self.title = title
        self.instructer = instructer
        self.detail = detail
        self.date = date

    def __str__(self):
        return str(self.id) + ':' + self.title