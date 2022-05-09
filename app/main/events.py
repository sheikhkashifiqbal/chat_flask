from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio
import pymongo
import uuid
client = pymongo.MongoClient('localhost', 27017)
db = client.users
ausers = []
allmessages = []
@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    join_room(session.get('name'))
    is_found = False
    for i in range(len(ausers)):
       if ausers[i] == session.get('name'):
           is_found = True
    if is_found is False:
        ausers.append(session.get('name'))
    print(ausers)
    allmessages.clear()
    for x in db.chat.find({"username":session.get('name')}, {"_id": 0, "username": 1, "message": 1}):
        #allmessages = allmessages + x + "\n"
        allmessages.append(x['message'])

    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    umessage = {
        "_id": uuid.uuid4().hex,
        "username": session.get('name'),
        "message": ''
    }

    txt = message['msg']
    if "::" in txt:
        txt = txt.split("::")
        join_room(txt[0])
        emit('message', {'msg': session.get('name') + '->' + message['msg']}, room=txt[0])

        umessage['message'] = session.get('name') + '->' + message['msg']
        db.chat.insert_one(umessage)

        umessage = {
            "_id": uuid.uuid4().hex,
            "username": txt[0],
            "message": umessage['message']
        }
        db.chat.insert_one(umessage)
        leave_room(txt[0])
    else:
        room = session.get('room')
        emit('message', {'msg': session.get('name') + ':' + message['msg']}, room=room)
        umessage['message'] = session.get('name') + ':' + message['msg']
        for i in range(len(ausers)):
            umessage = {
                "_id": uuid.uuid4().hex,
                "username": ausers[i],
                "message": umessage['message']
            }
            db.chat.insert_one(umessage)

@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    ausers.remove(session.get('name'))
    print(ausers)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)