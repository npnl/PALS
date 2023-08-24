#!/bin/bash
set -e
source ~/.pals-env.sh

git config user.email "docker@pals.com"
git config user.name "Docker"

# git fetch --all > /dev/null 2>&1
# git reset --hard origin/master > /dev/null 2>&1

if [[ $1 == "" ]]; then
	/usr/bin/python3.7 run_pals.py -s --docker -c /config/*.json

elif [[ $1 == "-d" ]]; then
	/usr/bin/python3.7 run_pals.py -d -s --docker -c /config/*.json
else
	exec "$@"
fi

