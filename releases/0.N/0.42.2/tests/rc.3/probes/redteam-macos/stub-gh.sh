#!/bin/bash
# Test stub: no GitHub account actions. Only anonymous clone of public base repos.
echo "gh $*" >> "${STUB_LOG:-/dev/null}"
if [ "$1" = repo ] && [ "$2" = clone ]; then
  case "$3" in
    TserenTserenov/ZP|ailev/FPF|TserenTserenov/SPF)
      exec /usr/bin/git clone --depth=1 --quiet "https://github.com/$3.git" "$4" ;;
  esac
fi
exit 1
