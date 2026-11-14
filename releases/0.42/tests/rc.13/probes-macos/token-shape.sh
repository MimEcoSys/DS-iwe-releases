t=$(cat ~/.claude-oauth-token)
case "$t" in sk-ant-oat01-*) echo "начало: правильное (sk-ant-oat01-)";; sk-ant-*) echo "начало: sk-ant-, но не oat01";; *) echo "начало: не похоже на ключ Claude";; esac
echo "длина: ${#t}; пробелов/переводов строки: $(printf %s "$t" | tr -cd ' \n\r\t' | wc -c | tr -d ' '); не из [A-Za-z0-9_-]: $(printf %s "$t" | tr -d 'A-Za-z0-9_-' | wc -c | tr -d ' ')"
