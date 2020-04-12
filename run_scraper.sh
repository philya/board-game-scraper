#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="$(dirname "$(readlink --canonicalize "${BASH_SOURCE[0]}")")"
SCRAPER="${1:-}"
FEEDS_DIR="${2:-${BASE_DIR}/feeds}"
JOBS_DIR="${3:-${BASE_DIR}/jobs}"
JOB_DIR="${JOBS_DIR}/${SCRAPER}"
DONT_RUN_BEFORE_FILE="${JOB_DIR}/.dont_run_before"
STATE_FILE='.state'
DATE="$(date --utc +'%Y-%m-%dT%H-%M-%S')"

if [[ -z "${SCRAPER}" ]]; then
    echo 'Scraper is required, aborting...'
    exit 1
fi

echo "Running scraper <${SCRAPER}>"
echo "Saving feeds to <${FEEDS_DIR}> and job data to <${JOB_DIR}>"

function find_state() {
    BASE_DIR="${1}"
    STATES="${2}"
    DELETE="${3:-}"

    for DIR in "${BASE_DIR}"/*; do
        for STATE in ${STATES}; do
            if [[ -d "${DIR}" && -f "${DIR}/${STATE_FILE}" && "$(cat "${DIR}/${STATE_FILE}")" == "${STATE}" ]]; then
                basename "${DIR}"
                if [[ -n "${DELETE}" ]]; then
                    rm --recursive --force "${DIR}"
                fi
            fi
        done
    done
}

mkdir --parents "${BASE_DIR}/.scrapy/httpcache" "${FEEDS_DIR}/${SCRAPER}" "${JOB_DIR}"

DELETED=$(find_state "${JOB_DIR}" 'finished' 'true')

if [[ -n "${DELETED}" ]]; then
    echo "Deleted finished jobs in <${JOB_DIR}>: ${DELETED}."
fi

RUNNING=$(find_state "${JOB_DIR}" 'running')

if [[ -n "${RUNNING}" ]]; then
    echo "Found a running job <$(echo "${RUNNING}" | tr -d '[:space:]')>, skipping <${SCRAPER}>..."
    exit 0
fi

JOBTAG="${DATE}"
SHUT_DOWN="$(find_state "${JOB_DIR}" 'shutdown closespider_timeout')"

if [[ -n "${SHUT_DOWN}" ]]; then
    JOBTAG="$(echo "${SHUT_DOWN}" | tr -d '[:space:]')"
    echo "Resuming previous job <${JOBTAG}> for spider <${SCRAPER}>."
else
    echo "Starting new job for spider <${SCRAPER}>."
fi

CURR_JOB="${JOB_DIR}/${JOBTAG}"

# Scrapy insists on reading scrapy.cfg from the current dir, so we need to cd
cd "${BASE_DIR}"

exec scrapy crawl "${SCRAPER}" \
    --output "${FEEDS_DIR}/%(name)s/%(class)s/%(time)s.jl" \
    --set "JOBDIR=${CURR_JOB}" \
    --set "DONT_RUN_BEFORE_FILE=${DONT_RUN_BEFORE_FILE}"
