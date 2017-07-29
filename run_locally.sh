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
