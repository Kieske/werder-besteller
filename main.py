# main.py
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werder_besteller.models import db, User, Game, Order
from werder_besteller.forms import LoginForm, OrderForm, GameForm, UserForm
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dein-geheimes-passwort'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///werder.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables_and_admin():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', is_admin=True)
        admin.set_password('adminpass')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Ungültiger Benutzername oder Passwort')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    games = Game.query.order_by(Game.date).all()
    orders = Order.query.all()
    return render_template('dashboard.html', games=games, orders=orders)

@app.route('/order/<int:game_id>', methods=['GET', 'POST'])
@login_required
def order(game_id):
    game = Game.query.get_or_404(game_id)
    form = OrderForm()
    if form.validate_on_submit():
        existing_order = Order.query.filter_by(user_id=current_user.id, game_id=game_id).first()
        if existing_order:
            existing_order.amount = form.amount.data
            existing_order.note = form.note.data
        else:
            order = Order(user_id=current_user.id, game_id=game_id,
                          amount=form.amount.data, note=form.note.data)
            db.session.add(order)
        db.session.commit()
        flash('Bestellung gespeichert.')
        return redirect(url_for('dashboard'))
    return render_template('order.html', form=form, game=game)

@app.route('/manage/games', methods=['GET', 'POST'])
@login_required
def manage_games():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    form = GameForm()
    if form.validate_on_submit():
        game = Game(opponent=form.opponent.data,
                    date=form.date.data,
                    deadline=form.deadline.data)
        db.session.add(game)
        db.session.commit()
        flash('Spiel hinzugefügt.')
        return redirect(url_for('manage_games'))
    games = Game.query.order_by(Game.date).all()
    return render_template('manage_games.html', form=form, games=games)

@app.route('/manage/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    form = UserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, is_admin=form.is_admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Benutzer erstellt.')
        return redirect(url_for('manage_users'))
    users = User.query.all()
    return render_template('manage_users.html', form=form, users=users)

if __name__ == '__main__':
    app.run(debug=True)
