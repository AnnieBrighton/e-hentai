#!/bin/bash

BASE=$(dirname $0)

cat "$1" | while read url other ; do
  [ -n "$url" ] && $BASE/ehentai.py "$url"
done
