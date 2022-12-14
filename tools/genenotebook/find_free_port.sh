#!/bin/bash

set -e

# This script finds a free port on the local machine in the 7000-65000 interval
# Should work in biocontainers derived from conda
# Taken from https://unix.stackexchange.com/a/358101

if command -v ss &> /dev/null
then
  ss -alnut | awk '
    $2 == "LISTEN" {
      if ($5 ~ "[.:][0-9]+$") {
        split($5, a, /[:.]/);
        port = a[length(a)];
        p[port] = 1
      }
    }
    END {
      for (i = 7000; i < 65000 && p[i]; i++){};
      if (i == 65000) {exit 1};
      print i
    }
  '
elif command -v netstat &> /dev/null
then
  netstat -aln | awk '
    $6 == "LISTEN" {
      if ($4 ~ "[.:][0-9]+$") {
        split($4, a, /[:.]/);
        port = a[length(a)];
        p[port] = 1
      }
    }
    END {
      for (i = 7000; i < 65000 && p[i]; i++){};
      if (i == 65000) {exit 1};
      print i
    }
  '
else
  echo "This tool requires one of 'netstat' of 'ss' commands."
fi
