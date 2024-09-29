from flask import Blueprint, render_template, request, jsonify
import sys


routes_message = Blueprint('routes_message', __name__)


@routes_message.route('/')
def main_page():

    return render_template("index.html")


@routes_message.route('/sendmessage', methods=['GET', 'POST'])
def send_message():
    from config import Message, session, datetime

    if request.method == 'POST':
        send_username = request.form['send_user']
        receive_user = request.form['receive_user']
        content = request.form['content']

        new_message = Message(send_username=send_username, receive_username=receive_user,
                              content=content, datetime=datetime.utcnow())

        session.add(new_message)
        session.commit()

    return render_template("sendmessage.html")


@routes_message.route('/messagelist', methods=['GET', 'POST'])
def check_list():
    from config import Message, session
    if request.method == 'POST':
        send_username = request.form['send_username']

        messages_sent = session.query(Message).filter_by(
            send_username=send_username).order_by(Message.datetime.desc()).all()

        return render_template("Messagelist.html", messages_sent=messages_sent)

    messages_sent = session.query(Message).order_by(
        Message.datetime.desc()).all()

    return render_template("Messagelist.html", messages_sent=messages_sent)


@routes_message.route('/messagesreceived', methods=['GET', 'POST'])
def received_list():
    from config import Message, session
    if request.method == 'POST':

        receive_username = request.form['receive_username']

        messages_sent = session.query(Message).filter_by(
            receive_username=receive_username).order_by(Message.datetime.desc()).all()

        return render_template("receivelist.html", messages_sent=messages_sent)

    messages_sent = session.query(Message).order_by(
        Message.datetime.desc()).all()

    return render_template("receivelist.html", messages_sent=messages_sent)

# API routes


@routes_message.route('/API/messages/<id>/list', methods=['GET'])
def check_list_API(id):
    from config import Message, session
    receiver_id = id

    # Query messages received by the receiver
    messages_received = (
        session.query(Message)
        .filter_by(receive_username=receiver_id)
        .order_by(Message.datetime.desc())
        .all()
    )
    

    # Initialize lists to store message information
    sender_usernames = []
    datetimes = []
    contents = []

    # Extract information from the messages and populate the lists
    for message in messages_received:
        sender_usernames.append(message.send_username)
        datetimes.append(message.datetime.strftime("%Y-%m-%d %H:%M:%S"))
        contents.append(message.content)

    # Create a list of dictionaries to store message data
    messages_data = []
    for i in range(len(messages_received)):
        message_data = {
            "sender_username": sender_usernames[i],
            "datetime": datetimes[i],
            "content": contents[i],
        }
        messages_data.append(message_data)
    
    

    # Convert the list of message data to JSON
    messages_json = jsonify(messages_data)

    return messages_json


@routes_message.route('/API/sendmessage', methods=['POST'])
def send_message_API():
    from config import Message, session, datetime

    # Get the JSON data from the request
    data = request.get_json()

    if data:
        send_username = data.get('send_username')
        receive_username = data.get('receive_username')
        content = data.get('content')

        if send_username and receive_username and content:
            # Create a new Message object and add it to the database
            new_message = Message(
                send_username=send_username,
                receive_username=receive_username,
                content=content,
                datetime=datetime.utcnow()
            )

            session.add(new_message)
            session.commit()

            return jsonify({"message": "Message sent successfully"})
        else:
            return jsonify({"error": "Incomplete data"})
    else:
        return jsonify({"error": "Invalid JSON data"})
