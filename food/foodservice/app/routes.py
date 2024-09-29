from flask import Blueprint,Flask, render_template,request,redirect, url_for
import sys
from flask import jsonify
sys.path.append('/home/jose/Desktop/ADint/project')



list_routes = Blueprint('list_routes', __name__)

# Define routes for managing restaurants
@list_routes.route('/')
def list_restaurants():
    from config import Restaurantes, session
    restaurantes = session.query(Restaurantes).all() 

    
    return render_template("index.html", restaurantes=restaurantes)
    
@list_routes.route('/<int:restaurant_id>/Menu')
def view_menu(restaurant_id):
    from config import Restaurantes, Menu, session

    
    restaurante = session.query(Restaurantes).get(restaurant_id)

    if restaurante:
        
        menu_items = restaurante.menu
        print("Menu Items:", menu_items)
        return render_template("restaurant.html", restaurante=restaurante, menu_items=menu_items)
    else:
        
        return "Restaurant not found."

@list_routes.route('/API/<int:restaurant_id>/Menu')
def view_menu_API(restaurant_id):
    from config import Restaurantes, Menu, session

    restaurante = session.query(Restaurantes).get(restaurant_id)

    if restaurante:
        menu_items = [{'name': item.Pratos} for item in restaurante.menu]
        return jsonify({
            "restaurant_name": restaurante.Nome,
            "menu": menu_items
        })
    else:
        return jsonify({"error": "Restaurant not found."}), 404


@list_routes.route('/<int:restaurant_id>/Evaluate', methods=['GET', 'POST'])
def evaluate_restaurant(restaurant_id):
    from config import  session, Evaluation,Restaurantes
    restaurante = session.query(Restaurantes).get(restaurant_id)
    menu_items = restaurante.menu
    if request.method == 'POST':
        evaluation_text = request.form['evaluation']

        # Create a new evaluation instance and associate it with the restaurant
        new_evaluation = Evaluation(text=evaluation_text, restaurant_id=restaurant_id)
        session.add(new_evaluation)
        session.commit()

        # Redirect to another page or return a response as needed
        return redirect(url_for('list_routes.list_restaurants'))

    return render_template("menu.html", restaurante=restaurante, menu_items= menu_items)

@list_routes.route('/API/<int:restaurant_id>/Evaluate', methods=['POST'])
def evaluate_restaurant_API(restaurant_id):
    from config import  session, Evaluation, Restaurantes
    
    
    
    data = request.get_json()    
    print(data)
    evaluation_text = data['evaluation'] 
    print(evaluation_text)  
         

    new_evaluation = Evaluation(text=evaluation_text, restaurant_id=restaurant_id)
    session.add(new_evaluation)
    session.commit()

    return jsonify({"message": "Evaluation submitted successfully!"})