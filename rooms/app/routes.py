from flask import Blueprint,Flask, render_template,request,redirect, url_for
import sys
from flask import jsonify
sys.path.append('/home/jose/Desktop/ADint/project')



routes_rooms = Blueprint('routes_rooms', __name__)

# Define routes for managing restaurants
@routes_rooms.route('/')
def list_rooms():
    from config import Room, session
    rooms = session.query(Room).all() 
    print(rooms)

    
    return render_template("index.html", rooms=rooms)
    
@routes_rooms.route('/<room_id>/schedule', methods=['GET'])
def view_schedule(room_id):
    from config import Room, session
    room = session.query(Room).filter(Room.id == room_id).first()

    # Get all events
    events = room.event

    # Sort events by date and then by start time
    sorted_events = sorted(events, key=lambda x: (x.day, x.start))

    # Group events by date
    events_by_date = {}
    for event in sorted_events:
        date = event.day
        if date not in events_by_date:
            events_by_date[date] = []
        events_by_date[date].append(event)

    return render_template('rooms.html', room=room, events_by_date=events_by_date)

@routes_rooms.route('/API/<room_id>/schedule', methods=['GET'])
def view_schedule_API(room_id):
    from config import Room, session
    room = session.query(Room).filter(Room.id == room_id).first()

    if not room:
        # Room not found, returning an error response
        return jsonify({'error': 'Room not found'}), 404

    # Get all events
    events = room.event
    # If events is None or an empty list, return no events.
    if not events:
        return jsonify({
            'room_id': room_id,
            'room_name': room.name, 
            'events': {}
        })
    # Sort events by date and then by start time
    sorted_events = sorted(events, key=lambda x: (x.day, x.start))

    # Construct a JSON-serializable dictionary
    events_by_date = {}
    for event in sorted_events:
        date_str = event.day.isoformat() if hasattr(event.day, 'isoformat') else str(event.day)
        if date_str not in events_by_date:
            events_by_date[date_str] = []

        event_data = {
            'start': event.start.isoformat() if hasattr(event.start, 'isoformat') else str(event.start),
            # Include the end time and course_id if they exist in your model
            'end': event.end.isoformat() if hasattr(event.end, 'isoformat') else str(event.end),
            'course_id': event.course_id
        }
        events_by_date[date_str].append(event_data)

    return jsonify({
        'room_id': room_id,
        'room_name': room.name, 
        'events': events_by_date
    })
