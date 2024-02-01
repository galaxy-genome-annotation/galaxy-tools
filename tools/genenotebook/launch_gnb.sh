#!/bin/bash

set -e

echo "Running mongod: "
mongod --dbpath ./mongo_db/ --unixSocketPrefix "$(pwd)" --bind_ip fake_socket --logpath ./mongod.log --pidfilepath ./mongo.pid &

echo "Waiting while mongod starts up"

tries=0

# "Listening on" is for mongodb 5x
while ! grep -q "Listening on" ./mongod.log; do

  tries=$((tries + 1))

  if [ "$tries" -ge 30 ]; then
    echo "Failed to launch MongoDB:" 1>&2;
    cat ./mongod.log 1>&2;
    exit 1;
  fi

  sleep 3
done;

TMP_STORAGE=$(pwd)/tmp_storage
mkdir "$TMP_STORAGE"

export NODE_OPTIONS="--max-old-space-size=$((${GALAXY_MEMORY_MB:-8192} * 75 / 100))"

genoboo run --storage-path "$TMP_STORAGE" --port ${GNB_PORT} --mongo-url mongodb://$MONGO_URI%2Fmongodb-27017.sock/genenotebook > ./gnb.log 2>&1 &

export GNB_PID=$!

tries_gnb=0

while ! grep -q "GeneNoteBook server started, serving" ./gnb.log; do

  tries_gnb=$((tries_gnb + 1))

  if [ "$tries_gnb" -ge 30 ]; then
    echo "Failed to launch GeneNoteBook:" 1>&2;
    cat ./gnb.log 1>&2;
    kill $GNB_PID $(<"./mongo.pid");
    exit 1;
  fi

  sleep 3
done;
