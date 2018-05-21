#!/bin/bash
USER_NAME=ubuntu
SERVER_IP=130.238.28.96
NAME_NODE_IP=namenode

ssh \
    -L 8080:localhost:8080 \
    -L 4040:localhost:4040 \
    -L 8888:localhost:8888 \
    -L 50070:$NAME_NODE_IP:50070 \
    $USER_NAME@$SERVER_IP
