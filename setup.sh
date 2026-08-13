#!/usr/bin/env bash
# Setup script for Advanced Reconnaissance Scanner v2.0

set -e

echo -e "\n[+] Advanced Reconnaissance Scanner Setup\n"

# Update package lists
echo "[+] Updating package lists..."
sudo apt update -qq

# ============ Install System Packages ============
echo "[+] Installing system dependencies (this may take a while)..."
sudo apt install -y \
    nmap \
    whois \
    curl \
    git \
    golang-go \
    python3-pip \
    proxychains-ng \
    tor \
    chromium \
    xvfb \
    dirb \
    gobuster \
    ffuf \
    exploitdb \
    theharvester \
    dmitry \
    finger \
    rpcbind \
    nfs-common \
    smbclient \
    enum4linux \
    ldap-utils \
    netcat-openbsd \
    recon-ng \
    seclists \
    wget \
    sudo

# ============ Install Python Packages ============
echo "[+] Installing Python packages from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt
else
    echo "[!] requirements.txt not found. Installing core packages..."
    pip3 install requests PySocks pyyaml dnspython urllib3 --break-system-packages 2>/dev/null || pip3 install requests PySocks pyyaml dnspython urllib3
fi

# ============ Install Go Tools ============
echo "[+] Setting up Go environment..."
export GOPROXY=direct
export GOSUMDB=off
export GO111MODULE=on
export PATH=$PATH:$(go env GOPATH)/bin

# Install Subfinder
echo "[+] Installing Subfinder..."
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Install HTTPX
echo "[+] Installing HTTPX..."
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# Install Katana
echo "[+] Installing Katana..."
go install github.com/projectdiscovery/katana/cmd/katana@latest

# ============ Install TruffleHog (pre-built binary) ============
echo "[+] Installing TruffleHog v3.96.0..."
TRUFFLEHOG_VERSION="3.96.0"
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"
wget -q "https://github.com/trufflesecurity/trufflehog/releases/download/v${TRUFFLEHOG_VERSION}/trufflehog_${TRUFFLEHOG_VERSION}_linux_amd64.tar.gz"
tar -xzf "trufflehog_${TRUFFLEHOG_VERSION}_linux_amd64.tar.gz"
sudo mv trufflehog /usr/local/bin/
sudo chmod +x /usr/local/bin/trufflehog
cd - > /dev/null
rm -rf "$TMP_DIR"

# ============ Install GitHacker ============
echo "[+] Installing GitHacker..."
pip3 install githacker --break-system-packages 2>/dev/null || pip3 install githacker

# ============ Install Pagodo ============
echo "[+] Installing Pagodo..."
cd /tmp
rm -rf pagodo
git clone https://github.com/opsdisk/pagodo.git
cd pagodo
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt
sudo ln -sf /tmp/pagodo/pagodo.py /usr/local/bin/pagodo
cd - > /dev/null

# ============ Install uDork ============
echo "[+] Installing uDork..."
cd /tmp
rm -rf uDork
git clone https://github.com/m3n0sd0n4ld/uDork.git
cd uDork
sudo cp uDork.sh /usr/local/bin/udork
sudo chmod +x /usr/local/bin/udork
cd - > /dev/null

# ============ Install Gowitness ============
echo "[+] Installing Gowitness..."
sudo apt install gowitness -y 2>/dev/null || (echo "Gowitness not available via apt. Installing from GitHub..." && \
    wget -q https://github.com/sensepost/gowitness/releases/latest/download/gowitness-linux-amd64 -O /tmp/gowitness && \
    sudo mv /tmp/gowitness /usr/local/bin/gowitness && sudo chmod +x /usr/local/bin/gowitness)

# ============ Start Tor service ============
echo "[+] Starting Tor service..."
sudo systemctl start tor || sudo service tor start
sudo systemctl enable tor || sudo update-rc.d tor defaults

# ============ Finalize ============
echo "[+] Adding ~/go/bin to PATH in ~/.bashrc..."
if ! grep -q 'export PATH=$PATH:~/go/bin' ~/.bashrc; then
    echo 'export PATH=$PATH:~/go/bin' >> ~/.bashrc
fi
export PATH=$PATH:~/go/bin

echo -e "\n[+] Setup complete! You can now run the scanner:\n"
echo "    python3 recon_scanner.py <target>"
echo "    or"
echo "    ./recon_scanner.py <target>"
echo
echo "    For anonymous scanning, ensure Tor is running and use the default proxy option."
echo "    Example: python3 recon_scanner.py example.com"
echo "    To disable proxy: python3 recon_scanner.py example.com --no-proxy"
echo
