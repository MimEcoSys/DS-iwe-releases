# Check that every step of RMP.1:4.1 from the FPF source appears verbatim in the agent's answer.
# Usage: python3 -I verbatim-check.py <fpf-source.md> <answer.md>
import re, sys
src = open(sys.argv[1]).read()
ans = open(sys.argv[2]).read()
sec = src[src.index("#### RMP.1:4.1"):]
sec = sec[:sec.index("\n#### ", 5)]
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"^\s*[-*>]\s+", "", s, flags=re.M)).replace("**", "").strip()
steps = re.findall(r"^\d\. (.*?)(?=^\d\. |\Z)", sec, flags=re.M | re.S)
print("шагов в источнике:", len(steps))
for i, s in enumerate(steps, 1):
    print(i, "дословно" if norm(s) in norm(ans) else "РАСХОДИТСЯ")
