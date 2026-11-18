# Common environment for every probe run as iwe-test: clean PATH without the operator's home, test-only gh stub first.
[ "$HOME" = /Users/iwe-test ] || { echo "НЕ тот HOME: $HOME" >&2; exit 97; }
export PATH="$HOME/iwe-rc13-macos/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
unset $(env | grep -oE '^IWE_[A-Z_]+' ) 2>/dev/null
export RC=v0.42.0-rc.13 PREV=v0.41.11 W="$HOME/iwe-rc13-macos"
export GIT_TERMINAL_PROMPT=0
