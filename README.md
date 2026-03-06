# Deluge → qBittorrent Transfer Script

Automatically move completed torrents from Deluge to qBittorrent after they have seeded for a configurable time.

## Features

- Works with Deluge 2.x
- Works with qBittorrent 4.x
- Moves data instead of copying
- Dry run support
- Cron automation support

## Installation

Clone repository:

git clone https://github.com/race-in/deluge-to-qbittorrent-transfer.git

Install dependencies:

pip install -r requirements.txt

## Usage

Dry run:

python deluge_to_qb.py --dry-run

Run normally:

python deluge_to_qb.py
