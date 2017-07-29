#!/bin/bash


# Start server
##############
myshop-server &
SERVER_PID=$!

# Start client
##############
myshop-ui &
CLIENT_PID=$!


wait $SERVER_PID $CLIENT_PID



#### Fresh test run in docker ######
####################################
# docker run -it \
#            -p 8443:8443 \
#            -p 9443:9443 \
#            ubuntu:latest bash -c "apt-get update; \
#            apt-get install -y python-pip git; \
#            git clone https://github.com/dsouzajude/rest-demo.git; \
#            cd /rest-demo/server; \
#            python setup.py install; \
#            cd /rest-demo/client; \
#            python setup.py install; \
#            myshop-server & \
#            myshop-ui & \
#            wait"
