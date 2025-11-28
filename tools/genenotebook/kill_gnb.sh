#!/bin/bash

# Make sure everything is cleaned (including job queue)
sleep 5

# Print server log
echo ""
echo "--- 'genoboo run' stopped, printing logs (server side) ---"
cat ./gnb.log

# Kill GeneNoteBook
kill $GNB_PID

sleep 5

# Kill MongoDB
kill $(<"./mongo.pid")

# Wait to make sure the process is actually killed
sleep 60
