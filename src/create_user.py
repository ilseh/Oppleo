"""Create a new admin user """
from getpass import getpass
import sys

from flask import current_app
from nl.carcharging.webapp.WebApp import app, User, db
from werkzeug.security import generate_password_hash, check_password_hash

def main():
    """Main entry point for script."""
    with app.app_context():
        db.metadata.create_all(db.engine)
        if User.query.all():
            print('A user already exists! Create another? (y/n):')
            create = input()
            if create == 'n':
                return

        print('Enter username: ')
        username = input()
        password = getpass()
        assert password == getpass('Password (again):')

        user = User(
            username=username, 
            password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        print('User added.')


if __name__ == '__main__':
    sys.exit(main())