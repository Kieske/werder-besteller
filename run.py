from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Game, Order
from forms import LoginForm, RegisterForm, OrderForm, GameForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///werder.db'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
