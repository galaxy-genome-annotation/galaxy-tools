#!/bin/bash

export PWD=`pwd` &&
sed -i.bak "s|unix_socket_directories.*|unix_socket_directories = '$PWD/postgresql/'|" ./postgresql/db/postgresql.conf &&

pglite start  -d ./postgresql &&

timeout 60 bash -c 'until pglite status -d ./postgresql | grep -F -q "server is running"; do sleep 1; done' &&
pglite status -d ./postgresql &&
timeout 60 bash -c 'until ls -la ./postgresql | grep -F -q ".s.PGSQL.5432"; do sleep 1; done' &&
pglite status -d ./postgresql &&

echo "__default: local" > '.auth.yml' &&
echo "local:" >> '.auth.yml' &&
echo "    dbhost: \"xxx\"" >> '.auth.yml' &&
echo "    dbname: \"xxx\"" >> '.auth.yml' &&
echo "    dbpass: \"xxx\"" >> '.auth.yml' &&
echo "    dbuser: \"xxx\"" >> '.auth.yml' &&
echo "    dbschema: \"$1\"" >> '.auth.yml' &&
echo "    dbport: \"xxx\"" >> '.auth.yml' &&
echo "    dburl: \"$(pglite url -d ./postgresql)\"" >> '.auth.yml' &&

export CHAKIN_GLOBAL_CONFIG_PATH='.auth.yml'
