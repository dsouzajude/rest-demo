This is a simple REST API demo project written in python. The demo comes both with a server and a client that would consume the api exposed by the server. The server allows users to register online, authenticate and then see their login history. It exposes the following endpoints:

```
POST /register -d {
  "username": "string",
  "password": "string",
  "full_name": "string"
}

POST /auth -d {
  "username": "string",
  "password": "string"
}

GET /logins
```

For the purposes of the demo, the server uses an SQLite database.


The Server
==========
The server allows users to register, authenticate and view their login history. The server only allows users to view their login history if they have been successfully authenticated. For users to authenticate themselves they first need to register their username and password which would then be saved in the server's database. From a security point of view, the server only stores the hash of the password and not the password itself. After a successful registration the user can then proceed to authentication.

Authentication works via the use of session tokens. Upon successful authentication the server responds back with a limited time session token. The default is one day. The client needs to pass on these session tokens on every subsequent request which would indicate to the server that its a valid session, a valid user and that this user is authenticated. Using this session token the server will retrieve the username connected with the session and then provide login history of the logged-in user.

Session tokens can be revoked at anytime which would allow the user to authenticate again with the server.

For increased security, the server communicates over SSL that uses self-signed certificates. This is only done for the purposes of the demo. In a real production setup, the SSL termination should be done on a loadbalancer such as AWS ELB, Nginx or HAProxy.

With the use of SSL, it would be hard for an attacker to sniff traffic and get hold of the session token, hence this would strengthen privacy such that users would not be allowed to view other users login history.


The Client
==========
The client is a web-ui that consumes the server's API. It is a separate setup from the server and is basically the web interface for the server that allows users to register, authenticate and view their login history.


Server Installation
===================
The following command will install the server and get it up and running. It will also install the dependencies which are passlib, bottle, guincorn, SQLAlchemy, webtest, jsonschema.

```bash
>> git clone https://github.com/dsouzajude/rest-demo.git
>> cd rest-demo/server
>> python setup.py install
>> myshop-server
```

For the purposes of the demo, the server communicates over SSL and listens on port 8443.


Client Installation
===================
The following command will install the client. It uses mako for the web ui and saves session tokens via cookies in the client's browser.

```bash
>> git clone https://github.com/dsouzajude/rest-demo.git
>> cd rest-demo/client
>> python setup.py install
>> myshop-ui
```

Server Demo
===========
Running the server, listens on port 8443 over HTTPS.

```bash
>> myshop-server
```

Register a user.

```bash
curl --cacert server/certs/ca.pem https://0.0.0.0:8443/register -d '{"username": "jude", "password": "jude", "full_name": "Jude DSouza"}'
```

Response:

```json
{
  "username": "jude",
  "update_time": "2017-07-21T18:58:06Z",
  "create_time": "2017-07-21T18:58:06Z",
  "full_name": "Jude DSouza"
}
```

Authenticate the user.

```bash
curl --cacert server/certs/ca.pem https://0.0.0.0:8443/auth -d '{"username": "jude", "password": "jude"}'
```

Response:

```json
{
  "session_token": "5586cd30-1dbe-4660-9b68-b20be4d280fb"
}
```

Get login history (5 most recent successful logins).

```bash
curl --cacert server/certs/ca.pem https://0.0.0.0:8443/logins -H 'Authorization: Session-token 5586cd30-1dbe-4660-9b68-b20be4d280fb'
```

Response:

```json
{
  "logins": [
    {"username": "jude", "login_time": "2017-07-21T19:03:25Z"},
    {"username": "jude", "login_time": "2017-07-21T19:03:24Z"},
    {"username": "jude", "login_time": "2017-07-21T19:03:21Z"},
    {"username": "jude", "login_time": "2017-07-21T19:03:19Z"},
    {"username": "jude", "login_time": "2017-07-21T19:03:18Z"}
  ]
}
```


Client Demo
===========
The pre-requisite is to run the server and for that follow above steps of the Server Demo. Also, this demo has been tested on the Chrome browser.

Run the client, listens on port 9443 and also communicates over SSL.

```bash
>> myshop-ui
```

Open the browser and browse to the url "https://0.0.0.0:9443"


Running tests (server and client)
=================================
`cd` into the project home directory and run the tests via nose.

```
>> cd rest-demo/server
>> nosetests -svx tests

>> cd rest-demo/client
>> nosetests -svx tests
```
