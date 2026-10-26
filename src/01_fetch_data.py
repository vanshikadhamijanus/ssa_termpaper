"""
Step 1 - download every scriptable data source into data/raw/ and write
data/raw/MANIFEST.csv (what was fetched, when, size, sha256, status).

Uses only the Python standard library, so it runs before any pip install.

    python src/01_fetch_data.py               # fetch anything not yet on disk
    python src/01_fetch_data.py --force       # re-download everything
    python src/01_fetch_data.py --only weather datagovsg
"""
import argparse
import csv
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sources as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANUAL_DIR = ROOT / "data" / "manual"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def http_get(url, retries=6, timeout=90):
    """GET with exponential backoff (data.gov.sg rate-limits bursts)."""
    delay = 3
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            code = getattr(e, "code", None)
            if code in (403, 404) or attempt == retries:
                raise
            print(f"    retry {attempt}/{retries} after {delay}s ({e})")
            time.sleep(delay)
            delay *= 2


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def record(rows, kind, title, url, path, status, note=""):
    rows.append({
        "kind": kind, "title": title, "url": url,
        "file": str(path.relative_to(ROOT)) if path else "",
        "bytes": path.stat().st_size if path and path.exists() else "",
        "sha256_16": sha256(path) if path and path.exists() else "",
        "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "status": status, "note": note,
    })


# --------------------------------------------------------------------------
def fetch_datagovsg(rows, force):
    out = RAW / "datagovsg"
    out.mkdir(parents=True, exist_ok=True)
    for ds_id, fname, title, _ in S.DATAGOVSG:
        path = out / fname
        url = f"https://data.gov.sg/api/action/datastore_search?resource_id={ds_id}&limit=10000"
        if path.exists() and not force:
            record(rows, "datagovsg", title, url, path, "cached")
            continue
        print(f"  data.gov.sg  {fname}")
        for attempt in range(6):
            payload = json.loads(http_get(url))
            if "result" in payload:  # rate-limited responses come back without 'result'
                break
            time.sleep(5 * (attempt + 1))
        else:
            record(rows, "datagovsg", title, url, None, "FAILED", str(payload)[:120])
            continue
        res = payload["result"]
        fields = [f["id"] for f in res["fields"] if f["id"] != "_id"]
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(res["records"])
        record(rows, "datagovsg", title, url, path, "ok", f"{len(res['records'])} rows")
        time.sleep(3)  # stay under the anonymous rate limit


def fetch_weather(rows, force):
    """Hourly Open-Meteo archive for Jurong Island (model selection not pinned)."""
    out = RAW / "weather"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"openmeteo_{S.SITE['name'].replace(' ', '_').lower()}_hourly_{min(S.WEATHER_YEARS)}_{max(S.WEATHER_YEARS)}.csv"
    base = "https://archive-api.open-meteo.com/v1/archive"
    if path.exists() and not force:
        record(rows, "openmeteo", "Open-Meteo hourly weather", base, path, "cached")
        return
    variables = ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "wet_bulb_temperature_2m"]
    n = 0
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["time"] + variables)
        for yr in S.WEATHER_YEARS:
            q = urllib.parse.urlencode({
                "latitude": S.SITE["lat"], "longitude": S.SITE["lon"],
                "start_date": f"{yr}-01-01", "end_date": f"{yr}-12-31",
                "hourly": ",".join(variables), "timezone": "Asia/Singapore",
            })
            print(f"  open-meteo   {yr}")
            h = json.loads(http_get(f"{base}?{q}"))["hourly"]
            for i, t in enumerate(h["time"]):
                w.writerow([t] + [h[v][i] for v in variables])
                n += 1
            time.sleep(1)
    record(rows, "openmeteo", f"Open-Meteo hourly weather, {S.SITE['name']}", base, path, "ok", f"{n} hourly rows")


def fetch_csv(rows, force):
    out = RAW / "csv"
    out.mkdir(parents=True, exist_ok=True)
    for url, fname, title, _ in S.CSV:
        path = out / fname
        if path.exists() and not force:
            record(rows, "csv", title, url, path, "cached")
            continue
        print(f"  csv          {fname}")
        path.write_bytes(http_get(url))
        record(rows, "csv", title, url, path, "ok")


def fetch_documents(rows, force):
    out = RAW / "docs"
    out.mkdir(parents=True, exist_ok=True)
    for url, fname, title, _ in S.DOCUMENTS:
        path = out / fname
        if path.exists() and not force:
            record(rows, "document", title, url, path, "cached")
            continue
        print(f"  document     {fname}")
        try:
            data = http_get(url)
        except Exception as e:  # keep going; a missing snapshot is not fatal
            record(rows, "document", title, url, None, "FAILED", str(e)[:120])
            continue
        if fname.endswith(".pdf") and not data.startswith(b"%PDF"):
            record(rows, "document", title, url, None, "FAILED", "response was not a PDF")
            continue
        path.write_bytes(data)
        record(rows, "document", title, url, path, "ok")
        time.sleep(1)


def check_manual(rows):
    MANUAL_DIR.mkdir(parents=True, exist_ok=True)
    recorded = set()
    for title, url, pattern, note in S.MANUAL:
        hits = sorted(MANUAL_DIR.glob(pattern))
        status = "present" if hits else "MANUAL - not yet downloaded"
        if not hits:
            record(rows, "manual", title, url, None, status, note)
        for path in hits:
            record(rows, "manual", title, url, path, status, note)
            recorded.add(path)
    # A downloaded file must not disappear from the inventory merely because
    # an old registry pattern missed it. Leave provenance explicitly unknown.
    for path in sorted(MANUAL_DIR.iterdir()):
        if path.is_file() and path.suffix.lower() in {".pdf", ".xlsx", ".csv"} and path not in recorded:
            record(rows, "manual", path.name, "", path, "present - registry mapping needed",
                   "Local source exists; exact source URL not established by this registry")


STEPS = {"datagovsg": fetch_datagovsg, "weather": fetch_weather, "csv": fetch_csv, "docs": fetch_documents}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="re-download files already on disk")
    ap.add_argument("--only", nargs="+", choices=STEPS, help="run only these steps")
    args = ap.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, fn in STEPS.items():
        if args.only and name not in args.only:
            continue
        print(f"[{name}]")
        try:
            fn(rows, args.force)
        except Exception as e:
            print(f"  !! {name} failed: {e}")
            record(rows, name, name, "", None, "FAILED", str(e)[:120])
    check_manual(rows)

    manifest = RAW / "MANIFEST.csv"
    with manifest.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    bad = [r for r in rows if r["status"] == "FAILED"]
    todo = [r for r in rows if r["status"].startswith("MANUAL")]
    print(f"\nManifest: {manifest.relative_to(ROOT)}  ({len(rows)} entries, {len(bad)} failed, {len(todo)} manual to-do)")
    for r in bad:
        print(f"  FAILED  {r['title']}: {r['note']}")
    for r in todo:
        print(f"  MANUAL  {r['title']}")


if __name__ == "__main__":
    main()
