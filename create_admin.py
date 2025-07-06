from werder_besteller.models import db, User
from main import app  # Stelle sicher, dass hier `app` korrekt importiert ist

with app.app_context():
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", is_admin=True)
        admin.set_password("adminpass")
        db.session.add(admin)
        db.session.commit()
        print("Admin wurde erstellt.")
    else:
        print("Admin existiert bereits.")
