until [ "$(curl -s https://api.github.com/rate_limit | jq .resources.core.remaining)" -ge 50 ] 2>/dev/null; do sleep 30; done
sudo -n -u iwe-test -i bash /private/tmp/iwe-rc13-probes/row4b.sh
