from flask import Flask
from app.routes import routes_rooms
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
import json

import os
from os.path import exists
import datetime
from os import path
from flask_xmlrpcre.xmlrpcre import *


app = Flask(__name__, template_folder='app/templates')

# Register the imported routes
app.register_blueprint(routes_rooms, url_prefix='/')


handler = XMLRPCHandler('api')
handler.connect(app, '/api')


@handler.register
def create_room(room_data):
    nome = room_data['name']
    id = room_data['id']
    new_room = Room(name=nome, id=id)
    session.add(new_room)
    session.commit()

    return "Room added successfully!"


@handler.register
def list_rooms():
    try:

        rooms = session.query(Room).all()
        room_list = [(room.id, room.name) for room in rooms]

        return room_list
    except Exception as e:
        return str(e)


@handler.register
def import_schedule_from_json(file_path):
    try:
        with open(file_path, 'r') as file:
            schedule_data = json.load(file)
        return schedule_data
    except FileNotFoundError:
        return None
    except Exception as e:
        return str(e)


@handler.register
def update_room_schedule(room_id, new_schedule):
    room = session.query(Room).filter(Room.id == room_id).first()

    if room is not None:
        for event in room.event:
            session.delete(event)

        for event_data in new_schedule.get('events', []):
            if 'course' in event_data:  # Check if the 'course' key exists in event_data
                new_event = Event(
                    start=event_data.get('start', ''),
                    end=event_data.get('end', ''),
                    day=event_data.get('day', ''),
                    course_id=event_data['course']['id'],
                    room_id=room_id
                )
                session.add(new_event)
        session.commit()
        return "Room schedule updated successfully!"
    else:
        return f"Room with ID {room_id} not found."


# SQL access layer initialization
DATABASE_FILE = "room_database.sqlite"
db_exists = False

if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s' % (DATABASE_FILE), echo=True)

Base = declarative_base()

# Declaration of data tables


class Room(Base):
    __tablename__ = 'room'
    id = Column(String, primary_key=True)
    name = Column(String)
    event = relationship("Event", backref="room")

    def __repr__(self):
        return f"<Room(id={self.id}, name={self.name})>"


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start = Column(String)
    end = Column(String)
    day = Column(String)
    course_id = Column(String)
    room_id = Column(String, ForeignKey('room.id'))

    def __repr__(self):
        return f"<Event(id={self.id},  start={self.start})>"


# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5002, debug=True)
