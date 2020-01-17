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

        print('Resetting users. Delete all existing? (y/n):')
        create = input()
        if create == 'n':
            print('Stopping. No changes made.')
            return
        # Delete all users
        User.query.delete()

        user = User(
            username='admin', 
            password=generate_password_hash('admin'))
        db.session.add(user)
        db.session.commit()
        print('Default admin user with admin password created.')


if __name__ == '__main__':
    sys.exit(main())