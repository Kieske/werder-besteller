from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from forms import LoginForm, OrderForm, UserForm, GameForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dein_geheimer_schluessel'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///werder.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opponent = db.Column(db.String(150))
    date = db.Column(db.String(20))
    deadline = db.Column(db.String(20), nullable=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    amount = db.Column(db.Integer)
    comment = db.Column(db.String(300))
    user = db.relationship('User')
    game = db.relationship('Game')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routen (Login, Dashboard, Order, Admin)
# (Hier kommen die Routen rein, ich kann die bei Bedarf auch komplett schreiben)

if __name__ == '__main__':
    app.run(debug=True)
