#!/usr/bin/env python
from __future__ import print_function

import argparse
import logging

from webapollo import AssertUser, GuessOrg, OrgOrGuess, PasswordGenerator, PermissionCheck, WAAuth, WebApolloInstance
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sample script to completely delete an organism')
    WAAuth(parser)
    parser.add_argument('email', help='User Email')
    OrgOrGuess(parser)

    args = parser.parse_args()

    wa = WebApolloInstance(args.apollo, args.username, args.password)
    # User must have an account
    try:
        gx_user = AssertUser(wa.users.loadUsers(email=args.email))
    except Exception:
        returnData = wa.users.createUser(args.email, args.email, args.email, PasswordGenerator(12), role='user', addToHistory=True)
        gx_user = AssertUser(wa.users.loadUsers(email=args.email))

    # Get organism
    org_cn = GuessOrg(args, wa)
    if isinstance(org_cn, list):
        org_cn = org_cn[0]

    if not PermissionCheck(gx_user, org_cn, "WRITE"):
        raise Exception("You do not have write permission on this organism")
    org = wa.organisms.findOrganismByCn(org_cn)

    # Call setSequence to tell apollo which organism we're working with
    wa.annotations.setSequence(org['commonName'], org['id'])
    # Then get a list of features.
    features = wa.annotations.getFeatures()
    # For each feature in the features
    for feature in features['features']:
        # We see that deleteFeatures wants a uniqueName, and so we pass
        # is the uniquename field in the feature.
        print(wa.annotations.deleteFeatures([feature['uniquename']]))
