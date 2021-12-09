#!/usr/bin/env python
from __future__ import print_function

import argparse
import json
import time

from apollo import accessible_organisms
from apollo.util import CnOrGuess, GuessCn

from arrow.apollo import get_apollo_instance

from webapollo import UserObj, handle_credentials

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to export data from Apollo via web services')
    CnOrGuess(parser)
    parser.add_argument('--gff', type=argparse.FileType('w'))
    parser.add_argument('--gff_with_fasta', action='store_true')
    parser.add_argument('--fasta_pep', type=argparse.FileType('w'))
    parser.add_argument('--fasta_cds', type=argparse.FileType('w'))
    parser.add_argument('--fasta_cdna', type=argparse.FileType('w'))
    parser.add_argument('--vcf', type=argparse.FileType('w'))
    parser.add_argument('--json', type=argparse.FileType('w'))
    parser.add_argument('--die', action='store_true')
    parser.add_argument('email', help='User Email')
    args = parser.parse_args()

    wa = get_apollo_instance()

    # User must have an apollo account, if not, create it
    gx_user = UserObj(**wa.users._assert_or_create_user(args.email))
    handle_credentials(gx_user)

    org_cns, seqs = GuessCn(args, wa)
    if not isinstance(org_cns, list):
        org_cns = [org_cns]

    all_orgs = wa.organisms.get_organisms()
    if 'error' in all_orgs:
        all_orgs = []
    all_orgs = [org['commonName'] for org in all_orgs]

    def error(message):
        if args.die:
            raise Exception(message)
        else:
            print(message)

    org_data = []
    for org_cn in org_cns:
        if org_cn not in all_orgs:
            raise Exception("Could not find organism %s" % org_cn)

        orgs = accessible_organisms(gx_user, [org_cn], 'READ')
        if not orgs:
            raise Exception("You do not have read permission on organism %s" % org_cn)

        org = wa.organisms.show_organism(org_cn)

        # Fetch all the refseqs
        realSeqs = wa.organisms.get_sequences(org['id'])

        # We'll loop over them individually for decreased memory pressure
        for sequence in realSeqs['sequences']:
            print("Downloading", sequence)

            try:
                uuid_gff = wa.io.write_downloadable(org['commonName'], 'GFF3', export_gff3_fasta=args.gff_with_fasta, sequences=[sequence['name']])
                if 'error' in uuid_gff or 'uuid' not in uuid_gff:
                    error("Apollo failed to prepare the GFF3 file for download: %s" % uuid_gff)
                args.gff.write(wa.io.download(uuid_gff['uuid'], output_format="text"))
                time.sleep(1)
            except Exception as e:
                error(e)


            try:
                uuid_vcf = wa.io.write_downloadable(org['commonName'], 'VCF', sequences=[sequence['name']])
                if 'error' in uuid_vcf or 'uuid' not in uuid_vcf:
                    error("Apollo failed to prepare the VCF file for download: %s" % uuid_vcf)
                args.vcf.write(wa.io.download(uuid_vcf['uuid'], output_format="text"))
                time.sleep(1)
            except Exception as e:
                error(e)

            try:
                uuid_fa = wa.io.write_downloadable(org['commonName'], 'FASTA', sequences=[sequence['name']], seq_type='cdna')
                if 'error' in uuid_fa or 'uuid' not in uuid_fa:
                    error("Apollo failed to prepare the cdna FASTA file for download: %s" % uuid_fa)
                args.fasta_cdna.write(wa.io.download(uuid_fa['uuid'], output_format="text"))
                time.sleep(1)
            except Exception as e:
                error(e)

            try:
                uuid_fa = wa.io.write_downloadable(org['commonName'], 'FASTA', sequences=[sequence['name']], seq_type='cds')
                if 'error' in uuid_fa or 'uuid' not in uuid_fa:
                    error("Apollo failed to prepare the cds FASTA file for download: %s" % uuid_fa)
                args.fasta_cds.write(wa.io.download(uuid_fa['uuid'], output_format="text"))
                time.sleep(1)
            except Exception as e:
                error(e)

            try:
                uuid_fa = wa.io.write_downloadable(org['commonName'], 'FASTA', sequences=[sequence['name']], seq_type='peptide')
                if 'error' in uuid_fa or 'uuid' not in uuid_fa:
                    error("Apollo failed to prepare the file for download: %s" % uuid_fa)
                args.fasta_pep.write(wa.io.download(uuid_fa['uuid'], output_format="text"))
                time.sleep(1)
            except Exception as e:
                error(e)

            org_data.append(org)

    args.json.write(json.dumps(org_data, indent=2))
