#!/bin/bash
flake8 --exclude=.git,conda,test-data --ignore E501 *.py
