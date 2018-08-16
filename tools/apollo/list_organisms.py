#!/usr/bin/env python
from __future__ import print_function

import argparse
import json

from webapollo import AssertUser, PasswordGenerator, WAAuth, WebApolloInstance, accessible_organisms

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List all organisms available in an Apollo instance')
    WAAuth(parser)
    parser.add_argument('email', help='User Email')
    args = parser.parse_args()

    wa = WebApolloInstance(args.apollo, args.username, args.password)

    try:
        gx_user = AssertUser(wa.users.loadUsers(email=args.email))
    except Exception:
        returnData = wa.users.createUser(args.email, args.email, args.email, PasswordGenerator(12), role='user', addToHistory=True)
        gx_user = AssertUser(wa.users.loadUsers(email=args.email))

    all_orgs = wa.organisms.findAllOrganisms()

    try:
        orgs = accessible_organisms(gx_user, all_orgs)
    except Exception:
        orgs = []

    print(json.dumps(orgs, indent=2))
