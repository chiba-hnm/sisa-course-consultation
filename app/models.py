# from sqlalchemy import Column, Integer, String, Text, DateTime
# # from models.database import Base
# from app.app import app
# from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy

# app.config['SQLALCHEMY_DATABASE_URI'] = 'or 'postgresql://postgres:@localhost/sample'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# class Course(db.Model):
#     __tablename__ = 'course'
#     id = Column('id', Integer, primary_key=True)
#     day = Column('day', String(10), unique=False)
#     time = Column('time', Integer, unique=False)
#     campus = Column('campus', String(10), unique=False)
#     semester = Column('semester', String(10), unique=False)
#     title = Column('title', String(128), unique=False)
#     instructer = Column('instructer', String(128), unique=False)
#     detail = Column('detail', Text, unique=False)
#     # date = Column(DateTime, default=datetime.now())

#     def __init__(self, day, time, campus, semester, title, instructer, detail):
#         self.day = day
#         self.time = time
#         self.campus = campus
#         self.semester = semester
#         self.title = title
#         self.instructer = instructer
#         self.detail = detail
#         # self.date = date

#     def __str__(self):
#         return str(self.id) + ':' + self.title