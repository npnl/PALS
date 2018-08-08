#!/bin/bash
# entrypoint.sh file for starting the xvfb with better screen resolution, configuring and running the vnc server, pulling the code from git and then running the test.
export DISPLAY=:20
Xvfb :20 -screen 0 1366x768x16 &
x11vnc -passwd TestVNC -display :20 -N -forever &
cd /usr/qxf2_pom/qxf2-page-object-model/
git pull
pytest -B chrome -s -v > pytest_report.log
wait
