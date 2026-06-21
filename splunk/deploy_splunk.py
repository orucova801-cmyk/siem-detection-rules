#!/usr/bin/env python3
"""
deploy_splunk.py
-----------------
GitHub repo-dakı rules/*.json fayllarını oxuyub Splunk-a Alert kimi göndərir.

İş axını:
  1) Rule-u GitHub repo-da rules/ qovluğunda .json faylı kimi yaz/redaktə et
  2) git pull ilə Splunk serverinə (və ya istənilən hostа) çək
  3) Bu skripti işlət -> hər rule API ilə yaradılır (yoxdursa) və ya yenilənir (varsa)

İstifadə:
  export SPLUNK_USER="Aytac"
  export SPLUNK_PASS="..."
  python3 deploy_splunk.py [rules_qovluğu_yolu]
"""

import json
import os
import sys
import glob
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Konfiqurasiya: şifrə skriptin içində saxlanmır, environment-dən oxunur ---
SPLUNK_USER = os.environ.get("SPLUNK_USER", "Aytac")
SPLUNK_PASS = os.environ.get("SPLUNK_PASS", "")
SPLUNK_URL = "https://127.0.0.1:8089/services/saved/searches"
RULES_DIR = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("RULES_DIR", "./rules")


def load_rules(rules_dir):
    """rules/ qovluğundakı hər .json faylını ayrı bir rule kimi oxuyur
    (GitHub repo strukturuna uyğun: hər fayl = 1 detection rule)."""
    rules = []
    for filepath in sorted(glob.glob(os.path.join(rules_dir, "*.json"))):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                rules.append(json.load(f))
            except json.JSONDecodeError as e:
                print(f"XƏTA: {filepath} JSON formatı xətalıdır -> {e}")
    return rules


def build_payload(rule):
    """Splunk REST API üçün payload qurur. Alert sahələri olmadan
    Splunk bunu sadəcə 'Report' kimi yaradır, 'Alert' kimi yox."""
    return {
        "name": rule["name"],
        "search": rule["search"],
        "cron_schedule": rule.get("cron_schedule", "*/5 * * * *"),
        "is_scheduled": "1",
        "description": rule.get("description", ""),
        "sharing": "app",

        # --- Alert kimi göstərilməsi üçün vacib sahələr ---
        "alert_type": rule.get("alert_type", "number of events"),
        "alert_comparator": rule.get("alert_comparator", "greater than"),
        "alert_threshold": str(rule.get("alert_threshold", 0)),
        "alert.severity": str(rule.get("severity", 3)),   # 1=Info ... 5=Critical
        "alert.track": "1",                                # Triggered Alerts panelinə yazılsın
        "alert.suppress": "0",

        # --- Axtarış zaman aralığı (yoxdursa alert işləməyəcək) ---
        "dispatch.earliest_time": rule.get("earliest_time", "-15m"),
        "dispatch.latest_time": rule.get("latest_time", "now"),
    }


def create_rule(rule):
    payload = build_payload(rule)
    return requests.post(SPLUNK_URL, auth=(SPLUNK_USER, SPLUNK_PASS), data=payload, verify=False)


def update_rule(rule):
    """Mövcud rule-u yeniləyir. Update endpoint-i /saved/searches/{name} formatındadır,
    body-də 'name' göndərilmir."""
    payload = build_payload(rule)
    payload.pop("name", None)
    update_url = f"{SPLUNK_URL}/{rule['name']}"
    return requests.post(update_url, auth=(SPLUNK_USER, SPLUNK_PASS), data=payload, verify=False)


def push_to_splunk(rule):
    print(f"[{rule['name']}] Splunk-a göndərilir...")
    response = create_rule(rule)

    if response.status_code == 201:
        print("  -> Uğurla yaradıldı (yeni Alert).")
    elif response.status_code == 409:
        print("  -> Artıq mövcuddur, yenilənir (update)...")
        update_response = update_rule(rule)
        if update_response.status_code == 200:
            print("  -> Uğurla yeniləndi.")
        else:
            print(f"  -> Yeniləmə xətası: {update_response.status_code} - {update_response.text[:200]}")
    else:
        print(f"  -> Xəta baş verdi: {response.status_code} - {response.text[:200]}")


def main():
    if not SPLUNK_PASS:
        print("XƏTA: SPLUNK_PASS environment variable təyin edilməyib.")
        print("İstifadə: export SPLUNK_PASS='şifrən' && python3 deploy_splunk.py")
        sys.exit(1)

    rules = load_rules(RULES_DIR)
    if not rules:
        print(f"XƏBƏRDARLIQ: '{RULES_DIR}' qovluğunda .json rule faylı tapılmadı.")
        sys.exit(1)

    print(f"{len(rules)} rule tapıldı, Splunk-a göndərilir...\n")
    for rule in rules:
        push_to_splunk(rule)


if __name__ == "__main__":
    main()
