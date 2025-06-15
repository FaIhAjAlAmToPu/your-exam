from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

class PasswordManager:
    def __init__(self):
        self.password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))

    def verify_and_update(self, plain_password, hashed_password):
        return self.password_hash.verify_and_update(plain_password, hashed_password)

    def verify(self, plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)

    def hash(self, password):
        return self.password_hash.hash(password)

password_manager = PasswordManager()