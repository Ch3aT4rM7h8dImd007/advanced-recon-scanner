#  Advanced Recon Scanner – Proxychains4 Edition

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Kali%20Linux%20%7C%20Parrot%20%7C%20Ubuntu-lightgrey)](https://kali.org)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen)]()
[![Proxychains](https://img.shields.io/badge/proxy-proxychains4-orange)]()

> **All‑in‑one automated reconnaissance and OSINT tool – integrates 15+ powerful tools, supports proxychains4 for anonymous scanning, and generates a comprehensive detailed report.**

---

## 📖 What is Advanced Recon Scanner?

**Advanced Recon Scanner (ARS)** is a fully automated Python‑based reconnaissance framework that combines **more than 15 industry‑standard security tools** into a single, easy‑to‑use script. It performs a complete reconnaissance cycle on a target domain or IP:

- 🔎 **OSINT & Email Harvesting** – theHarvester (multi‑source).
- 🧠 **Information Gathering** – Dmitry (WHOIS, IP, port scan, Netcraft, email).
- 🌐 **DNS & Zone Transfer Testing** – dig, nslookup, host, Python DNS library.
- 📡 **Port Scanning** – Nmap (with service/OS detection).
- 🧩 **Subdomain Discovery** – Subfinder, crt.sh, HackerTarget, dig.
- ✅ **Live Host Validation** – HTTPX (probes, tech detection, title, etc.).
- 📸 **Screenshots** – Gowitness (headless Chromium).
- 🕸️ **URL Discovery** – Katana (advanced web crawler).
- 🔐 **Secret Scanning** – TruffleHog (detects hard‑coded secrets).
- 📂 **Git Repository Exposure** – GitHacker (finds `.git` folders).
- 📋 **Vulnerability Search** – Searchsploit (Exploit‑DB).
- 🔍 **Google Dorking** – WebDork (customised dork search).
- 🧾 **WHOIS & Netcraft** – domain registration and hosting details.
- 🎯 **Deep URL Analysis** – categorises URLs by sensitivity (admin panels, config files, API endpoints, etc.).

All traffic can be **anonymised** via **proxychains4** (Tor or any SOCKS/HTTP proxy), making it suitable for red‑team exercises and authorised penetration testing.

---

## ✨ Features at a Glance

| Category | Tools Included | Key Outputs |
|----------|----------------|-------------|
| **OSINT** | theHarvester (crtsh, HackerTarget, DuckDuckGo, DNSDumpster, ThreatCrowd, URLScan, Wayback, Shodan) | Emails, subdomains, hosts |
| **Information Gathering** | Dmitry (WHOIS, IP, port scan, Netcraft, email harvest) | Domain info, open ports, emails, server headers |
| **Port Scanning** | Nmap (–sV, –sC, –O, –A) | Open ports, services, OS guess |
| **Zone Transfer** | dig, nslookup, host, Python DNS | DNS records, vulnerability status |
| **Subdomain Discovery** | Subfinder, crt.sh, HackerTarget, dig | Subdomain lists |
| **Live Host Validation** | HTTPX (probe, title, tech‑detect, server, IP, CDN, TLS) | Alive URLs, technology stack |
| **Screenshots** | Gowitness (headless Chromium) | PNG screenshots of live hosts |
| **URL Discovery** | Katana (crawler with depth, filters, headless) | Discovered URLs |
| **Deep URL Analysis** | Custom analysis (regex patterns) | Categorised URLs (admin, config, API, etc.) |
| **Google Dorking** | WebDork (custom dorks) | URLs from Google searches |
| **Vulnerability Search** | Searchsploit (Exploit‑DB) | Relevant exploits |
| **Secret Scanning** | TruffleHog (filesystem, entropy, verified) | Detected secrets (keys, tokens) |
| **Git Exposure** | GitHacker | Downloaded `.git` repositories |
| **WHOIS & Netcraft** | whois command + Netcraft API | Domain registration, hosting, server, OS |
| **Proxy Anonymity** | proxychains4 (Tor, SOCKS5, HTTP) | Anonymous scanning |

---

## 🛠️ Installation

### Prerequisites

- **Operating System:** Kali Linux, Parrot OS, Ubuntu (or any Debian‑based).
- **Python 3.6+** (with `pip`).
- **Root/sudo privileges** (for installing tools and dependencies).
- **Internet connection** (to download tools and perform scans).

### Step 1: Clone the repository

```bash
git clone [https://github.com/yourusername/advanced-recon-scanner.git](https://github.com/yourusername/advanced-recon-scanner.git)
cd advanced-recon-scanner
```

### Step 2: Make the script executable

```bash
chmod +x recon_scanner.py
```

### Step 3: Run the script – it will automatically install all missing dependencies

```bash
sudo python3 recon_scanner.py example.com
```

> **Note:** The script will prompt you for proxy usage during the first run. All installations are handled automatically via `apt`, `pip`, and `go`.

### Step 4: (Optional) Configure Shodan API key for theHarvester

Edit the script and set your Shodan key:

```python
SHODAN_API_KEY = "your_shodan_api_key_here"
```

Or set it as an environment variable:

```bash
export SHODAN_API_KEY="your_key"
```

The script will also attempt to write the key to `/etc/theHarvester/api-keys.yaml`.

---

## 🚀 Usage

### Basic Usage (with proxychains)

```bash
sudo python3 recon_scanner.py example.com
```

You will be prompted:

```text
Use proxychains4 for anonymity? (y/n, default: y):
```

Press `y` to enable proxychains (Tor required) or `n` to scan directly.

### Disable proxychains via command line

```bash
sudo python3 recon_scanner.py example.com --no-proxy
# or
sudo python3 recon_scanner.py example.com -np
```

### Specify a target directly (non‑interactive)

```bash
sudo python3 recon_scanner.py 192.168.1.1
```

### Scan a domain and use custom output directory

The script always creates a timestamped directory (e.g., `recon_results_20260101_120000`). You cannot change it via command line, but you can modify the code.

---

## 🖥️ Example Terminal Output (Abridged)

```text
╔═══════════════════════════════════════════════════════════════════╗
║     ADVANCED RECONNAISSANCE SCANNER v2.0 - PROXYCHAINS4 EDITION ║
║     Complete OSINT & Web Reconnaissance Tool                    ║
║     Kali Linux Optimized - Anonymous Scanning                   ║
╚═══════════════════════════════════════════════════════════════════╝

🎯 Target: example.com
📁 Results: recon_results_20260101_120000
🔒 Proxy: Enabled (Proxychains4)

======================================================================
📦 STEP 0: Checking Dependencies
   ✅ All required tools are already installed.

📦 STEP 1: Installing All Required Tools
   ✅ Go is installed
   ✅ pip3 is installed
   ✅ subfinder already installed
   ✅ httpx already installed
   ...

📦 STEP 2: theHarvester - OSINT Email & Subdomain Harvesting
======================================================================
🔍 THEHARVESTER - OSINT EMAIL & SUBDOMAIN HARVESTING
======================================================================
✅ theHarvester is installed
✅ Shodan API key configured

📝 Test: 01_Crtsh
   Certificate Transparency logs
   CMD: theHarvester -d example.com -l 50 -b crtsh
   🔄 Searching...
      🌐 crtsh.example.com
      📧 admin@example.com
   ✅ Completed in 2.34s. Saved to recon_results_.../theharvester_01_Crtsh.txt

📊 THEHARVESTER SUMMARY
======================================================================
Total tests: 12
✅ Successful: 12
📧 Emails Found: 45
🌐 Subdomains Found: 120
📁 Emails saved to .../theharvester_emails.txt
📁 Subdomains saved to .../theharvester_subdomains.txt

📦 STEP 3: DMITRY - Complete Information Gathering
======================================================================
🔍 DMITRY - COMPLETE INFORMATION GATHERING (ALL OPTIONS)
======================================================================
✅ Dmitry is installed

📝 [1/7] 01_Whois_Lookup
   Flag: -w
   CMD: dmitry -w example.com
      📋 Domain Name: example.com
      📍 IP Address: 93.184.216.34
      ...
   ✅ Completed (3.12s)
   📁 Saved: recon_results_.../dmitry/dmitry_whois.txt

📊 DMITRY - COMPLETE SCAN SUMMARY
======================================================================
Total tests: 7
✅ Successful: 7
📍 IP Addresses Found: 1
📧 Total Emails Found: 12
🔓 Total Open Ports Found: 4
...
... (continues for each step)
```

After all steps, a `FINAL_REPORT.md` and `report.json` are generated in the results directory.

---

## ⚙️ How It Works (Flow Diagram)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            START SCAN                                       │
│        User provides target domain/IP and proxy preference                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PHASE 0: DEPENDENCY CHECK & INSTALL                    │
│  • Check for required tools (nmap, go, git, pip, etc.)                    │
│  • Auto‑install missing packages via apt, pip, go                         │
│  • Set up proxychains4 and Tor (if proxy enabled)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 PHASE 1: OSINT & INFORMATION GATHERING                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. theHarvester (12 sources) – emails, subdomains, hosts           │   │
│  │    Sources: crtsh, hackertarget, duckduckgo, dnsdumpster,          │   │
│  │    threatcrowd, urlscan, waybackarchive, shodan (if key set),      │   │
│  │    multi‑source combinations, DNS brute, takeover check.           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 2. Dmitry (7 options) – WHOIS, IP info, port scan, Netcraft,       │   │
│  │    email harvest, full WHOIS, verbose/debug modes.                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 3. WHOIS (7 variants) – standard, Verisign, IANA, ARIN, port 43,  │   │
│  │    IANA query, no‑recursion, verbose.                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 4. Netcraft – server, OS, IP, hosting, country, organisation,      │   │
│  │    nameservers, registrar, dates, SSL, rank, status.               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  PHASE 2: DNS & NETWORK RECONNAISSANCE                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 5. Zone Transfer Testing (9 methods):                              │   │
│  │    • dig axfr (plain, +short, +multiline, -p 53)                  │   │
│  │    • nslookup -type=any                                            │   │
│  │    • host -l                                                       │   │
│  │    • Python dns library                                            │   │
│  │    • DNS Rebind attack test                                        │   │
│  │    • DNS Cache snooping                                            │   │
│  │    Deep verification with record extraction (subdomains, IPs, MX, │   │
│  │    TXT, CNAME, internal IPs).                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 6. Nmap port scan – scans 25+ interesting ports with -sV -sC -O   │   │
│  │    -A -T4, saves XML and text output.                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   PHASE 3: SUBDOMAIN ENUMERATION & LIVE CHECK              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 7. Subfinder (full + simple) – uses multiple sources.              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 8. Subdomain Discovery (crt.sh + HackerTarget + dig) – also        │   │
│  │    performs wildcard detection and filters valid subdomains.       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 9. HTTPX – for each discovered subdomain, probes all open ports    │   │
│  │    (from Nmap) with follow‑redirects, tech detection, TLS, etc.    │   │
│  │    Saves live hosts list.                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  PHASE 4: WEB & APPLICATION RECONNAISSANCE                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 10. Gowitness – takes screenshots of all live hosts using headless │   │
│  │     Chromium (auto‑installs xvfb and chromium).                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 11. Katana – runs 15 different crawl configurations (basic, depth, │   │
│  │     headless, JS extraction, filter, JSON, verbose, etc.) with     │   │
│  │     a 120‑second timeout per test. Saves all discovered URLs.      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 12. Deep URL Analysis – categorises all collected URLs into        │   │
│  │     ~30 categories: admin panels, sensitive files, API endpoints,  │   │
│  │     upload endpoints, config files, backup files, login pages,     │   │
│  │     database files, log files, debug pages, git repos, env files,  │   │
│  │     php info, server status, XML sitemap, robots.txt, crossdomain, │   │
│  │     graphql, swagger, CMS (WordPress/Joomla/Drupal), ecommerce,    │   │
│  │     payment, user data, admin actions, parameters, potential IDOR, │   │
│  │     SQLi, XSS, LFI, RFI, development, staging, etc.               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 PHASE 5: VULNERABILITY & SECRET DISCOVERY                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 13. WebDork – Google dorking with a list of ~20 dorks, searches   │   │
│  │     pages 1‑2, saves results.                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 14. Searchsploit – runs 10+ vulnerability searches (basic, JSON,   │   │
│  │     verbose, exact, platform‑filtered, remote/local) and also      │   │
│  │     performs targeted searches for common vulnerability patterns.  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 15. TruffleHog – scans filesystem (with entropy and verified       │   │
│  │     modes) and also a public Git repo, outputs JSON and human      │   │
│  │     readable secrets.                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 16. GitHacker – for each live host, tries to access /.git and      │   │
│  │     downloads the repository if exposed (with brute‑force).        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHASE 6: REPORT GENERATION                           │
│                                                                             │
│  • Collect all outputs from all tools.                                    │
│  • Generate a detailed Markdown report (`FINAL_REPORT.md`) with:         │
│      - Executive summary (counts of subdomains, live hosts, ports, etc.) │
│      - Per‑tool detailed sections with sample outputs.                   │
│      - Deep URL analysis categories.                                     │
│      - Zone transfer details.                                            │
│      - List of all generated files with sizes.                           │
│      - Proxy information.                                                │
│      - Recommendations and disclaimer.                                   │
│  • Also generate a structured JSON report (`report.json`).              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SCAN COMPLETE – all results saved                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Output Structure

After a successful scan, a directory named `recon_results_YYYYMMDD_HHMMSS/` is created. Inside, you will find:

```text
recon_results_20260101_120000/
├── FINAL_REPORT.md                      # Complete detailed report
├── report.json                          # Structured JSON data
├── live_hosts.txt                       # Live hosts from HTTPX
├── subdomains_alt.txt                   # All subdomains (deduplicated)
├── open_ports.txt                       # Open ports from Nmap
├── dmitry/                              # Dmitry outputs
│   ├── dmitry_whois.txt
│   ├── dmitry_ip_info.txt
│   ├── dmitry_netcraft.txt
│   ├── dmitry_emails.txt
│   ├── dmitry_full_whois.txt
│   ├── dmitry_verbose.txt
│   └── dmitry_debug.txt
├── theharvester_*.txt                   # Per‑source theHarvester outputs
├── theharvester_emails.txt              # All harvested emails
├── theharvester_subdomains.txt          # All harvested subdomains
├── subfinder_all.txt                    # Subfinder output
├── nmap_scan.txt                        # Nmap text output
├── nmap_scan.xml                        # Nmap XML
├── httpx_all.txt                        # HTTPX raw output
├── live_hosts_list.txt                  # URLs of live hosts
├── screenshots/                         # Gowitness PNGs
│   ├── example_com.png
│   └── ...
├── katana_*.txt                         # Katana outputs (15 configs)
├── katana_all_urls.txt                  # All URLs from Katana
├── webdork_results.txt                  # WebDork results
├── searchsploit_*.txt                   # Various Searchsploit outputs
├── searchsploit_all_findings.txt        # Combined vulnerability findings
├── searchsploit_vulnerabilities.txt     # Targeted vulnerability search
├── trufflehog_*.json                    # TruffleHog JSON outputs
├── trufflehog_secrets.txt               # Human‑readable secrets
├── trufflehog_all_secrets.json          # All secrets in JSON
├── githacker_*.txt                      # GitHacker findings
├── githacker_<host>/                    # Downloaded .git repos (if found)
│   └── ...
├── whois_all.txt                        # Combined WHOIS results
├── netcraft_info.txt                    # Netcraft extracted info
├── netcraft_report.html                 # Full Netcraft page
├── zone_transfer_results.txt            # Zone transfer summary
├── zone_transfer_results.json           # Zone transfer JSON
├── zone_transfer_detailed_report.txt    # In‑depth zone transfer report
├── url_categories.json                  # Deep URL analysis categories
├── url_deep_analysis.txt                # Human‑readable URL analysis
└── DMITRY_COMPLETE_REPORT.txt           # Dmitry combined report
```

---

## ⚙️ Configuration

The script is highly customisable. Key parameters you may want to adjust:

| Setting | Location | Description |
|---------|----------|-------------|
| **Shodan API Key** | `SHODAN_API_KEY` global variable | Set to enable Shodan in theHarvester. |
| **Proxychains config** | `proxy_config` path | By default uses `/etc/proxychains4.conf`; creates a custom one if missing. |
| **Interesting ports** | `self.interesting_ports` list | Ports scanned by Nmap. |
| **HTTPX ports** | Uses the same open ports from Nmap. |
| **Katana test configs** | `test_configs` in `run_katana_all()` | Add/modify crawl configurations. |
| **Deep analysis patterns** | `patterns` dict in `analyze_urls_deep()` | Add custom regex patterns for URL categorisation. |
| **WebDork dorks** | `dorks.txt` file in `webdork_fixed/` | Customise Google dorks. |
| **TruffleHog version** | In `check_and_install_trufflehog()` | Change version if needed. |
| **Proxy enable/disable** | Command‑line `--no-proxy` or interactive prompt. |

---

## 🧪 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Proxychains not working** | Ensure Tor is running: `sudo systemctl start tor`. Check `/etc/proxychains4.conf` for correct proxy lines (`socks5 127.0.0.1 9050`). |
| **Tool installation fails** | Some tools require `sudo` – run the script with `sudo`. Check internet connectivity. |
| **theHarvester Shodan error** | Set `SHODAN_API_KEY` in the script or environment. |
| **Gowitness fails** | Ensure Chromium and `xvfb` are installed (script auto‑installs). On headless systems, you may need to set `DISPLAY=:99`. |
| **Katana times out** | The default timeout per test is 120 seconds; you can increase it in `run_katana_with_timeout()`. |
| **TruffleHog not found** | The script downloads v3.96.0 from GitHub; if that fails, install manually from [TruffleHog GitHub](https://github.com/trufflesecurity/trufflehog). |
| **Zone transfer fails** | Most DNS servers are secure; this is normal. The script will report no vulnerability if properly configured. |
| **Permission denied** | Run with `sudo` to allow tool installations and file writes. |
| **Report generation huge** | The report includes all tool outputs; you can reduce verbosity by modifying the `generate_report()` function. |

---

## 📦 Dependencies

### System Tools (auto‑installed)
- `nmap`, `whois`, `curl`, `git`, `tor`, `proxychains4`, `chromium`, `xvfb`, `finger`, `rpcbind`, `nfs-common`, `smbclient`, `enum4linux`, `ldap-utils`, `dmitry`, `theharvester`, `exploitdb` (`searchsploit`).
- **Go tools:** `subfinder`, `httpx`, `katana` (installed via `go install`).
- **Python packages:** `requests`, `PySocks`, `yaml`, `dnspython` (for zone transfer), and `trufflehog` (binary downloaded).
- **Git repos:** SecLists, pagodo, uDork (installed on demand).

### Python Version
- Python 3.6+ (all standard libraries except `requests` and `PySocks`).

---

## 📜 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is intended for educational and authorised testing purposes only.
Unauthorised scanning, enumeration, and exploitation may violate laws and terms of service. The authors are not responsible for any misuse, damage, or legal consequences. Always obtain proper written permission before testing any system.

---

## 🤝 Contributing

Contributions are welcome! You can help by:
- Adding new tools or integrations.
- Improving error handling and reporting.
- Adding support for more CMS detection or vulnerability checks.
- Enhancing the proxy rotation logic.
- Writing additional test configurations for Katana or WebDork.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

Please ensure your code follows the existing style and includes appropriate comments. For major changes, open an issue first to discuss.

---

## 📚 Resources

- [theHarvester GitHub](https://github.com/laramies/theHarvester)
- [Dmitry – Deepmagic Information Gathering Tool](https://github.com/jaygreig86/dmitry)
- [Nmap Documentation](https://nmap.org/docs.html)
- [Subfinder](https://github.com/projectdiscovery/subfinder)
- [HTTPX](https://github.com/projectdiscovery/httpx)
- [Katana](https://github.com/projectdiscovery/katana)
- [Gowitness](https://github.com/sensepost/gowitness)
- [TruffleHog](https://github.com/trufflesecurity/trufflehog)
- [Searchsploit (Exploit‑DB)](https://www.exploit-db.com/searchsploit)
- [Proxychains4](https://github.com/rofl0r/proxychains-ng)

---

## 📊 Badges

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Kali%2520Linux%2520%257C%2520Parrot%2520%257C%2520Ubuntu-lightgrey)](https://kali.org)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](http://makeapullrequest.com)

---

## 👨‍💻 Author

Your Name  
GitHub: [@yourusername](https://github.com/)

---

## 🙏 Acknowledgments

- All open‑source tool developers whose work makes this framework possible.
- The security community for continuous testing and feedback.

---

## 📌 Final Notes

### Quick Start

```bash
# Clone and run
git clone [https://github.com/yourusername/advanced-recon-scanner.git](https://github.com/yourusername/advanced-recon-scanner.git)
cd advanced-recon-scanner
sudo python3 recon_scanner.py example.com
```

### Pro Tips
- **Always use proxies** for real engagements to protect your identity.
- **Check `FINAL_REPORT.md` first** – it summarises all findings.
- **Use custom Shodan key** for better theHarvester results.
- **Combine results with other tools** (e.g., nuclei) for further exploitation.
- **Monitor disk space** – scans with many hosts can generate large outputs.

Made with ❤️ for the Security Community

[![Security Community](https://img.shields.io/badge/security-community-blue)](https://)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](http://makeapullrequest.com)
