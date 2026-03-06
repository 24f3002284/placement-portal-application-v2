from flask import current_app as app
from .models import db
from flask_security import SQLAlchemyUserDatastore, hash_password

with app.app_context():
    db.create_all()

    datastore: SQLAlchemyUserDatastore = app.security.datastore

    # Create roles
    datastore.find_or_create_role(name="admin")
    datastore.find_or_create_role(name="company")
    datastore.find_or_create_role(name="student")

    # Create admin if not exists
    if not datastore.find_user(email="admin@placement.edu"):
        datastore.create_user(
            name="Admin",
            email="admin@placement.edu",
            password=hash_password("admin123"),
            roles=["admin"]
        )

    db.session.commit()
