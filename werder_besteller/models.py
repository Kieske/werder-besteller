from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///werder.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opponent = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    deadline = db.Column(db.Date, nullable=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='orders')
    game = db.relationship('Game', backref='orders')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', is_admin=True)
        admin.set_password('adminpass123')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
@login_required
def dashboard():
    games = Game.query.order_by(Game.date).all()
    orders = Order.query.all()
    return render_template('dashboard.html', games=games, orders=orders, current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    class LoginForm(FlaskForm):
        username = StringField('Benutzername', validators=[DataRequired()])
        password = PasswordField('Passwort', validators=[DataRequired()])
        submit = SubmitField('Login')

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Ungültige Anmeldedaten')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/order/<int:game_id>', methods=['GET', 'POST'])
@login_required
def order(game_id):
    class OrderForm(FlaskForm):
        amount = IntegerField('Anzahl Karten', validators=[DataRequired()])
        comment = TextAreaField('Bemerkung')
        submit = SubmitField('Speichern')

    game = Game.query.get_or_404(game_id)
    form = OrderForm()
    order = Order.query.filter_by(user_id=current_user.id, game_id=game_id).first()
    if request.method == 'GET' and order:
        form.amount.data = order.amount
        form.comment.data = order.comment
    if form.validate_on_submit():
        if not order:
            order = Order(user_id=current_user.id, game_id=game_id)
        order.amount = form.amount.data
        order.comment = form.comment.data
        db.session.add(order)
        db.session.commit()
        flash('Bestellung gespeichert')
        return redirect(url_for('dashboard'))
    return render_template('order.html', form=form, game=game)

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))

    class RegisterForm(FlaskForm):
        username = StringField('Benutzername', validators=[DataRequired(), Length(min=3)])
        password = PasswordField('Passwort', validators=[DataRequired(), Length(min=4)])
        submit = SubmitField('Hinzufügen')

    form = RegisterForm()
    users = User.query.all()
    if form.validate_on_submit():
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Benutzer hinzugefügt')
    return render_template('manage_users.html', users=users, form=form)

@app.route('/admin/games', methods=['GET', 'POST'])
@login_required
def manage_games():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))

    class GameForm(FlaskForm):
        opponent = StringField('Gegner', validators=[DataRequired()])
        date = DateField('Spieltermin', validators=[DataRequired()])
        deadline = DateField('Bestellfrist', format='%Y-%m-%d', validators=[])
        submit = SubmitField('Hinzufügen')

    form = GameForm()
    games = Game.query.order_by(Game.date).all()
    if form.validate_on_submit():
        new_game = Game(opponent=form.opponent.data, date=form.date.data, deadline=form.deadline.data)
        db.session.add(new_game)
        db.session.commit()
        flash('Spieltag hinzugefügt')
    return render_template('manage_games.html', games=games, form=form)

if __name__ == '__main__':
    app.run(debug=True)
