#!/bin/bash

# Kill GeneNoteBook
kill $GNB_PID

sleep 5

# Kill MongoDB
kill $(<"./mongo.pid")

sleep 5
