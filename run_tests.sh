#!/bin/bash 
ls shortener | grep .py$ | cut -d. -f1 | xargs -L1 -I{} python3 -m shortener.{}
