SyncX
A lightweight CLI tool for downloading, verifying, and preparing Linux distribution ISO images for bootable USB creation.

📋 Overview
SyncX simplifies the process of obtaining legitimate Linux distribution ISOs, verifying their integrity, and preparing them for creation of bootable recovery or installation media. It eliminates manual steps of searching for official downloads, checking checksums, and handling image preparation.

⚙️ Features
Automated ISO retrieval from official distribution mirrors
Integrity verification using SHA256/MD5 checksums
Distribution support for Ubuntu, Debian, Fedora, Arch, and others
Command-line interface suitable for scripting and automation
Zero dependencies beyond standard Linux utilities (curl/wget, sha256sum/md5sum)
Cross-platform compatibility works on any modern Linux distribution
📥 Installation
Code
· bash
# Clone the repository
git clone https://github.com/yourusername/SyncX.git
cd SyncX

# Make the script executable
chmod +x syncx

# Optional: Install system-wide
sudo cp syncx /usr/local/bin/
💻 Usage
List available distributions
Code
· bash
syncx --list
Download an ISO
Code
· bash
# Download Ubuntu 22.04 LTS desktop ISO
syncx --distro ubuntu --version 22.04 --flavor desktop

# Download Fedora 38 workstation ISO
syncx --distro fedora --version 38 --flavor workstation
Verify an existing ISO
Code
· bash
syncx --verify /path/to/downloaded.iso
Prepare ISO for USB creation
Code
· bash
syncx --prepare ubuntu-22.04-desktop-amd64.iso
# Output: Ready image at ubuntu-22.04-desktop-amd64.iso.prepared
Full workflow example
Code
· bash
syncx --distro ubuntu --version 22.04 --flavor desktop --verify --prepare
🔧 Requirements
Bash 4.0+
Either curl or wget for downloads
Either sha256sum or md5sum for verification
Standard Linux userland utilities (grep, sed, etc.)
🤝 Contributing
Fork the repository
Create a feature branch (git checkout -b feature/improvement)
Make your changes
Commit (git commit -m "Description of changes")
Push to the branch (git push origin feature/improvement)
Open a Pull Request
📄 License
This project is licensed under the MIT License - see the LICENSE [blocked] file for details.

📌 Notes
All ISOs are downloaded directly from official distribution mirrors
Checksums are verified against official sources when available
Prepared images are optimized for use with dd or similar USB writing tools
Network connectivity is required for ISO downloads and verification
SyncX: Simplifying Linux ISO management since 2024.
