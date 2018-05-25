#!/bin/bash

DATA_DIR="/home/ubuntu/data"

bwm-ng --unit bits \
       --interfaces ens3 \
       -o csv - | \
    xz --fast > $DATA_DIR/bandwidth-measurements-$HOSTNAME.xz
