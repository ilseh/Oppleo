print("Oppleo user utility")

from nl.oppleo.models.Base import Base
from nl.oppleo.models.User import User
from werkzeug.security import generate_password_hash

print(" Create Oppleo Administrator user account(s). To access the database the database url configured in ")
print(" the oppleo.ini config file is used.")

vu = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
vp = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890@#$%^&*()_{}[]'

def valid(s, v):
    if s is None:
        return False
    for cs in s:
        valid = False
        for cv in v:
            if cs == cv:
                valid = True
                break
        if not valid:
            return False
    return True


try:
    create = input("Remove all existing accounts? [Y/n] ")
    if create.upper() in ['Y', 'YES']:
        print(' Deleting all users... ', end='')
        User.delete_all()
        print(" deleted!")

    creatingUserAccounts = True
    while creatingUserAccounts:
        print('Create new user')
        username = ''
        while len(username) < 1 or not valid(username, vu):
            username = input(" Username: ")
            if len(username) == 0:
                print("Username cannot be empty")
            if not valid(username, vu):
                print("Username can only contain '{}'".format(vu))

        password = None
        while password is None or not valid(password, vp):
            password = input(" Password: ")
            if not valid(password, vu):
                print("Password can only contain '{}'".format(vp))
            if len(password) == 0:
                print("Are you sure you want an empty password? [Y/n]")
                confirmEmptyPw = input()
                if confirmEmptyPw not in ['y', 'Y']:
                    password = None

        print("Creating user '{}'... ".format(username), end='')
        user = User()
        user.username = username
        user.password = generate_password_hash(password)
        user.is_active = False
        user.save()
        print(" created!")

        again = input("Create another user account? [Y/n] ")
        creatingUserAccounts = again.upper() in ['Y', 'YES']

    print("Done")


except KeyboardInterrupt:
    print('Done')
    exit(0)

