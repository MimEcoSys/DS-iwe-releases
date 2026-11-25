#!/bin/bash
echo "crontab $*" >> "${STUB_LOG:-/dev/null}"
if [ "$1" = -l ]; then echo "crontab: no crontab for tester" >&2; exit 1; fi
exit 0
