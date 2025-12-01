from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask_socketio import SocketIO, emit, join_room, leave_room
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Track online users
online_users = set()
user_rooms = {}

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    company = db.Column(db.String(100))
    position = db.Column(db.String(100))
    memo = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

# ... (keep all your existing routes) ...

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    print('Client connected:', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    user = next((u for u, sid in user_rooms.items() if sid == request.sid), None)
    if user:
        online_users.discard(user)
        user_rooms.pop(user)
        emit('user_status', {'user': user, 'status': 'offline'}, broadcast=True)

@socketio.on('login')
def handle_login(data):
    username = data.get('username')
    if username:
        user_rooms[username] = request.sid
        online_users.add(username)
        emit('user_status', {'user': username, 'status': 'online'}, broadcast=True)
        emit('online_users', list(online_users), broadcast=True)

@socketio.on('send_message')
def handle_send_message(data):
    username = data.get('sender')
    message = data.get('message')
    if username and message:
        # Save message to database
        msg = Message(sender=username, content=message)
        db.session.add(msg)
        db.session.commit()
        
        # Broadcast the message to all clients
        emit('receive_message', {
            'sender': username,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, broadcast=True)

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    socketio.run(app, debug=True)