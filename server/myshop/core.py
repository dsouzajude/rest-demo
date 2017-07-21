from passlib.hash import sha256_crypt
from datetime import datetime

import utils, backend, errors


class Controller(object):

    def __init__(self, db_url, session_expiry_time=86400):
        self.backend = backend.MyshopBackend(db_url)
        self.backend.bootstrap()
        self.session_expiry_time_seconds = session_expiry_time

    def reset_backend(self):
        self.backend.reset()

    def ping(self):
        self.backend.ping()

    def register_user(self, username, password, full_name):
        """ Registers a user into the system.
        The registration does not save the actual password but the hashed
        password of the user for security purposes.
        """
        hashed_password = sha256_crypt.hash(password)
        user = self.backend.create_user(username, hashed_password, full_name)
        return user

    def authenticate(self, username, password):
        """ Authenticates the user and upon successful authentication creates
        a new session and returns the session token.

        Authentication is done by verifying the password with it's hash.
        """
        # Authenticate
        user = self.backend.get_user(username)
        if not user:
            raise errors.Unauthorized()

        is_success = sha256_crypt.verify(password, user.hashed_password)
        session_token = utils.generate_uuid() if is_success else None

        # Record the login attempt
        self.backend.insert_login_attempt(username, session_token)
        if not is_success:
            raise errors.InvalidLogin()

        # Create the session on successful login
        self.backend.create_session(session_token, username)
        return session_token

    def validate_session(self, session_token):
        """ Validates the session, raises an exception if either the
        session token does not exists or has expired.

        Upon successful validation, returns the username connected with
        the session.
        """
        # Check if session exists
        session = self.backend.get_session(session_token)
        if not session:
            raise errors.Unauthorized()

        # Check expiry
        now = datetime.utcnow()
        session_duration = (now - session.create_time).seconds
        if session_duration > self.session_expiry_time_seconds:
            raise errors.SessionExpired()

        return session.username

    def get_successful_logins(self, username, max_records=5):
        """ Gets the recent most successful logins """
        user_logins = self.backend.get_successful_logins(username, max_records)
        return user_logins
