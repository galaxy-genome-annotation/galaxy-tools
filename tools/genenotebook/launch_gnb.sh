#!/bin/bash

set -e

# Make sure the file always exists even on first grep
touch mongod.log

echo "Starting mongod, listening on unix socket in $(pwd)"
mongod --dbpath ./mongo_db/ --unixSocketPrefix "$(pwd)" --bind_ip fake_socket --logpath ./mongod.log --pidfilepath ./mongo.pid &

echo "Waiting while mongod starts up"

tries=0

# "Listening on" is for mongodb 150x
while ! grep -q "Listening on" ./mongod.log; do

  tries=$((tries + 1))

  if [ "$tries" -ge 150 ]; then
    echo "Failed to launch MongoDB:" 1>&2;
    cat ./mongod.log 1>&2;
    exit 1;
  fi

  sleep 5
done;

TMP_STORAGE=$(pwd)/tmp_storage
mkdir "$TMP_STORAGE"

# Make sure the file always exists
touch gnb.log

export NODE_OPTIONS="--max-old-space-size=$((${GALAXY_MEMORY_MB:-8192} * 75 / 100))"

# Find free port at the last moment
export GNB_PORT=$(bash "$(dirname "${BASH_SOURCE[0]}")/find_free_port.sh")
echo "Mongod is ready, starting gnb now on port ${GNB_PORT} and with mongodb://${MONGO_URI}%2Fmongodb-27017.sock/genenotebook"

genoboo run --storage-path "$TMP_STORAGE" --port ${GNB_PORT} --mongo-url mongodb://$MONGO_URI%2Fmongodb-27017.sock/genenotebook > ./gnb.log 2>&1 &

export GNB_PID=$!

tries_gnb=0

while ! grep -q "GeneNoteBook server started, serving" ./gnb.log; do

  tries_gnb=$((tries_gnb + 1))

  # GNB can take a while to start depending on storage (accessing many many small js files)
  if [ "$tries_gnb" -ge 250 ]; then
    echo "Failed to launch GeneNoteBook:" 1>&2;
    cat ./gnb.log 1>&2;
    kill $GNB_PID $(<"./mongo.pid");
    exit 1;
  fi

  sleep 3
done;

# Make sure that gnb is working, and that it's serving on the expected port
# Wait a bit for curl to work, just in case. Dump the logs if it does not

tries_curl=0

while ! curl -s "http://127.0.0.1:${GNB_PORT}/healthcheck"; do
  tries_curl=$((tries_curl + 1))
  if [ "$tries_curl" -ge 200 ]; then
    echo "Healthcheck is not working, stopping:" 1>&2;
    cat ./gnb.log 1>&2;
    kill $GNB_PID $(<"./mongo.pid");
    exit 1;
  fi

  sleep 3
done;

grep -q "Healthcheck OK" ./gnb.log

sleep 30

echo "GNB is ready"