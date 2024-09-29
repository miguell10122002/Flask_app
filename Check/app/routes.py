from flask import Blueprint,Flask, render_template,request,redirect, url_for
import sys
from flask import jsonify
sys.path.append('/home/jose/Desktop/ADint/project')



routes_check = Blueprint('routes_check', __name__)

# Define routes for managing restaurants
@routes_check.route('/')
def main_page():
    
    
    return render_template("index.html")

@routes_check.route('/checkin', methods=['GET', 'POST'])
def check_in():
    from config import Check_in, session, datetime

    if request.method == 'POST':
        username = request.form['username']
        space = request.form['space']
        
        new_checkin = Check_in(username=username, space=space, datetime=datetime.utcnow())
        
        session.add(new_checkin)
        session.commit()

    return render_template("checkin.html")

@routes_check.route('/API/checkIn', methods=['GET', 'POST'])
def check_in_API():
    from config import Check_in, session, datetime

    if request.method == 'POST':
        data = request.get_json()    
        username = data['username']    
        space = data['space']
        action= data['action'] 
        course_id= data['course_id']
        new_checkin = Check_in(username=username, space=space,action=action,course_id=course_id ,datetime=datetime.utcnow())
        session.add(new_checkin)
        session.commit()

        return jsonify({"message": "Check-in successful"})  # Sending a JSON response back

    # If it's not a POST, you can add logic for GET or just return something by default
    return jsonify({"message": "This is a GET request or something else."})



@routes_check.route('/checkout', methods=['GET', 'POST'])
def check_out():
    
    from config import Check_out, session, datetime

    if request.method == 'POST':
        username = request.form['username']
        space = request.form['space']
        
        new_checkout = Check_out(username=username, space=space, datetime=datetime.utcnow())
        
        session.add(new_checkout)
        session.commit()

    return render_template("checkout.html")
    

@routes_check.route('/API/checkOut', methods=['GET', 'POST'])
def check_out_API():
    
    from config import Check_out, session, datetime

    if request.method == 'POST':
        data = request.get_json()    
        username = data['username']    
        space = data['space']
        new_checkout = Check_out(username=username, space=space, datetime=datetime.utcnow())
        session.add(new_checkout)
        session.commit()

        return jsonify({"message": "Check-in successful"})  # Sending a JSON response back

    # If it's not a POST, you can add logic for GET or just return something by default
    return jsonify({"message": "This is a GET request or something else."})
    
@routes_check.route('/checklist', methods=['GET', 'POST'])
def check_list():
    from config import session, Check_in, Check_out
    if request.method == 'POST':
        username = request.form['username']
        
        check_ins = session.query(Check_in).filter_by(username=username).all()
        check_outs = session.query(Check_out).filter_by(username=username).all()
        

        return render_template("checklist.html", check_ins=check_ins, check_outs=check_outs)

    check_ins = session.query(Check_in).all()
    check_outs = session.query(Check_out).all()
    
    return render_template("checklist.html", check_ins=check_ins, check_outs=check_outs)


@routes_check.route('/API/users/<roomID>/list', methods=['GET'])
def user_list(roomID):
    from config import session, Check_in, Check_out
    room_id = roomID

    # Query the most recent check-in and check-out records for the specified room_id
    check_ins = (
        session.query(Check_in)
        .filter_by(space=room_id)
        .all()
    )
    check_outs = (
        session.query(Check_out)
        .filter_by(space=room_id)
        .all()
    )

    # Extract usernames from check-in and check-out records
    check_in_usernames = [check_in.username for check_in in check_ins]
    check_out_usernames = [check_out.username for check_out in check_outs]

    # See if the user is still on the room
    # List to store usernames that have not checked out
    roomUsernames = []

    for user in check_in_usernames:
        if user in check_out_usernames:
            lastCheckIn = (session.query(Check_in).filter_by(
                username=user).order_by(Check_in.datetime.desc()).first())
            lastCheckOut = (session.query(Check_out).filter_by(
                username=user).order_by(Check_out.datetime.desc()).first())
            if lastCheckIn and lastCheckOut:
                if lastCheckIn.datetime > lastCheckOut.datetime:
                    if user not in roomUsernames:
                        roomUsernames.append(user)
        else:
            if user not in roomUsernames:
                roomUsernames.append(user)

    

    data = {
        'usernames': roomUsernames
        
    }

    return jsonify(data)