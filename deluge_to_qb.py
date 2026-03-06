#!/usr/bin/env python3
"""
Transfer torrents from Deluge to qBittorrent after they have seeded for N minutes.
"""

import os
import sys
import time
import logging
import shutil
import argparse
from pathlib import Path

from deluge_client import DelugeRPCClient
from qbittorrentapi import Client as QBClient, LoginFailed, APIConnectionError

# -----------------------------------------------------------------------------
# DEFAULT CONFIGURATION (edit these or use command-line arguments)
# -----------------------------------------------------------------------------
DELUGE_HOST = "localhost"
DELUGE_PORT = 10006
DELUGE_USERNAME = "khokan"
DELUGE_PASSWORD = "Murmu007"
DELUGE_STATE_DIR = "/home/khokan/.config/deluge/state"
DELUGE_DOWNLOAD_DIR = "/home/khokan/torrents/deluge"

QB_HOST = "localhost"
QB_PORT = 15164
QB_USERNAME = "khokan"
QB_PASSWORD = "Murmu007"
QB_DOWNLOAD_DIR = "/home/khokan/torrents/qbittorrent"

SEEDING_MINUTES = 5          # transfer after this many minutes of seeding
# -----------------------------------------------------------------------------

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger("deluge_to_qb")

def connect_deluge():
    client = DelugeRPCClient(DELUGE_HOST, DELUGE_PORT, DELUGE_USERNAME, DELUGE_PASSWORD)
    try:
        client.connect()
        log.info("Connected to Deluge")
        return client
    except Exception as e:
        log.error(f"Failed to connect to Deluge: {e}")
        return None

def connect_qbittorrent():
    qb = QBClient(host=f"http://{QB_HOST}:{QB_PORT}", username=QB_USERNAME, password=QB_PASSWORD)
    try:
        qb.auth_log_in()
        log.info("Connected to qBittorrent")
        return qb
    except (LoginFailed, APIConnectionError) as e:
        log.error(f"Failed to connect to qBittorrent: {e}")
        return None

def get_deluge_torrents(deluge_client):
    fields = ['hash', 'name', 'state', 'save_path', 'completed_time', 'progress', 'files']
    torrents = deluge_client.call('core.get_torrents_status', {}, fields)
    return torrents

def torrent_is_ready(torrent_data):
    if torrent_data.get(b'state') != b'Seeding' and torrent_data.get(b'progress', 0) < 100:
        return False
    completed_time = torrent_data.get(b'completed_time', 0)
    if not completed_time:
        return False
    age = time.time() - completed_time
    return age >= SEEDING_MINUTES * 60

def torrent_exists_in_qb(qb_client, torrent_hash):
    try:
        torrents = qb_client.torrents_info()
        return any(t['hash'] == torrent_hash for t in torrents)
    except Exception as e:
        log.error(f"Failed to list qBittorrent torrents: {e}")
        return False

def move_torrent_data(torrent_name, source_base, dest_base):
    src_path = Path(source_base) / torrent_name
    dst_path = Path(dest_base) / torrent_name

    if not src_path.exists():
        log.error(f"Source path does not exist: {src_path}")
        return False

    dst_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if dst_path.exists():
            log.error(f"Destination already exists: {dst_path}")
            return False
        log.info(f"Moving {src_path} -> {dst_path}")
        shutil.move(str(src_path), str(dst_path))
        return True
    except Exception as e:
        log.error(f"Failed to move {src_path} to {dst_path}: {e}")
        return False

def add_torrent_to_qb(qb_client, torrent_file_path, save_path):
    try:
        with open(torrent_file_path, 'rb') as f:
            torrent_file = f.read()
    except Exception as e:
        log.error(f"Could not read torrent file {torrent_file_path}: {e}")
        return False

    try:
        qb_client.torrents_add(
            torrent_files=torrent_file,
            save_path=save_path,
            skip_checking=True,
            is_paused=False
        )
        log.info(f"Added torrent to qBittorrent, save_path={save_path}")
        return True
    except Exception as e:
        log.error(f"Failed to add torrent to qBittorrent: {e}")
        return False

def remove_from_deluge(deluge_client, torrent_hash):
    try:
        deluge_client.call('core.remove_torrent', torrent_hash, False)
        log.info(f"Removed {torrent_hash} from Deluge")
        return True
    except Exception as e:
        log.error(f"Failed to remove torrent {torrent_hash} from Deluge: {e}")
        return False

