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


from webapollo import GuessOrg, OrgOrGuess, PermissionCheck, WAAuth, WebApolloInstance
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create or update an organism in an Apollo instance')
    WAAuth(parser)
    parser.add_argument('jbrowse_old', help='Old JBrowse Data Directory')
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
    shutil.copytree(args.jbrowse_old, args.jbrowse)

    path_fasta = args.jbrowse + '/seq/genome.fasta'
    path_2bit = args.jbrowse + '/seq/genome.2bit'

    # Convert fasta if existing
    if(os.path.exists(path_fasta)):
      arg = [ 'faToTwoBit', path_fasta, path_2bit]
      tmp_stderr = tempfile.NamedTemporaryFile( prefix="tmp-data-manager-twobit-builder-stderr" )
      proc = subprocess.Popen(args=arg, shell=False, cwd=args.jbrowse, stderr=tmp_stderr.fileno() )
      return_code = proc.wait()
      if return_code:
        tmp_stderr.flush()
        tmp_stderr.seek(0)
        print("Error building index:", file=sys.stderr)
        while True:
            chunk = tmp_stderr.read( CHUNK_SIZE )
            if not chunk:
                break
            sys.stderr.write( chunk )
        sys.exit( return_code)
      blat_db = path_2bit
      tmp_stderr.close()

    wa = WebApolloInstance(args.apollo, args.username, args.password)

    org_cn = GuessOrg(args, wa)
    if isinstance(org_cn, list):
        org_cn = org_cn[0]

    # User must have an account, if not, create it
    gx_user = wa.users.assertOrCreateUser(args.email)

    log.info("Determining if add or update required")
    try:
        org = wa.organisms.findOrganismByCn(org_cn)
    except Exception:
        org = None

    if org:
        old_directory = org['directory']

        if not PermissionCheck(gx_user, org_cn, "WRITE"):
            print("Naming Conflict. You do not have permissions to access this organism. Either request permission from the owner, or choose a different name for your organism.")
            sys.exit(2)

        log.info("\tUpdating Organism")
        data = wa.organisms.updateOrganismInfo(
            org['id'],
            org_cn,
            args.jbrowse,
            # mandatory
            genus=args.genus,
            species=args.species,
            public=args.public,
            blatdb = blat_db
        )
        time.sleep(2)
        if args.remove_old_directory and args.jbrowse != old_directory:
            shutil.rmtree(old_directory)

        data = [wa.organisms.findOrganismById(org['id'])]

    else:
        # New organism
        log.info("\tAdding Organism")
        data = wa.organisms.addOrganism(
            org_cn,
            args.jbrowse,
            genus=args.genus,
            species=args.species,
            public=args.public,
            blatdb = blat_db
        )

        # Must sleep before we're ready to handle
        time.sleep(2)
        log.info("Updating permissions for %s on %s", gx_user, org_cn)
        wa.users.updateOrganismPermission(
            gx_user, org_cn,
            write=True,
            export=True,
            read=True,
        )

        # Group access
        if args.group:
            group = wa.groups.loadGroupByName(name=args.group)
            res = wa.groups.updateOrganismPermission(group, org_cn,
                                                     administrate=False, write=True, read=True,
                                                     export=True)

    data = [o for o in data if o['commonName'] == org_cn]
    print(json.dumps(data, indent=2))
