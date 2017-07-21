import os
import json
import sys
from functools import wraps
from pkg_resources import Requirement, resource_filename

import jsonschema
import bottle
from bottle import request, Bottle, response

import core, schemas, errors


class MyshopApp(Bottle):
    def __init__(self, controller):
        self.controller = controller
        super(MyshopApp, self).__init__()

    def route(self, pattern, require_auth=True, *args, **kwargs):
        """ Wrapper around the original Bottle.route() that validates
        the session before executing the route actions.

        The session_token can be extracted either from the 'Authorization'
        header or from the query parameters.
        """
        def decorator(handler):
            @wraps(handler)
            def wrapper(*args, **kwargs):
                if require_auth:
                    session_token = None
                    auth_header = request.get_header('Authorization')
                    if auth_header:
                        # Header format 'Authorization: Session-token mytoken'
                        session_token = auth_header.split(' ', 1)[1]
                    else:
                        # Params format '?session_token=mytoken'
                        session_token = request.query.get('session_token')

                    if not session_token:
                        raise errors.Unauthorized()

                    # Raises an exception if the session is not valid
                    # Else get the username connected with the session.
                    username = self.controller.validate_session(session_token)

                    return handler(username, *args, **kwargs)

                return handler(*args, **kwargs)

            return super(MyshopApp, self)\
                .route(pattern, *args, **kwargs)(wrapper)

        return decorator


def create_app(controller):
    app = MyshopApp(controller)

    @app.error()
    @app.error(404)
    def handle_error(error):
        if issubclass(type(error.exception), errors.ApiException):
            response.status = error.exception.code
        else:
            response.status = error.status_code

        error_dict = {
            "message": str(error.exception) if error.exception else '',
            "exc_type": type(error.exception).__name__,
            "status_code": response.status
        }

        # Log error in server
        print 'Error - {}'.format(error_dict)

        # Return error description back to the client
        # Would not contain coding details
        response.set_header('Content-type', 'application/json')
        return json.dumps({
            "code": error_dict['exc_type'],
            "status": error_dict['status_code']
        })

    @app.route('/ping', require_auth=False, method=['GET'])
    def ping():
        controller.ping()
        return {'service_name': 'myshop'}

    @app.route('/register', require_auth=False, method=['POST'])
    def register_user():
        data = {}
        try:
            data = json.loads(request.body.read())
            schemas.register_user.validate(data)
        except jsonschema.ValidationError as err:
            raise errors.BadRequest(str(err))
        except ValueError:
            raise errors.BadRequest()

        user = controller.register_user(
            data['username'],
            data['password'],
            data['full_name']
        )
        return user.to_json_dict()

    @app.route('/auth', require_auth=False, method=['POST'])
    def authenticate():
        data = {}
        try:
            data = json.loads(request.body.read())
            schemas.auth.validate(data)
        except jsonschema.ValidationError as err:
            raise errors.BadRequest(str(err))
        except ValueError:
            raise errors.BadRequest()

        username = data['username']
        password = data['password']
        session_token = controller.authenticate(username, password)
        return {"session_token": session_token}

    @app.route('/logins', method=['GET'])
    def get_successful_logins(username):
        logins = controller.get_successful_logins(username)
        logins_json = [login.to_json_dict() for login in logins]
        return {"logins": logins_json}

    return app


def main():
    """ Run the server. The server supports SSL since the application is
    storing sensitive information like username and password. This is done only
    for a demo server.

    In a production system, usually SSL would be terminated via a proxy (maybe
    nginx or haproxy) and then http connections would be forwarded to the
    from the proxy.
    """
    cert_file = resource_filename("myshop", "certs/server.pem")
    key_file = resource_filename("myshop", "certs/server.key")
    db_path = resource_filename("myshop", "data/myshop.db")
    db_url = 'sqlite:///{path}'.format(path=db_path)
    db_url = os.environ.get('DB_URL', db_url)
    controller = core.Controller(db_url)
    app = create_app(controller)
    app.run(
        host='0.0.0.0',
        port=8443,
        server='gunicorn',
        loglevel='warning',
        certfile=cert_file,
        keyfile=key_file
    )


if __name__=='__main__':
    main()
