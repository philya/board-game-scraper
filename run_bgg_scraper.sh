#!/usr/bin/env bash

DATADIR="/Volumes/NimbleHook/data/bgg/"
SPIDER="bgg"

JOBDIR="${DATADIR}jobs/${SPIDER}/$(date --utc +'%Y-%m-%dT%H-%M-%S')"
scrapy crawl "${SPIDER}" \
    --output "${DATADIR}feeds/%(name)s/%(time)s/%(class)s.csv" \
    --set "JOBDIR=${JOBDIR}"
