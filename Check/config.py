from flask import Flask
from app.routes import routes_check
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
import json
from datetime import datetime
import os
from os.path import exists

from os import path
from flask_xmlrpcre.xmlrpcre import *
from flask_cors import CORS

app = Flask(__name__, template_folder='app/templates')
CORS(app, resources={r"/API/*": {"origins": "http://127.0.0.1:5000"}})
# Register the imported routes
app.register_blueprint(routes_check, url_prefix='/')


# SQL access layer initialization
DATABASE_FILE = "check_id_database.sqlite"
db_exists = False

if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s' % (DATABASE_FILE), echo=True)

Base = declarative_base()

# Declaration of data tables


class Check_in(Base):
    __tablename__ = 'check_in'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    space = Column(String)
    datetime = Column(DateTime)
    action = Column(String)
    course_id = Column(String)

    def __repr__(self):
        return f"<Check_in(id={self.id})>"


class Check_out(Base):
    __tablename__ = 'check_out'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    space = Column(String)
    datetime = Column(DateTime)

    def __repr__(self):
        return f"<Check_in(id={self.id})>"


# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5004, debug=True)