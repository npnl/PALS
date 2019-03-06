#!/bin/bash
set -e
source ~/.pals-env.sh

git pull > /dev/null 2>&1

if [[ $1 == "" ]]; then
	/usr/bin/python run_pals.py -s --docker -c /config/*.json

elif [[ $1 == "-d" ]]; then
	/usr/bin/python run_pals.py -d -s --docker -c /config/*.json
else
	exec "$@"
fi

