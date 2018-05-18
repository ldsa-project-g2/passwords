#!/bin/bash
USER_NAME=ubuntu
SERVER_IP=130.238.28.96

ssh -v \
    -L 8080:localhost:8080 \
    -L 4040:localhost:4040 \
    -L 8888:localhost:8888 \
    $USER_NAME@$SERVER_IP
