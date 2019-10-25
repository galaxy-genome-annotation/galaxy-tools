#!/usr/bin/env python
from __future__ import print_function

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create or update an organism in an Apollo instance')
    parser.add_argument('jbrowse_src', help='Old JBrowse Data Directory')
    parser.add_argument('jbrowse', help='JBrowse Data Directory')
    parser.add_argument('email', help='User Email')
    OrgOrGuess(parser)
    parser.add_argument('--genus', help='Organism Genus')
    parser.add_argument('--species', help='Organism Species')
    parser.add_argument('--public', action='store_true', help='Make organism public')
    parser.add_argument('--group', help='Give access to a user group')
    parser.add_argument('--remove_old_directory', action='store_true', help='Remove old directory')
    args = parser.parse_args()
    CHUNK_SIZE = 2**20
    blat_db = None

    # Cleanup if existing
    if(os.path.exists(args.jbrowse)):
        shutil.rmtree(args.jbrowse)
    # Copy files
    shutil.copytree(args.jbrowse_src, args.jbrowse, symlinks=True)

    path_fasta = args.jbrowse + '/seq/genome.fasta'
    path_2bit = args.jbrowse + '/seq/genome.2bit'

    # Convert fasta if existing
    if(IsBlatEnabled() and os.path.exists(path_fasta)):
        arg = ['faToTwoBit', path_fasta, path_2bit]
        tmp_stderr = tempfile.NamedTemporaryFile(prefix="tmp-twobit-converter-stderr")
        proc = subprocess.Popen(args=arg, shell=False, cwd=args.jbrowse, stderr=tmp_stderr.fileno())
        return_code = proc.wait()
        if return_code:
            tmp_stderr.flush()
            tmp_stderr.seek(0)
            print("Error building index:", file=sys.stderr)
            while True:
                chunk = tmp_stderr.read(CHUNK_SIZE)
                if not chunk:
                    break
                sys.stderr.write(chunk)
            sys.exit(return_code)
        blat_db = path_2bit
        tmp_stderr.close()

    wa = get_apollo_instance()

    # User must have an account, if not, create it
    gx_user = UserObj(**wa.users._assert_or_create_user(args.email))
    handle_credentials(gx_user)

    org_cn = GuessOrg(args, wa)
    if isinstance(org_cn, list):
        org_cn = org_cn[0]

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
        all_orgs = [org['commonName'] for org in all_orgs]
        if org_cn not in all_orgs:
            raise Exception("Could not find organism %s" % org_cn)

        orgs = accessible_organisms(gx_user, [org_cn], 'WRITE')
        if not orgs:
            raise Exception("Naming Conflict. You do not have write permission on this organism. Either request permission from the owner, or choose a different name for your organism.")

        log.info("\tUpdating Organism")
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
        if args.remove_old_directory and args.jbrowse != old_directory:
            shutil.rmtree(old_directory)

        data = wa.organisms.show_organism(org_cn)

    else:
        # New organism
        log.info("\tAdding Organism")
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
            res = wa.groups.update_organism_permissions(group, org_cn,
                                                        administrate=False, write=True, read=True,
                                                        export=True)

    print(json.dumps(data, indent=2))
