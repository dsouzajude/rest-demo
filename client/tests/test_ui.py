import os
from os.path import join, dirname
from mock import patch
import nose.tools as nt
from webtest import TestApp

from myshop_ui import server


class TestServer(object):

    def setup(self):
        self.test_username = "jude"
        self.test_password = "jude123"
        templates_dir = join(dirname(__file__), '../templates')
        app = server.create_app("", templates_dir, "")
        self.app = TestApp(app)

    def test_index_view(self):
        resp = self.app.get('/')
        nt.assert_equals(resp.status_int, 200)

    def test_registration_view(self):
        resp = self.app.get('/register')
        nt.assert_equals(resp.status_int, 200)

    @patch('myshop_ui.requestor._make_request')
    def test_user_registers_successfully(self, request_mock):
        resp = self.app.post('/register')
        nt.assert_equals(resp.status_int, 302)

    def test_login_view(self):
        resp = self.app.get('/login')
        nt.assert_equals(resp.status_int, 200)

    @patch('myshop_ui.requestor._make_request')
    @patch('myshop_ui.server.json')
    @patch('myshop_ui.server.response')
    def test_user_logins_successfully(self, resp_mock, json_mock, req_mock):
        resp = self.app.post('/login')
        nt.assert_equals(resp.status_int, 302)

    @patch('myshop_ui.requestor._make_request')
    @patch('myshop_ui.server.json')
    @patch('myshop_ui.server.request')
    def test_welcome_view(self, sreq_mock, json_mock, rreq_mock):
        resp = self.app.get('/welcome')
        nt.assert_equals(resp.status_int, 200)
