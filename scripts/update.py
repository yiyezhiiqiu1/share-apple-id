"""Read public 52id region endpoints; publish aggregate counts only."""
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
REGIONS = (("us", "美区"), ("jp", "日区"), ("hk", "港区"), ("tw", "台湾地区"), ("cn", "中国大陆"))

def summarize(payload):
    accounts = payload.get("accounts") if isinstance(payload, dict) else None
    if not isinstance(accounts, list) or not accounts or any(not isinstance(a, dict) for a in accounts):
        raise ValueError("接口没有返回有效账号列表，保留上次发布内容")
    counts = {"normal": 0, "abnormal": 0, "unknown": 0}
    for account in accounts:
        # Match the site's displayed status precedence; never serialize source records.
        values = (account.get("status"), account.get("last_check_success"))
        if any(v is True or type(v) is int and v == 1 for v in values):
            counts["normal"] += 1
        elif any(v is False or type(v) is int and v == 0 for v in values):
            counts["abnormal"] += 1
        else:
            counts["unknown"] += 1
    return {"count": len(accounts), **counts}

def collect():
    rows = []
    for code, label in REGIONS:
        request = Request(f"https://52id.org/api-getappleid?region=apple{code}", headers={"Accept": "application/json", "User-Agent": "52id-github-daily/1.0"})
        with urlopen(request, timeout=25) as response:
            if response.status != 200:
                raise ValueError(f"{code}: HTTP {response.status}")
            payload = json.load(response)
        rows.append({"region": label, "url": f"https://52id.org/apple-id-{code}.html", **summarize(payload)})
    return rows

def publish(rows):
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    snapshot = {"fetched_at": now.isoformat(timespec="seconds"), "timezone": "Asia/Shanghai", "regions": rows}
    lines = [f"| [{r['region']}]({r['url']}) | {r['count']} | {r['normal']} | {r['abnormal']} | {r['unknown']} |" for r in rows]
    template = (ROOT / "README.template.md").read_text(encoding="utf-8")
    readme = template.replace("{{FETCHED_AT}}", now.strftime("%Y-%m-%d %H:%M:%S")).replace("{{REGION_ROWS}}", "\n".join(lines))
    if "{{" in readme:
        raise ValueError("README 模板存在未填写字段")
    # All requests and validation finish before any published file is changed.
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data/latest.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(f"已同步 {len(rows)} 个地区的接口统计；没有保存账号或密码。")

if __name__ == "__main__":
    publish(collect())
