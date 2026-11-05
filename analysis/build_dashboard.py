"""Builds DATA_FINAL/dashboard/Dashboard.html: ONE self-contained page (data and charts inside, works offline, no internet needed).
Usage: python analysis/build_dashboard.py   (writes dashboard/index.html; run analysis/build_kpis.py first, or use analysis/update_dashboard.py)"""
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); B = f"{R}/dashboard"
public = True
pay = json.load(open(f"{B}/payload.json"))
if public:
    pay["public"] = True
    pay["customers"] = [[c[0], "Customer " + c[0], c[2], ""] for c in pay["customers"]]
    pay["cost"] = dict(method=None, rows=[], note="not shown in the public version", warnings=[])
tpl = open(f"{B}/template.html", encoding="utf-8").read()
js = open(f"{B}/lib/chart.umd.js", encoding="utf-8").read()
data = json.dumps(pay, separators=(",", ":")).replace("</", "<\\/")
html = tpl.replace("/*__PAYLOAD__*/", data).replace("/*__CHARTJS__*/", js.replace("</script", "<\\/script"))
page = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n' + html + "\n</html>\n"
out = f"{B}/index.html"
open(out, "w", encoding="utf-8").write(page)
print("written", out, f"({len(page) / 1e6:.2f} MB)")
