#!/run/current-system/sw/bin/bash
# Re-create the disposable iwe-test user if a NixOS switch dropped it; home dir is kept as is.
if ! getent passwd iwe-test >/dev/null; then
  sudo useradd -u 1001 -g users -d /home/iwe-test -s /run/current-system/sw/bin/bash iwe-test \
    && sudo loginctl enable-linger iwe-test \
    && echo "$(date '+%F %T') iwe-test re-created" >> /home/<user>/iwe-rc5-linux/logs/user-guard.log
fi
