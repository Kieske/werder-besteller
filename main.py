from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from werder_besteller.forms import LoginForm, OrderForm, UserForm, GameForm
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dein_geheimer_schluessel'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///werder.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Models (User, Game, Order) wie zuvor definiert

# ... Modelle hier einfügen (wie oben) ...


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Ungültiger Benutzername oder Passwort')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
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
    existing_order = Order.query.filter_by(user_id=current_user.id, game_id=game.id).first()
    if request.method == 'GET' and existing_order:
        form.amount.data = existing_order.amount
        form.comment.data = existing_order.comment

    if form.validate_on_submit():
        # Prüfe Frist
        if game.deadline:
            deadline_date = datetime.strptime(game.deadline, '%Y-%m-%d').date()
            if date.today() > deadline_date:
                flash('Bestellfrist für dieses Spiel ist abgelaufen.')
                return redirect(url_for('dashboard'))

        if existing_order:
            existing_order.amount = form.amount.data
            existing_order.comment = form.comment.data
        else:
            new_order = Order(user_id=current_user.id, game_id=game.id,
                              amount=form.amount.data, comment=form.comment.data)
            db.session.add(new_order)
        db.session.commit()
        flash('Bestellung gespeichert.')
        return redirect(url_for('dashboard'))

    return render_template('order.html', game=game, form=form)


@app.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Keine Berechtigung.')
        return redirect(url_for('dashboard'))

    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Benutzername existiert bereits.')
        else:
            new_user = User(username=form.username.data)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash('Benutzer angelegt.')
        return redirect(url_for('manage_users'))

    users = User.query.all()
    return render_template('manage_users.html', form=form, users=users)


@app.route('/manage_games', methods=['GET', 'POST'])
@login_required
def manage_games():
    if not current_user.is_admin:
        flash('Keine Berechtigung.')
        return redirect(url_for('dashboard'))

    form = GameForm()
    if form.validate_on_submit():
        new_game = Game(
            opponent=form.opponent.data,
            date=form.date.data,
            deadline=form.deadline.data if form.deadline.data else None
        )
        db.session.add(new_game)
        db.session.commit()
        flash('Spiel angelegt.')
        return redirect(url_for('manage_games'))

    games = Game.query.order_by(Game.date).all()
    return render_template('manage_games.html', form=form, games=games)


# --- Hilfsfunktion zum Versenden von Benachrichtigungen ---
def send_email(subject, body, recipients):
    sender = "deine.email@example.com"
    password = "dein_email_passwort"
    smtp_server = "smtp.example.com"
    smtp_port = 587

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())

# Beispiel: Du kannst eine Funktion implementieren, die die Fristen prüft und dann Mails versendet.

if __name__ == '__main__':
    app.run(debug=True)
