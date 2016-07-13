#!/bin/bash
if [ "$#" -ne 3 ] || ! [ -f "$1" ] || ! [ -f "$2" ]; then
  echo "Usage: $0 PAGERANK_EXECUTABLE LINKS_FILE OUTPUT_FILE" >&2
  exit 1
fi

tmp=$(mktemp)

set -x

$1 -o ${tmp} $2
cat ${tmp} | sort -k 2 -g -r > $3

set +x

rm ${tmp}


