#!/bin/bash

while true; do
    git fetch
    git reset --hard HEAD
    git merge '@{u}'
    sleep 10
done

