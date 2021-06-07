#!/bin/bash

if [[ ! -z "$GALAXY_SHARED_DIR" ]]; then
    echo "Running Apollo with mounted shared dir"
    mkdir -p "$GALAXY_SHARED_DIR"
    docker run -d -it -p 8888:8080 --name apollo -v `pwd`/apollo_shared_dir/:`pwd`/apollo_shared_dir/ gmod/apollo:latest
else
    echo "Running Apollo in remote mode"
    docker run -d -it -p 8888:8080 --name apollo gmod/apollo:latest
fi

echo "[BOOTSTRAP] Waiting while Apollo starts up..."
# Wait for apollo to be online
for ((i=0;i<30;i++))
do
    APOLLO_UP=$(arrow users get_users 2> /dev/null | head -1 | grep '^\[$' -q; echo "$?")
	if [[ $APOLLO_UP -eq 0 ]]; then
		break
	fi
    sleep 10
done

if ! [[ $APOLLO_UP -eq 0 ]]; then
    echo "Cannot connect to apollo for bootstrapping"
    arrow users get_users
    exit "${APOLLO_UP}"
fi

echo "[BOOTSTRAP] Apollo is up, bootstrapping for tests"

# Create some groups
arrow groups create_group one_group
arrow groups create_group another_group

# Create a user
arrow users create_user "test@bx.psu.edu" Junior Galaxy password

# Add some organisms
if [[ ! -z "$GALAXY_SHARED_DIR" ]]; then
    echo "[BOOTSTRAP] Create organisms from shared dir"
    cp -r tools/apollo/test-data/dataset_1_files/data/ "${GALAXY_SHARED_DIR}/org1"
    cp -r tools/apollo/test-data/dataset_1_files/data/ "${GALAXY_SHARED_DIR}/org2"
    cp -r tools/apollo/test-data/dataset_1_files/data/ "${GALAXY_SHARED_DIR}/org3"
    cp -r tools/apollo/test-data/dataset_1_files/data/ "${GALAXY_SHARED_DIR}/org4"

    arrow organisms add_organism --genus Testus --species organus test_organism $GALAXY_SHARED_DIR/org1
    arrow organisms add_organism --genus Foo --species barus alt_org $GALAXY_SHARED_DIR/org2
    arrow organisms add_organism --genus Foo3 --species barus org3 $GALAXY_SHARED_DIR/org3
    arrow organisms add_organism --genus Foo4 --species barus org4 $GALAXY_SHARED_DIR/org4
else
    echo "[BOOTSTRAP] Create organisms in remote mode"
    arrow remote add_organism --genus Testus --species organus test_organism tools/apollo/test-data/org_remote.tar.gz
    arrow remote add_organism --genus Foo --species barus alt_org tools/apollo/test-data/org_remote.tar.gz
    arrow remote add_organism --genus Foo3 --species barus org3 tools/apollo/test-data/org_remote.tar.gz
    arrow remote add_organism --genus Foo4 --species barus org4 tools/apollo/test-data/org_remote.tar.gz
fi

# Give access to organisms for test user
arrow users update_organism_permissions --write --read --export "test@bx.psu.edu" test_organism
arrow users update_organism_permissions --write --read --export "test@bx.psu.edu" alt_org
arrow users update_organism_permissions --write --read --export "test@bx.psu.edu" org3
arrow users update_organism_permissions --write --read --export "test@bx.psu.edu" org4

# Load some annotations
arrow annotations load_gff3 test_organism tools/apollo/test-data/merlin.gff
arrow annotations load_gff3 alt_org tools/apollo/test-data/merlin.gff
arrow annotations load_gff3 org3 tools/apollo/test-data/merlin.gff
arrow annotations load_gff3 org4 tools/apollo/test-data/merlin.gff
