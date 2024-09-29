from flask import Flask
from app.routes import list_routes
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from flask import Flask, render_template, request, send_from_directory, redirect, jsonify
import os
from os.path import exists
import datetime
from os import path
from flask_xmlrpcre.xmlrpcre import *


app = Flask(__name__, template_folder='app/templates')

# Register the imported routes
app.register_blueprint(list_routes, url_prefix='/')


handler = XMLRPCHandler('api')
handler.connect(app, '/api')


@handler.register
def create_restaurante(restaurant_data):
    nome = restaurant_data['nome']
    id = restaurant_data['id']
    new_restaurante = Restaurantes(Nome=nome, id=id)
    session.add(new_restaurante)
    session.commit()

    return "Restaurant added successfully!"


@handler.register
def create_menu(restaurant_id, menu_data):
    prato = menu_data['prato']

    try:

        restaurant = session.query(Restaurantes).filter_by(
            id=restaurant_id).first()

        if restaurant:

            new_prato = Menu(Pratos=prato, restaurante_id=restaurant_id)
            session.add(new_prato)
            session.commit()
            return "Menu item added to the restaurant successfully!"
        else:
            return "Restaurant not found."

    except Exception as e:
        return str(e)


@handler.register
def list_restaurants():
    try:
        restaurants = session.query(Restaurantes).all()
        restaurant_list = [(restaurant.id, restaurant.Nome)
                           for restaurant in restaurants]
        return restaurant_list
    except Exception as e:
        return str(e)


@handler.register
def list_evaluations(restaurant_id):
    try:
        evaluations = session.query(Evaluation).filter_by(
            restaurant_id=restaurant_id).all()
        evaluation_list = [evaluation.text for evaluation in evaluations]
        return evaluation_list
    except Exception as e:
        return str(e)


# SLQ access layer initialization
DATABASE_FILE = "database.sqlite"
db_exists = False

if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s' % (DATABASE_FILE),
                       echo=True)  # echo = True shows all SQL calls

Base = declarative_base()

# Declaration of data


class Restaurantes(Base):
    __tablename__ = 'restaurante'
    id = Column(Integer, primary_key=True)
    Nome = Column(String)
    menu = relationship("Menu", backref="restaurant")

    def __repr__(self):
        return f"<Restaurant(id={self.id}, Nome={self.Nome})>"


class Menu(Base):
    __tablename__ = 'menu'
    id = Column(Integer, primary_key=True, autoincrement=True)
    Pratos = Column(String)
    restaurante_id = Column(Integer, ForeignKey('restaurante.id'))

    def __repr__(self):
        return f"<Menu(id={self.id}, Pratos={self.Pratos})>"


class Evaluation(Base):
    __tablename__ = 'evaluation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String)  # Store the evaluation text
    # Store the evaluation date
    date = Column(DateTime, default=datetime.datetime.utcnow)
    # Foreign key to link evaluations to a restaurant
    restaurant_id = Column(Integer, ForeignKey('restaurante.id'))

    def __repr__(self):
        return f"<Evaluation(id={self.id}, text={self.text}, date={self.date})>"


# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session to interact with the database

Session = sessionmaker(bind=engine)
session = Session()


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5003, debug=True)
