#!/bin/bash
if [ "$#" -ne 4 ] || ! [ -f "$1" ] || ! [ -f "$2" ] || ! [ -f "$3" ]; then
  echo "Usage: $0 PAGERANK_EXECUTABLE DICTIONARY_FILE LINKS_FILE OUTPUT_FILE" >&2
  exit 1
fi

tmp=$(mktemp)

set -x

$1 -o ${tmp} $3
(join <(sort -k1,1 $2) <(sort -k1,1 ${tmp})) \
    | cut -d " " -f 2- \
    | sort -k 2 -g -r \
    > $4

set +x

rm ${tmp}


