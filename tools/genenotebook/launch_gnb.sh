#!/bin/bash

set -e

mongod --dbpath ./mongo_db/ --unixSocketPrefix `pwd` --bind_ip fake_socket --logpath ./mongod.log --pidfilepath ./mongo.pid &

sleep 15

# "Listening on" is for mongodb 5x
if ! grep -q "Listening on" ./mongod.log; then
  echo "Failed to launch MongoDB:" 1>&2;
  cat ./mongod.log 1>&2;
  kill $GNB_PID;
  exit 1;
fi;

TMP_STORAGE=$(pwd)/tmp_storage
mkdir "$TMP_STORAGE"

export NODE_OPTIONS="--max-old-space-size=$((${GALAXY_MEMORY_MB:-8192} * 75 / 100))"

genoboo run --storage-path "$TMP_STORAGE" --port ${GNB_PORT} --mongo-url mongodb://$MONGO_URI%2Fmongodb-27017.sock/genenotebook > ./gnb.log 2>&1 &

export GNB_PID=$!

sleep 15

if ! grep -q "GeneNoteBook server started, serving" ./gnb.log; then
  echo "Failed to launch GeneNoteBook:" 1>&2;
  cat ./gnb.log 1>&2;
  kill $GNB_PID $(<"./mongo.pid");
  exit 1;
fi;
