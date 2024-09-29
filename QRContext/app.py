import os
import secrets
from urllib.parse import urlencode
from flask import jsonify
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, render_template, flash, session, \
    current_app, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, \
    current_user, login_required
import requests
import logging
import json

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH2_PROVIDERS'] = {

    'fenix': {
        'client_id': os.environ.get('FENIX_CLIENT_ID'),
        'client_secret': os.environ.get('FENIX_CLIENT_SECRET'),
        'authorize_url': 'https://fenix.tecnico.ulisboa.pt/oauth/userdialog',
        'token_url': 'https://fenix.tecnico.ulisboa.pt/oauth/access_token',
        'userinfo': {
            'url': 'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person',
            'email': lambda json: json['email'],
        },
        'scopes': ['Curricular', 'Horário', 'Avaliações', 'Informação', 'Pagamentos', 'Gestão de Delegados', 'Assiduidade', 'Gestão planos curriculares de alunos', 'Aluno (Leitura)', 'Avaliações (Leitura)', 'Pessoal (Leitura)', 'Avaliações (Escrita)', 'Professor (Leitura)'],

    }
}
app.add_url_rule('/static/<path:filename>',
                 endpoint='custom_static', view_func=app.send_static_file)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'index'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    token = db.Column(db.String(300))
    course_ids = db.Column(db.String)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/main_screen')
@login_required
def main_screen():
    return render_template("main_screen.html")


@app.route('/messages')
@login_required
def messagesSCREEN():
    room = request.args.get('room')
    print(room)
    return render_template("messages.html", room_id=room, user=current_user.id)


@app.route('/authorize/<provider>')
def oauth2_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main_screen'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # generate a random string for the state parameter
    session['oauth2_state'] = secrets.token_urlsafe(16)

    # create a query string with all the OAuth2 parameters
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('oauth2_callback', provider=provider,
                                _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    # redirect the user to the OAuth2 provider authorization URL
    return redirect(provider_data['authorize_url'] + '?' + qs)


@app.route('/callback/<provider>')
def oauth2_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # if there was an authentication error, flash the error messages and exit
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('index'))

    # make sure that the state parameter matches the one we created in the
    # authorization request
    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    # make sure that the authorization code is present
    if 'code' not in request.args:
        abort(401)

    # exchange the authorization code for an access token
    response = requests.post(provider_data['token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('oauth2_callback', provider=provider,
                                _external=True),
    }, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    print(oauth2_token)
    if not oauth2_token:
        abort(401)

    # use the access token to get the user's email address
    response = requests.get(provider_data['userinfo']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })
    if response.status_code != 200:
        abort(401)
    email = provider_data['userinfo']['email'](response.json())

    # find or create the user in the database
    user = db.session.scalar(db.select(User).where(User.email == email))
    if user is None:
        user = User(email=email, username=email.split(
            '@')[0], token=oauth2_token)
        db.session.add(user)
        db.session.commit()

    # log the user in
    login_user(user)
    return redirect(url_for('main_screen'))


@app.route('/other')
@login_required  # Require authentication for this route
def other_route():
    academic_term = "2023/2024"  # Replace with the desired academic term

    try:
        url = f"https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person/courses?academicTerm={academic_term}"
        response = requests.get(url, headers={
            'Authorization': 'Bearer ' + current_user.token,
            'Accept': 'application/json',
        })

        if response.status_code != 200:
            abort(401, "Not authorized")

        course_info = response.json()

        # Extract course IDs from enrolments
        course_ids = [enrollment['id']
                      for enrollment in course_info.get('enrolments', [])]

        # Convert course_ids list to a JSON string
        course_ids_json = json.dumps(course_ids)

        # Store the course IDs in the user's model as a JSON string
        current_user.course_ids = course_ids_json
        db.session.commit()

        print("Course IDs:", course_ids)  # Debugging: Print course IDs
        return jsonify(course_ids)  # Return the list of course IDs as JSON
    except Exception as e:
        print("Error:", str(e))  # Debugging: Print the error
        abort(401, "Not logged in or an error occurred: " + str(e))

# ROOMS API


@app.route('/API/rooms/<room_id>/schedule', methods=['GET'])
def get_room_schedule(room_id):
    try:
        response = requests.get(
            f"http://127.0.0.1:5002/API/{room_id}/schedule")
        if response.status_code != 200:
            return render_template('500.html'), 500

        data = response.json()

        return jsonify(data)

    except Exception as e:
        if e.__class__ == requests.exceptions.ConnectionError:
            return render_template('503.html'), 503
        else:
            return render_template('500.html'), 500


