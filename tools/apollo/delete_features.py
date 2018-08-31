#!/usr/bin/env python
from __future__ import print_function

import argparse
import logging
import random

from webapollo import GuessOrg, OrgOrGuess, PermissionCheck, WAAuth, WebApolloInstance, retry
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sample script to delete all features from an organism')
    WAAuth(parser)
    parser.add_argument('email', help='User Email')
    parser.add_argument('--type', help='Feature type filter')
    OrgOrGuess(parser)

    args = parser.parse_args()

    wa = WebApolloInstance(args.apollo, args.username, args.password)
    # User must have an account
    gx_user = wa.users.assertOrCreateUser(args.email)

    # Get organism
    org_cn = GuessOrg(args, wa)
    if isinstance(org_cn, list):
        org_cn = org_cn[0]

    if not PermissionCheck(gx_user, org_cn, "WRITE"):
        raise Exception("Action not permitted")
    org = wa.organisms.findOrganismByCn(org_cn)

    sequences = wa.organisms.getSequencesForOrganism(org['id'])
    for sequence in sequences['sequences']:
        log.info("Processing %s %s", org['commonName'], sequence['name'])
        # Call setSequence to tell apollo which organism we're working with
        wa.annotations.setSequence(sequence['name'], org['id'])
        # Then get a list of features.
        features = wa.annotations.getFeatures()
        # For each feature in the features
        for feature in sorted(features['features'], key=lambda x: random.random()):
            if args.type:
                if args.type == 'tRNA':
                    if feature['type']['name'] != 'tRNA':
                        continue

                elif args.type == 'terminator':
                    if feature['type']['name'] != 'terminator':
                        continue

                elif args.type == 'mRNA':
                    if feature['type']['name'] != 'mRNA':
                        continue

                else:
                    raise Exception("Unknown type")

            # We see that deleteFeatures wants a uniqueName, and so we pass
            # is the uniquename field in the feature.
            def fn():
                wa.annotations.deleteFeatures([feature['uniquename']])
                print('Deleted %s [type=%s]' % (feature['uniquename'], feature['type']['name']))

            if not retry(fn, limit=3):
                print('Error %s' % feature['uniquename'])
