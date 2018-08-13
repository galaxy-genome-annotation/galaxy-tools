#!/usr/bin/env python
from __future__ import print_function

import argparse
import json
import logging
import shutil
import sys
import time
import random

from webapollo import AssertUser, GuessOrg, OrgOrGuess, WAAuth, WebApolloInstance
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def pwgen(length):
    chars = list('qwrtpsdfghjklzxcvbnm')
    return ''.join(random.choice(chars) for _ in range(length))

def str2bool(string):
    if string.lower() in ('true', 't', '1'):
        return True
    else:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create or update an organism in an Apollo instance')
    WAAuth(parser)

    parser.add_argument('jbrowse', help='JBrowse Data Directory')
    parser.add_argument('email', help='User Email')
    OrgOrGuess(parser)
    parser.add_argument('--genus', help='Organism Genus')
    parser.add_argument('--species', help='Organism Species')
    parser.add_argument('--public', action='store_true', help='Make organism public')
    parser.add_argument('--group', help='Give access to a user group')
    parser.add_argument('--remove_old_directory', action='store_true', help='Remove old directory')
    parser.add_argument('--use_remote_user', type=str2bool, default=False, help='Authentification with remote_user')

    args = parser.parse_args()
    wa = WebApolloInstance(args.apollo, args.username, args.password)

    org_cn = GuessOrg(args, wa)
    if isinstance(org_cn, list):
        org_cn = org_cn[0]

    # User must have an account, if not, create it
    try:
        gx_user = AssertUser(wa.users.loadUsers(email=args.email))
    except Exception:
        firstName = args.email
        lastName = args.email
        password = pwgen(12)
        returnData = wa.users.createUser(args.email, firstName, lastName, password, role='user')
        gx_user = AssertUser(wa.users.loadUsers(email=args.email))
        if(not args.use_remote_user):
            f = open("Apollo_credentials.txt", "w")
            f.write( 'Username: %s\tPassword: %s' % (args.email, password))


    log.info("Determining if add or update required")
    try:
        org = wa.organisms.findOrganismByCn(org_cn)
    except Exception:
        org = None

    if org:
        has_perms = False
        old_directory = org['directory']
        for user_owned_organism in gx_user.organismPermissions:
            if 'WRITE' in user_owned_organism['permissions']:
                has_perms = True
                break

        if not has_perms:
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
            public=args.public
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
            public=args.public
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
