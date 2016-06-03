#!/bin/bash

docker build -t ucamcldtg/equality-checker . && docker run -p 5000:5000 -it ucamcldtg/equality-checker

