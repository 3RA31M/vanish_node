from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit
from datetime import datetime
import random
import string
import os 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
socketio = SocketIO(app)
active_rooms = set()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    room = request.args.get('room')

    if not room:
        return "Room code missing", 400

    if room not in active_rooms:
        return "Invalid or expired room", 404

    return render_template('chat.html', room=room)


def generate_username():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"node_0x{suffix}"

@socketio.on('join')
def handle_join(data):
    room = data.get('room')
    if not room:
        return

    # register room on first join
    active_rooms.add(room)

    username = generate_username()
    join_room(room)

    emit('user_joined', {'username': username}, room=room)
    emit('assign_username', {'username': username}, to=request.sid)

@app.route('/create-room')
def create_room():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    active_rooms.add(code)
    return {"room": code}

@socketio.on('send_message')
def handle_message(data):
    room = data.get('room')
    username = data.get('username')
    message = data.get('message')
    if not all([room, username, message]):
        return

    emit('receive_message', {
        'username': username,
        'message': message,
    }, room=room)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Running on port {port}...")  # Add this debug log
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
