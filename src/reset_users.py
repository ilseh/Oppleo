"""Create a new admin user """
print('Reset user utility')
from getpass import getpass
import sys

from flask import current_app
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.models.Base import DbSession
from nl.oppleo.models.User import User
#from nl.oppleo.webapp.WebApp import app, User
from werkzeug.security import generate_password_hash, check_password_hash

OppleoSystemConfig.loadConfig()

def main():
    
    """Main entry point for script."""

    db_session = DbSession()

    print('Resetting users to default admin/admin. Delete all existing? (y/n):')
    try:
        create = input()
    except KeyboardInterrupt:
        print('Stopping. No changes made.')
        return
    if create != 'y' and create != 'Y':
        print('Stopping. No changes made.')
        return
    # Delete all users
    User.delete_all()

    user = User(
        username='admin', 
        password=generate_password_hash('admin'))
    db_session.add(user)
    db_session.commit()
    print('Default admin user with admin password created.')
    DbSession.remove()

if __name__ == '__main__':
    # sys.exit(main())
    main()
    