print("Oppleo user utility")

from nl.oppleo.models.Base import Base
from nl.oppleo.models.User import User
from werkzeug.security import generate_password_hash

print(" Remove 2FA from a user account(s). To access the database the database url configured in ")
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

users = User.all()
print(" There are {} users in the database.".format(len(users)))

for user in users:
    print(" User: {}  2FA: {}  Local enforced: {}".format(user.username, "Enabled" if user.enabled_2fa else "Disabled", "Enabled" if user.enforce_local_2fa else "Disabled"))

try:
    username = input("Username to remove 2FA from: ")
    user = User.get(username)
    if user is None:
        print(" User with username {} not found.".format(username))
        print("Done")
        exit()

    if not user.has_enabled_2FA():
        print(" User with username {} does not have 2FA enabled.".format(username))
        print("Done")
        exit()

    user.enabled_2fa = False
    user.save()
    print(" 2FA disabled for User with username {}.".format(username))
    print("Done")

except KeyboardInterrupt:
    print('Done')
    exit(0)

