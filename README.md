# scrambled-words
A game to find words scrambled in a grid.

## Technologies
This webapp uses Gevent with the Eventlet worker class to run the Flask application.
Socketio is used to send messages from client to server.

## Setup
To preserve consistency with running in the cloud, this application uses HTTPS even when running locally.
You will need to run the following commands from the root of the repo to get ready for HTTPS:
```
mkdir ssl
cd ssl
openssl req -nodes -new -x509 -keyout server.key -out server.crt \
    -subj "/C=GB/ST=London/L=London/O=Local/OU=Local/CN=127.0.0.1"
```

After generating the key and certificate, you are ready to run the application.
Your run configuration should look like the following:
```
venv/bin/gunicorn \
    --certfile=ssl/server.crt \
    --keyfile=ssl/server.key \
    --worker-class eventlet \
    -w 1 \
    "application:create_flask_app()"
```
Make sure to run the application with the working directory set at the root of the repo.
