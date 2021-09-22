#!/bin/bash

# Make sure everything is cleaned (including job queue)
sleep 5

# Kill GeneNoteBook
kill $GNB_PID

sleep 5

# Kill MongoDB
kill $(<"./mongo.pid")

sleep 5
