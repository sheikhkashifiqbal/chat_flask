from flask import session, redirect, url_for, render_template, request,jsonify
from passlib.hash import pbkdf2_sha256
from . import main
import uuid
import pymongo
from .forms import LoginForm
from .events import ausers, allmessages
from .signup import SignupForm

# Database
client = pymongo.MongoClient('localhost', 27017)
db = client.users

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Create the user object
        user = {
            "_id": uuid.uuid4().hex,
            "username": request.form.get('username'),
            "fname": request.form.get('fname'),
            "lname": request.form.get('lname'),
            "email": request.form.get('email'),
            "password": request.form.get('password')
        }
    else:
        return render_template('signup.html', form=form)

    # Encrypt the password
    user['password'] = pbkdf2_sha256.encrypt(user['password'])

    # Check for existing email address
    if db.users.find_one({ "email": user['email'] }):
      return render_template('signup.html', form=form,already_cr="Email address already in use.")
    if db.users.find_one({ "username": user['username'] }):
      return render_template('signup.html', form=form,already_cr="UserName already in use.")

    if db.users.insert_one(user):
      #form = LoginForm()
      return redirect(url_for('.home'))
      #return render_template('index.html', form=form,user_cr="Signup Successfully")

    return jsonify({ "error": "Signup failed" }), 400

@main.route('/', methods=['GET', 'POST'])
def index():
    """Login form to enter a room."""
    user = db.users.find_one({
       "username": request.form.get('username')
    })

    form = LoginForm()
    if form.validate_on_submit():
        if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            session['name'] = form.username.data
            session['room'] = "chatroom"

            return redirect(url_for('.chat'))
        else:
            return render_template('index.html', form=form, wrong_cr="username or password invalid")

    elif request.method == 'GET':
        form.username.data = session.get('name', '')

    return render_template('index.html', form=form)


@main.route('/chat')
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('chat.html', name=name, room=room, active_list=ausers, msg = allmessages)

@main.route('/home')
def home():
    form = LoginForm()
    return render_template('index.html', form=form, user_cr="User Created Successfully.")
