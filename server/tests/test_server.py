import os
from mock import patch
import nose.tools as nt
from webtest import TestApp

from myshop import core, server, utils, errors


class TestServer(object):

    def setup(self):
        db_url = 'sqlite:///./data/demo.db'
        self.test_username = "jude"
        self.test_password = "jude123"
        self.controller = core.Controller(db_url)
        self.controller.reset_backend()
        app = server.create_app(self.controller)
        self.app = TestApp(app)

    def teardown(self):
        self.controller.reset_backend()

    def _register_user(self, expect_errors=False):
        payload = {
            "username": self.test_username,
            "password": self.test_password,
            "full_name": self.test_username
        }
        return self.app.post_json('/register',
                                 payload,
                                 expect_errors=expect_errors)

    def _authenticate(self):
        payload = {
            "username": self.test_username,
            "password": self.test_password
        }
        return self.app.post_json('/auth', payload)

    def test_registers_user_successfully(self):
        resp = self._register_user()
        nt.assert_equals(resp.status_int, 200)

    def test_registers_fails_when_user_already_exists(self):
        self._register_user()
        resp = self._register_user(expect_errors=True)
        nt.assert_equals(resp.status_int, 409)
        nt.assert_equals(resp.json['code'], errors.UserExists.__name__)

    def test_registration_fails_for_missing_fields(self):
        payload = {
            "password": self.test_password
        }
        resp = self.app.post_json('/register', payload, expect_errors=True)
        nt.assert_equals(resp.status_int, 400)

    def test_authentication_is_successful(self):
        self._register_user()
        resp = self._authenticate()
        session_token = resp.json['session_token']
        nt.assert_not_equals(session_token, None)

    def test_authentication_fails_on_incorrect_password(self):
        self._register_user()
        payload = {
            "username": self.test_username,
            "password": "incorrect-password"
        }
        resp = self.app.post_json('/auth', payload, expect_errors=True)
        nt.assert_equals(resp.status_int, 401)
        nt.assert_equals(resp.json['code'], errors.InvalidLogin.__name__)

    def test_authentication_fails_when_user_does_not_exist(self):
        payload = {
            "username": "non-existent-user",
            "password": "non-existent-password"
        }
        resp = self.app.post_json('/auth', payload, expect_errors=True)
        nt.assert_equals(resp.status_int, 401)
        nt.assert_equals(resp.json['code'], errors.Unauthorized.__name__)

    def test_successfully_gets_login_attempts(self):
        self._register_user()
        resp = self._authenticate()
        session_token = resp.json['session_token']
        headers = {
            'Authorization': 'Session-token {}'.format(session_token)
        }
        resp = self.app.get('/logins', headers=headers)
        nt.assert_equals(resp.status_int, 200)
        logins = resp.json['logins']
        nt.assert_equals(len(logins), 1)

    def test_successfully_gets_multiple_login_attempts(self):
        self._register_user()
        attempts = 3
        resp = None
        for attempt in range(attempts):
            resp = self._authenticate()
        session_token = resp.json['session_token']
        headers = {
            'Authorization': 'Session-token {}'.format(session_token)
        }
        resp = self.app.get('/logins', headers=headers)
        nt.assert_equals(resp.status_int, 200)
        logins = resp.json['logins']
        nt.assert_equals(len(logins), attempts)

    def test_successfully_gets_only_successful_login_attemps(self):
        self._register_user()
        attempts = 3
        resp = None
        for attempt in range(attempts):
            if attempt == 0:
                # failed attempt with incorrect password
                payload = {
                    "username": self.test_username,
                    "password": "incorrect-password"
                }
                self.app.post_json('/auth', payload, expect_errors=True)
            else:
                resp = self._authenticate()

        session_token = resp.json['session_token']
        headers = {
            'Authorization': 'Session-token {}'.format(session_token)
        }
        resp = self.app.get('/logins', headers=headers)
        nt.assert_equals(resp.status_int, 200)
        logins = resp.json['logins']

        # Should return only the successful login attempts
        nt.assert_equals(len(logins), attempts-1)

    def test_getting_login_attempts_fails_on_session_expiry(self):
        self._register_user()
        self.controller.session_expiry_time_seconds = -1 # expire session sooner
        resp = self._authenticate()
        session_token = resp.json['session_token']
        headers = {
            'Authorization': 'Session-token {}'.format(session_token)
        }
        resp = self.app.get('/logins', headers=headers, expect_errors=True)
        nt.assert_equals(resp.status_int, 401)
        nt.assert_equals(resp.json['code'], errors.SessionExpired.__name__)
