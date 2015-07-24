#!/bin/bash
docker build -t marker . && docker run -p 5000:5000 -it marker