#!/bin/bash

while true; do
    git fetch
    git reset --hard HEAD
    git merge '@{u}'
    pip install -r requirements.txt
    sleep 10
done

