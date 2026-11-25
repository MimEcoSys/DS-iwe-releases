#!/bin/bash
# usage: variant-digest.sh <raw log>...  — the marker lines and what update.sh itself said about the settings file
RT="$(cd "$(dirname "$0")/.." && pwd)"
for f in "$@"; do
  echo "=========== $(basename "$f" .raw.log)"
  grep -n '^###\|^  \.claude/settings\.json\|^  [✓⚠] \.claude/settings\.json\|^  ⚠ --apply\|^  --apply\|^    [→+ℹ⚠] \|^    Применить слияние\|^    settings-merge-apply\|^    applied:\|^    ⚠ предпросмотр\|Режим --check\|^Отменено\|^ВЕРДИКТ\|^Причина\|Обновление завершено\|ОШИБКА' "$f" \
    | grep -v '^[0-9]*:  + \|^[0-9]*:    + -' | sed "s#$RT#<RT>#g" | cut -c1-430
done
