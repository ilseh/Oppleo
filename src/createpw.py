from werkzeug.security import generate_password_hash

print("Oppleo password utility")
print(" Creates the hash to be used in either the password field in the users table in the Oppleo database, or")
print(" in the on_db_failure_magic_password field in the oppleo.ini file in the Oppleo/src/nl/oppleo/config/ directory.")

password = None
try:
    password = input("Enter the password to hash: ")
except KeyboardInterrupt:
    print("Stopped")
    exit

print("Password hash:")
print(generate_password_hash(password))
print("This can be used in the password field in the users table in the Oppleo database, and in the on_db_failure_magic_password field in the oppleo.ini file in the Oppleo/src/nl/oppleo/config/ directory.")