def main():
    global DELUGE_HOST, DELUGE_PORT, DELUGE_USERNAME, DELUGE_PASSWORD
    global DELUGE_STATE_DIR, DELUGE_DOWNLOAD_DIR
    global QB_HOST, QB_PORT, QB_USERNAME, QB_PASSWORD, QB_DOWNLOAD_DIR
    global SEEDING_MINUTES

    parser = argparse.ArgumentParser(description="Transfer seeded torrents from Deluge to qBittorrent")
    parser.add_argument("--deluge-host", default=DELUGE_HOST)
    parser.add_argument("--deluge-port", type=int, default=DELUGE_PORT)
    parser.add_argument("--deluge-username", default=DELUGE_USERNAME)
    parser.add_argument("--deluge-password", default=DELUGE_PASSWORD)
    parser.add_argument("--deluge-state-dir", default=DELUGE_STATE_DIR)
    parser.add_argument("--deluge-download-dir", default=DELUGE_DOWNLOAD_DIR)
    parser.add_argument("--qb-host", default=QB_HOST)
    parser.add_argument("--qb-port", type=int, default=QB_PORT)
    parser.add_argument("--qb-username", default=QB_USERNAME)
    parser.add_argument("--qb-password", default=QB_PASSWORD)
    parser.add_argument("--qb-download-dir", default=QB_DOWNLOAD_DIR)
    parser.add_argument("--seeding-minutes", type=int, default=SEEDING_MINUTES)
    parser.add_argument("--dry-run", action="store_true", help="Only log what would be done")
    args = parser.parse_args()

    DELUGE_HOST = args.deluge_host
    DELUGE_PORT = args.deluge_port
    DELUGE_USERNAME = args.deluge_username
    DELUGE_PASSWORD = args.deluge_password
    DELUGE_STATE_DIR = args.deluge_state_dir
    DELUGE_DOWNLOAD_DIR = args.deluge_download_dir
    QB_HOST = args.qb_host
    QB_PORT = args.qb_port
    QB_USERNAME = args.qb_username
    QB_PASSWORD = args.qb_password
    QB_DOWNLOAD_DIR = args.qb_download_dir
    SEEDING_MINUTES = args.seeding_minutes

    log.info("Starting Deluge → qBittorrent transfer check (dry_run=%s)", args.dry_run)

    deluge = connect_deluge()
    if not deluge:
        return 1
    qb = connect_qbittorrent()
    if not qb:
        deluge.disconnect()
        return 1

    torrents = get_deluge_torrents(deluge)
    log.info(f"Found {len(torrents)} torrents in Deluge")

    processed = 0
    for torrent_hash, data in torrents.items():
        th = torrent_hash.decode() if isinstance(torrent_hash, bytes) else torrent_hash
        name = data.get(b'name', b'').decode() or th
        log.debug(f"Checking torrent {name} ({th})")

        if not torrent_is_ready(data):
            continue

        if torrent_exists_in_qb(qb, th):
            log.info(f"Torrent {name} ({th}) already in qBittorrent, removing from Deluge")
            if not args.dry_run:
                remove_from_deluge(deluge, th)
            processed += 1
            continue

        torrent_file = Path(DELUGE_STATE_DIR) / f"{th}.torrent"
        if not torrent_file.is_file():
            log.warning(f"Torrent file not found for {name}: {torrent_file}")
            continue

        torrent_top_name = name

        if not args.dry_run:
            move_ok = move_torrent_data(torrent_top_name, DELUGE_DOWNLOAD_DIR, QB_DOWNLOAD_DIR)
            if not move_ok:
                log.error(f"Skipping {name} because data move failed")
                continue
        else:
            log.info(f"[DRY RUN] Would move {torrent_top_name} from {DELUGE_DOWNLOAD_DIR} to {QB_DOWNLOAD_DIR}")

        if not args.dry_run:
            if add_torrent_to_qb(qb, torrent_file, QB_DOWNLOAD_DIR):
                time.sleep(2)
                remove_from_deluge(deluge, th)
            else:
                log.error(f"Failed to add {name} to qBittorrent, data was moved but Deluge entry remains")
        else:
            log.info(f"[DRY RUN] Would add torrent {torrent_file} to qBittorrent with save_path={QB_DOWNLOAD_DIR} and remove from Deluge")

        processed += 1

    deluge.disconnect()
    log.info(f"Transfer check completed. Processed {processed} torrents.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
