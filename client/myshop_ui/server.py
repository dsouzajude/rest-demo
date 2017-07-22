import os
import json
import traceback
from pkg_resources import Requirement, resource_filename

import requests
import bottle
from bottle import (
    Bottle,
    request,
    response,
    mako_view as view,
    mako_template as template,
    TEMPLATE_PATH,
    redirect,
    HTTPError,
    HTTPResponse
)

import requestor


def handle_errors(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (HTTPError, HTTPResponse):
            raise
        except Exception as e:
            print('exception caught by error handler',
                  type(e).__name__,
                  repr(e))
            traceback.print_exc()

            response.set_header('Content-type', 'text/plain')
            response.status = 500
            return 'Internal server error'
    return wrapper


def create_app(myshop_endpoint, templates_dir, ca_file):
    app = Bottle()
    TEMPLATE_PATH.insert(0, templates_dir)

    @app.route('/', method=['GET'])
    @handle_errors
    @view('index.mako')
    def login():
        return {}

    @app.route('/register', method=['GET'])
    @handle_errors
    @view('register.mako')
    def register():
        return {}

    @app.route('/register', method=['POST'])
    @handle_errors
    def do_register():
        full_name = request.forms.get('full_name')
        username = request.forms.get('username')
        password = request.forms.get('password')
        payload = json.dumps({
            "username": username,
            "password": password,
            "full_name": full_name
        })
        url = "{}/register".format(myshop_endpoint)
        try:
            requestor.post(url, data=payload, verify=ca_file)
        except requestor.ServiceFailedException as ex:
            error_msg = "{} Unable to register.".format(ex.error_msg)
            raise HTTPError(status=ex.status_code, body=error_msg)
        redirect('/login')

    @app.route('/login', method=['GET'])
    @handle_errors
    @view('login.mako')
    def login():
        return {}

    @app.route('/login', method=['POST'])
    @handle_errors
    def do_login():
        """ Authenticates via myshop server and saves the user's session
        token in the user's browser's cookie.
        """
        username = request.forms.get('username')
        password = request.forms.get('password')
        payload = json.dumps({
            "username": username,
            "password": password
        })
        url = "{}/auth".format(myshop_endpoint)
        try:
            resp = requestor.post(url, data=payload, verify=ca_file)
            resp = json.loads(resp.text)
            session_token = resp['session_token']
            response.set_cookie("myshop_session_token", session_token)
            print "Authenticated username={}".format(username)
            redirect('/welcome')
        except requestor.ServiceFailedException as ex:
            error_msg = "{} Authentication Failed.".format(ex.error_msg)
            raise HTTPError(status=ex.status_code, body=error_msg)

    @app.route('/welcome', method=['GET'])
    @handle_errors
    @view('welcome.mako')
    def welcome():
        """ Displays the login attempts of the current user.
        If the user has not yet authenticated, he/she will be redirected
        to the login page.

        If already authenticated, the session token will
        be picked up from the cookie. If the session token has expired,
        the user will need to re-authenticate and hence will be redirected back
        to the login page.
        """
        session_token = request.get_cookie("myshop_session_token")
        if not session_token:
            print "User not authenticated, redirecting"
            redirect('/login')

        url = "{}/logins".format(myshop_endpoint)
        headers = {"Authorization": "Session-token {}".format(session_token)}
        try:
            resp = requestor.get(url, verify=ca_file, headers=headers)
            resp = json.loads(resp.text)
            logins = resp['logins']
            return {"logins": logins}
        except requestor.ServiceFailedException as ex:
            # Session expired or Invalid session
            if ex.status_code == 401:
                print ex.error_msg, ex.status_code
                redirect('/login')
            else:
                # Unknown error
                raise HTTPError(status=ex.status_code, body=ex.error_msg)

    return app


def main():
    cert_file = resource_filename("myshop_ui", "certs/server.pem")
    key_file = resource_filename("myshop_ui", "certs/server.key")
    ca_file = resource_filename("myshop_ui", "certs/ca.pem")
    templates_dir = resource_filename("myshop_ui", "templates")
    myshop_endpoint = os.environ.get(
        'MYSHOP_ENDPOINT',
        'https://0.0.0.0:8443'
    )
    app = create_app(myshop_endpoint, templates_dir, ca_file)
    app.run(
        host='0.0.0.0',
        port=9443,
        server='gunicorn',
        loglevel='warning',
        certfile=cert_file,
        keyfile=key_file,
        ca_certs=ca_file
    )

if __name__ == '__main__':
    main()
