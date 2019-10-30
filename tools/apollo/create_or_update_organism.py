#!/usr/bin/env python
from __future__ import print_function

import argparse
import glob
import json
import logging
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time

from apollo import accessible_organisms
from apollo.util import GuessOrg, OrgOrGuess

from arrow.apollo import get_apollo_instance

from webapollo import UserObj, handle_credentials

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def IsBlatEnabled():
    if 'BLAT_ENABLED' not in os.environ:
        return False
    value = os.environ['BLAT_ENABLED']
    if value.lower() in ('true', 't', '1'):
        return True
    else:
        return False


def IsOrgCNSuffixEnabled():
    if 'GALAXY_APOLLO_ORG_SUFFIX' not in os.environ:
        return False
    value = os.environ['GALAXY_APOLLO_ORG_SUFFIX'].lower()
    if value in ('id', 'email'):
        return value

    return False


def IsRemote():
    return 'GALAXY_SHARED_DIR' not in os.environ or len(os.environ['GALAXY_SHARED_DIR'].lower().strip()) == 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create or update an organism in an Apollo instance')
    parser.add_argument('jbrowse_src', help='Source JBrowse Data Directory')
    parser.add_argument('jbrowse', help='Destination JBrowse Data Directory')
    parser.add_argument('email', help='User Email')
    OrgOrGuess(parser)
    parser.add_argument('--genus', help='Organism Genus')
    parser.add_argument('--species', help='Organism Species')
    parser.add_argument('--public', action='store_true', help='Make organism public')
    parser.add_argument('--group', help='Give access to a user group')
    parser.add_argument('--remove_old_directory', action='store_true', help='Remove old directory')
    parser.add_argument('--userid', help='User unique id')
    args = parser.parse_args()
    CHUNK_SIZE = 2**20
    blat_db = None

    path_fasta = args.jbrowse_src + '/seq/genome.fasta'

    # Cleanup if existing
    if not IsRemote():
        if(os.path.exists(args.jbrowse)):
            shutil.rmtree(args.jbrowse)
        # Copy files
        shutil.copytree(args.jbrowse_src, args.jbrowse, symlinks=True)

        path_2bit = args.jbrowse + '/seq/genome.2bit'
    else:
        path_2bit = tempfile.NamedTemporaryFile(prefix="genome.2bit")
        path_2bit = path_2bit.name
        os.chmod(path_2bit, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

    # Convert fasta if existing
    if IsBlatEnabled() and os.path.exists(path_fasta):
        arg = ['faToTwoBit', path_fasta, path_2bit]
        proc = subprocess.Popen(args=arg, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode:
            print("Error building index:", file=sys.stderr)
            sys.stderr.write(err)
            sys.exit(proc.returncode)
        if not IsRemote():
            # No need to send this in remote mode, it will be in the archive
            blat_db = path_2bit

    wa = get_apollo_instance()

    # User must have an account, if not, create it
    gx_user = UserObj(**wa.users._assert_or_create_user(args.email))
    handle_credentials(gx_user)

    org_cn = GuessOrg(args, wa)
    if isinstance(org_cn, list):
        org_cn = org_cn[0]

    if args.org_raw:
        suffix = IsOrgCNSuffixEnabled()
        if suffix == 'id' and args.userid:
            org_cn += ' (gx%s)' % args.userid
        elif suffix == 'email':
            org_cn += ' (%s)' % args.email

    log.info("Determining if add or update required")
    try:
        org = wa.organisms.show_organism(org_cn)
    except Exception:
        org = None

    if org and 'error' not in org:
        old_directory = org['directory']

        all_orgs = wa.organisms.get_organisms()
        if 'error' in all_orgs:
            all_orgs = []
        all_orgs = [x['commonName'] for x in all_orgs]
        if org_cn not in all_orgs:
            raise Exception("Could not find organism %s" % org_cn)

        orgs = accessible_organisms(gx_user, [org_cn], 'WRITE')
        if not orgs:
            raise Exception("Naming Conflict. You do not have write permission on this organism. Either request permission from the owner, or choose a different name for your organism.")

        log.info("\tUpdating Organism")
        if IsRemote():
            with tempfile.NamedTemporaryFile(suffix='.tar.gz') as archive:
                with tarfile.open(archive.name, mode="w:gz") as tar:
                    dataset_data_dir = args.jbrowse_src
                    for file in glob.glob(dataset_data_dir):
                        tar.add(file, arcname=file.replace(dataset_data_dir, './'))
                    if IsBlatEnabled():
                        tar.add(path_2bit, arcname="./searchDatabaseData/genome.2bit")
                data = wa.remote.update_organism(
                    org['id'],
                    archive,
                    # mandatory
                    blatdb=blat_db,
                    genus=args.genus,
                    species=args.species,
                    public=args.public
                )
        else:
            data = wa.organisms.update_organism(
                org['id'],
                org_cn,
                args.jbrowse,
                # mandatory
                genus=args.genus,
                species=args.species,
                public=args.public,
                blatdb=blat_db
            )
        time.sleep(2)

        if not IsRemote() and args.remove_old_directory and args.jbrowse != old_directory:
            shutil.rmtree(old_directory)

        data = wa.organisms.show_organism(org_cn)

    else:
        # New organism
        log.info("\tAdding Organism")

        if IsRemote():
            with tempfile.NamedTemporaryFile(suffix='.tar.gz') as archive:
                with tarfile.open(archive.name, mode="w:gz") as tar:
                    dataset_data_dir = args.jbrowse_src
                    for file in glob.glob(dataset_data_dir):
                        tar.add(file, arcname=file.replace(dataset_data_dir, './'))
                    if IsBlatEnabled():
                        with tempfile.TemporaryDirectory() as empty_dir:
                            os.chmod(empty_dir, stat.S_IRUSR | stat.S_IXUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                            tar.add(empty_dir, arcname="./searchDatabaseData/")
                            tar.add(path_2bit, arcname="./searchDatabaseData/genome.2bit")
                data = wa.remote.add_organism(
                    org_cn,
                    archive,
                    blatdb=blat_db,
                    genus=args.genus,
                    species=args.species,
                    public=args.public,
                    metadata=None
                )
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]
        else:
            data = wa.organisms.add_organism(
                org_cn,
                args.jbrowse,
                blatdb=blat_db,
                genus=args.genus,
                species=args.species,
                public=args.public,
                metadata=None
            )

        # Must sleep before we're ready to handle
        time.sleep(2)
        log.info("Updating permissions for %s on %s", gx_user, org_cn)
        wa.users.update_organism_permissions(
            gx_user.username,
            org_cn,
            write=True,
            export=True,
            read=True,
        )

        # Group access
        if args.group:
            group = wa.groups.get_groups(name=args.group)[0]
            res = wa.groups.update_organism_permissions(group['name'], org_cn,
                                                        administrate=False, write=True, read=True,
                                                        export=True)

    print(json.dumps(data, indent=2))
