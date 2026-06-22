# SIEM Detection Rules

Bu repo, SIEM platformaları (Splunk, QRadar) üçün detection rule-ların **mərkəzləşdirilmiş mənbəyi**dir. Bütün rule-lar burada yazılır, versiyalaşdırılır və REST API vasitəsilə avtomatik olaraq SIEM-lərə tətbiq edilir.

## Arxitektura / İş Axını

```
┌─────────────┐      git push      ┌─────────────┐      REST API      ┌─────────────┐
│   GitHub    │  ───────────────►  │  Deploy VM  │  ───────────────►  │    SIEM     │
│  (mənbə)    │  ◄───────────────  │  (skript)   │                    │  (Splunk)   │
└─────────────┘      git pull      └─────────────┘                    └─────────────┘
```

**Prinsip:** Rule-lar heç vaxt SIEM-in özündə birbaşa redaktə edilmir. Hər dəyişiklik bu ardıcıllıqla gedir:

1. Rule (`.json` faylı) bu repoda yazılır/redaktə edilir
2. GitHub-a commit + push edilir
3. SIEM serverinə `git pull` ilə çəkilir
4. `deploy_*.py` skripti rule-u REST API ilə SIEM-ə göndərir (yeni rule yaranır və ya mövcud olan yenilənir)

## Repo Strukturu

```
siem-detection-rules/
├── README.md
└── splunk/
    ├── deploy_splunk.py       # Splunk-a göndərmə/yeniləmə skripti
    └── rules/
        ├── owasp-a01-idor-detection.json
        ├── owasp-a01-privilege-escalation-detection.json
        ├── owasp-a02-cleartext-credentials-detection.json
        ├── owasp-a03-sqli-detection.json
        ├── owasp-a03-xss-detection.json
        ├── owasp-a03-command-injection-detection.json
        ├── owasp-a04-business-logic-abuse-detection.json
        ├── owasp-a05-sensitive-file-access-detection.json
        ├── owasp-a06-vulnerable-component-scan-detection.json
        ├── owasp-a07-brute-force-login-detection.json
        ├── owasp-a07-credential-stuffing-detection.json
        ├── owasp-a08-webshell-upload-detection.json
        ├── owasp-a09-audit-log-tampering-detection.json
        ├── owasp-a10-ssrf-detection.json
        └── network-port-scan-detection.json
```

## Splunk Detection Rules (15)

Bütün rule-lar OWASP Top 10 (2021) kateqoriyalarını əhatə edir, MITRE ATT&CK tagləri ilə işarələnib və real SOC mühitindəki false-positive ssenarilərini nəzərə alır.

| # | Rule adı | OWASP Kateqoriyası | MITRE ATT&CK | Severity |
|---|---|---|---|---|
| 1 | OWASP_A03_SQLi_Detection | A03 - Injection | T1190 | 4 |
| 2 | OWASP_A03_XSS_Detection | A03 - Injection | T1059.007 | 4 |
| 3 | OWASP_A03_Command_Injection_Detection | A03 - Injection | T1059 | 5 |
| 4 | OWASP_A01_IDOR_Enumeration_Detection | A01 - Broken Access Control | T1190 | 4 |
| 5 | OWASP_A01_Privilege_Escalation_Detection | A01 - Broken Access Control | T1078, T1098 | 5 |
| 6 | OWASP_A02_Cleartext_Credentials_In_Logs | A02 - Cryptographic Failures | T1552.001 | 4 |
| 7 | OWASP_A04_Excessive_Password_Reset_Requests | A04 - Insecure Design | T1110 | 3 |
| 8 | OWASP_A05_Sensitive_File_Exposure_Attempt | A05 - Security Misconfiguration | T1592 | 5 |
| 9 | OWASP_A06_Vulnerability_Scanner_Detection | A06 - Vulnerable Components | T1595.002 | 4 |
| 10 | OWASP_A07_Brute_Force_Login_Detection | A07 - Authentication Failures | T1110.001 | 4 |
| 11 | OWASP_A07_Credential_Stuffing_Detection | A07 - Authentication Failures | T1110.004 | 5 |
| 12 | OWASP_A08_Webshell_Upload_Detection | A08 - Data Integrity Failures | T1505.003 | 5 |
| 13 | OWASP_A09_Audit_Log_Tampering_Detection | A09 - Logging & Monitoring Failures | T1070.001 | 5 |
| 14 | OWASP_A10_SSRF_Detection | A10 - SSRF | T1190, T1078.004 | 5 |
| 15 | NET_Port_Scan_Reconnaissance_Detection | Network Recon (Pre-Attack) | T1595.001 | 3 |

## Rule Faylı Formatı

Hər rule Sigma-bənzər struktur daşıyan `.json` faylıdır:

```json
{
  "name": "Rule_Adi",
  "description": "Rule-un nə aşkar etdiyinin izahı",
  "search": "Splunk SPL sorğusu",
  "severity": 1-5,
  "alert_type": "number of events",
  "alert_comparator": "greater than",
  "alert_threshold": 0,
  "earliest_time": "-15m",
  "latest_time": "now",
  "cron_schedule": "*/5 * * * *",
  "mitre_attack": ["T-kodları"],
  "owasp_category": "OWASP Top 10 kateqoriyası",
  "false_positives": "Bilinən false-positive ssenariləri"
}
```

## İstifadə Qaydası

```bash
# Repo-nu çək
git clone https://github.com/orucova801-cmyk/siem-detection-rules.git
cd siem-detection-rules/splunk

# Splunk credential-larını environment variable kimi təyin et
export SPLUNK_USER="istifadeci_adin"
export SPLUNK_PASS="sifren"

# Bütün rule-ları Splunk-a göndər (yeni olanlar yaranır, mövcud olanlar yenilənir)
python3 deploy_splunk.py ./rules
```

Skript hər rule üçün avtomatik olaraq:
- Splunk-da mövcud deyilsə → **yaradır** (HTTP 201)
- Artıq mövcuddursa → **yeniləyir** (HTTP 409 → update)

## Müəllif

Aytac — İnformasiya Təhlükəsizliyi, MilliSec

