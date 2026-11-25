#!/bin/bash
echo "launchctl $*" >> "${STUB_LOG:-/dev/null}"
[ "$1" = list ] && exit 1
exit 0
