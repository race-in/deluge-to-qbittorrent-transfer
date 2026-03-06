# 🚀 Deluge → qBittorrent Auto Transfer Script

Automatically transfer torrents from Deluge to qBittorrent after they have seeded for a configurable amount of time.

This script connects to both torrent clients, detects completed torrents in Deluge, moves the torrent data to qBittorrent’s download folder, adds the torrent to qBittorrent, and removes it from Deluge.

---

# Features

- Works with Deluge 2.x
- Works with qBittorrent 4.x
- Automatically transfers seeded torrents
- Prevents duplicate torrents
- Moves torrent data instead of copying
- Safe dry-run mode
- Easy automation with cron

---

# Requirements

- Python 3.8+
- Deluge daemon running with RPC enabled
- qBittorrent Web UI enabled

Required Python packages:

deluge-client
qbittorrent-api

---

# Installation

Clone the repository

git clone https://github.com/race-in/deluge-to-qbittorrent-transfer.git
cd deluge-to-qbittorrent-transfer

Create virtual environment

python3 -m venv venv
source venv/bin/activate

Install dependencies

pip install deluge-client qbittorrent-api

or

pip install -r requirements.txt

---

# Configuration

Edit the variables at the top of the script:

DELUGE_HOST
DELUGE_PORT
DELUGE_USERNAME
DELUGE_PASSWORD

DELUGE_STATE_DIR
DELUGE_DOWNLOAD_DIR

QB_HOST
QB_PORT
QB_USERNAME
QB_PASSWORD

QB_DOWNLOAD_DIR

SEEDING_MINUTES

Example:

SEEDING_MINUTES = 5

This means torrents will transfer to qBittorrent after 5 minutes of seeding in Deluge.

---

# Usage

Test first using dry run

python deluge_to_qb.py --dry-run

This will show what the script would do without moving files.

Run normally

python deluge_to_qb.py

The script will:

1. Detect seeded torrents in Deluge
2. Move torrent data
3. Add the torrent to qBittorrent
4. Remove the torrent from Deluge

---

# Automation with Cron

To run the script automatically every minute:

crontab -e

Add this line:

* * * * * /home/khokan/deluge-venv/bin/python3 /home/khokan/deluge_to_qb.py >> /home/khokan/deluge_to_qb.log 2>&1

Now every minute the script will check for newly completed torrents and transfer them.

---

# How the Script Works

1. Connects to Deluge RPC
2. Fetches all torrents
3. Filters torrents that:
   - Are completed
   - Have seeded longer than configured time
4. Moves torrent data to qBittorrent directory
5. Adds torrent to qBittorrent with skip hash check
6. Removes torrent from Deluge

---

# Example Directory Layout

/home/khokan/torrents/

deluge/
    torrent_data

qbittorrent/
    torrent_data

After transfer the torrent moves from:

deluge → qbittorrent

---

# Notes

- Torrent data is moved, not copied
- Existing files will not be overwritten
- Script avoids duplicate torrents
- Ensure correct file permissions

---

# Troubleshooting

Connection error

systemctl status deluged

Torrent file not found

Check the directory:

~/.config/deluge/state

Permission error

Ensure the script user has access to:

Deluge download directory
qBittorrent download directory
Deluge state directory

---

# License

MIT License

---

# Support

If you find this useful, please consider giving the repository a star on GitHub.

https://github.com/race-in/deluge-to-qbittorrent-transfer
