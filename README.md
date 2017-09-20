# Galaxy Tools for Galaxy Genome Annotation

This repo contains some Galaxy repositories specific to the [Galaxy Genome
Annotation project](https://github.com/galaxy-genome-annotation) project.

## Overview

Directory | Purpose
--------- | --------
apollo    | Tools for talking to an Apollo server, e.g. adding a new organism, fetching data, sharing data between users.
askomics  | Tools for talking to an AskOmics
jbrowse   | Galaxy-JBrowse extras, things outside the scope of the normal JBrowse tools.
tripal    | Tools for administering a Tripal instance.

These tools will only talk to a single Tripal/Apollo currently, pending
implementation of tool+user preferences in Galaxy. Most of them require
additional setup in the form of environment variables.

## LICENSE

MIT