# FOOD API

@app.route('/API/restaurant/<restaurant_id>/Menu', methods=['GET'])
def get_restaurant_menu(restaurant_id):
    try:
        response = requests.get(
            f"http://127.0.0.1:5003/API/{restaurant_id}/Menu")
        if response.status_code != 200:
            return render_template('500.html'), 500

        data = response.json()

        return jsonify(data)

    except Exception as e:
        if e.__class__ == requests.exceptions.ConnectionError:
            return render_template('503.html'), 503
        else:
            return render_template('500.html'), 500


@app.route('/API/restaurant/<restaurant_id>/evaluation', methods=['POST'])
def evaluate_restaurant(restaurant_id):
    try:
        # Get the evaluation text from the request body
        evaluation_text = request.json.get('evaluation')
        data_to_send = {
            'evaluation': evaluation_text,

        }
        print(data_to_send)
        # Send POST request to Restaurant API
        response = requests.post(
            f"http://127.0.0.1:5003/API/{restaurant_id}/Evaluate", json=data_to_send)
        if response.status_code != 200:
            return jsonify({"error": "Evaluation submission failed!"}), 500

        return jsonify({"message": "Evaluation submitted successfully!"})

    except Exception as e:
        print(f"Error parsing JSON data: {str(e)}")
        if e.__class__ == requests.exceptions.ConnectionError:
            return render_template('503.html'), 503
        else:
            return render_template('500.html'), 500


# Check API
@app.route('/API/checkIn', methods=['POST'])
def check_in():
    try:
        check_in_data = request.json

        userId = check_in_data.get('userId')
        space = check_in_data.get('space')
        action = check_in_data.get('action')
        course_id = check_in_data.get('course_id')

        print(f'User ID: {userId}, Space: {space}',  action,  course_id)

        # Post the data to the other Flask route
        data_to_send = {
            'username': userId,
            'space': space,
            'action': action,
            'course_id': course_id,
        }

        response = requests.post(
            'http://127.0.0.1:5004/API/checkIn', json=data_to_send)

        if response.status_code == 200:
            response_data = {'message': 'Check-in successful'}
            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Check-in failed'}), 500

    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500


@app.route('/API/checkOut', methods=['POST'])
def check_out():
    try:
        check_out_data = request.json

        userId = check_out_data.get('userId')
        space = check_out_data.get('space')

        print(f'User ID: {userId}, Space: {space}')

        # Post the data to the other Flask route
        data_to_send = {
            'username': userId,
            'space': space,
        }

        response = requests.post(
            'http://127.0.0.1:5004/API/checkOut', json=data_to_send)

        if response.status_code == 200:
            response_data = {'message': 'Check-out successful'}
            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Check-out failed'}), 500

    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500


@app.route('/API/users/<roomID>/list', methods=['GET', 'POST'])
def users(roomID):
    try:
        response = requests.get(
            f"http://127.0.0.1:5004/API/users/{roomID}/list")
        if response.status_code == 500:
            return render_template('500.html'), 500
        elif response.status_code == 404:
            return jsonify({"message": "No messages found"})

        data = response.json()

        return jsonify(data)

    except Exception as e:
        if e._class_ == requests.exceptions.ConnectionError:
            return render_template('503.html'), 503
        else:
            return render_template('500.html'), 500

# Message API


@app.route('/API/messages/<myUsername>/list', methods=['GET', 'POST'])
def messages(myUsername):
    try:
        response = requests.get(
            f"http://127.0.0.1:5005/API/messages/{myUsername}/list")
        if response.status_code == 500:
            return render_template('500.html'), 500
        elif response.status_code == 404:
            return jsonify({"message": "No messages found"})

        data = response.json()

        return jsonify(data)
    except Exception as e:
        if e._class == requests.exceptions.ConnectionError:
            return render_template('503.html'), 503
        else:
            return render_template('500.html'), 500


@app.route('/API/sendmessage', methods=['POST'])
def sendMessage():
    try:
        message_data = request.json

        sender = message_data.get('send_username')
        receiver = message_data.get('receive_username')
        message = message_data.get('content')

        # Post the data to the other Flask route
        data_to_send = {

            'send_username': sender,
            'receive_username': receiver,
            'content': message
        }

        response = requests.post(
            'http://127.0.0.1:5005/API/sendmessage', json=data_to_send)

        if response.status_code == 200:
            response_data = {'message': 'Message successful'}
            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Message failed'}), 500

    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
