#!/usr/bin/env python3
"""
UpdateVault.py — LBG TTRPG Player Template updater
Checks GitHub for a newer version and updates template files.
Your campaign data (My Character/, Campaign Notes/, Possessions/, Lore/) is NEVER touched.
"""

import json
import os
import sys
import shutil
import urllib.request
import urllib.error
import zipfile
import tempfile

REPO = "lostbardgames/obsidian-ttrpg-player-template"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
VAULT_ROOT = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(VAULT_ROOT, "version.json")

# Folders and files that contain campaign data — NEVER touched by the updater
PROTECTED = {
    "My Character",
    "Campaign Notes",
    "Possessions",
    "Lore",
    "z_Assets/Character",
    "z_Assets/Unsorted",
    "z_Excalidraw",
    "z_Uncategoried",
}

# Tool files that get a .bak backup before overwriting (user may have customised them)
TOOL_FILES = {
    "1.Tools/Homepage.md",
    "1.Tools/Player Screen.md",
    "1.Tools/Buttons.md",
    "HOW TO USE.md",
    "START HERE.md",
}


def get_current_version():
    try:
        with open(VERSION_FILE) as f:
            return json.load(f).get("version", "0.0.0")
    except Exception:
        return "0.0.0"


def version_tuple(v):
    return tuple(int(x) for x in v.split("."))


def fetch_latest_release():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "LBG-Player-Updater"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        print(f"  ✗ Could not reach GitHub: {e}")
        return None


def download_zip(url, dest):
    print(f"  Downloading update...")
    req = urllib.request.Request(url, headers={"User-Agent": "LBG-Player-Updater"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as f:
        shutil.copyfileobj(resp, f)


def is_protected(rel_path):
    parts = rel_path.replace("\\", "/")
    for p in PROTECTED:
        if parts == p or parts.startswith(p + "/"):
            return True
    return False


def update_vault(zip_path, new_version):
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        # The zip has a top-level folder like "obsidian-ttrpg-player-template-1.0.1/"
        prefix = names[0].split("/")[0] + "/" if names else ""

        updated = []
        backed_up = []
        skipped = []

        for name in names:
            if not name.startswith(prefix):
                continue
            rel = name[len(prefix):]
            if not rel or rel.endswith("/"):
                continue
            if is_protected(rel):
                skipped.append(rel)
                continue

            dest = os.path.join(VAULT_ROOT, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)

            # Back up tool files before overwriting
            if rel in TOOL_FILES and os.path.exists(dest):
                bak = dest + ".bak"
                shutil.copy2(dest, bak)
                backed_up.append(rel)

            with zf.open(name) as src, open(dest, "wb") as dst:
                shutil.copyfileobj(src, dst)
            updated.append(rel)

    # Stamp the new version
    with open(VERSION_FILE, "w") as f:
        json.dump({"version": new_version}, f, indent=2)

    return updated, backed_up, skipped


def main():
    print("=" * 60)
    print("  LBG TTRPG Player Template — Update Check")
    print("=" * 60)

    current = get_current_version()
    print(f"\n  Installed version : v{current}")
    print("  Checking GitHub for updates...\n")

    release = fetch_latest_release()
    if not release:
        print("  Could not fetch release info. Check your internet connection.")
        sys.exit(1)

    latest = release.get("tag_name", "").lstrip("v")
    if not latest:
        print("  No release found on GitHub.")
        sys.exit(1)

    print(f"  Latest version    : v{latest}")

    if version_tuple(latest) <= version_tuple(current):
        print("\n  ✓ You are already on the latest version. Nothing to do.")
        sys.exit(0)

    print(f"\n  A new version is available: v{current} → v{latest}")
    body = release.get("body", "").strip()
    if body:
        print("\n  Release notes:")
        for line in body.splitlines()[:20]:
            print(f"    {line}")
    print()

    answer = input("  Update now? [y/N] ").strip().lower()
    if answer != "y":
        print("  Update cancelled.")
        sys.exit(0)

    # Find the zip asset
    assets = release.get("assets", [])
    zip_asset = next((a for a in assets if a["name"].endswith(".zip")), None)
    if not zip_asset:
        # Fall back to source zip
        zip_url = release.get("zipball_url")
    else:
        zip_url = zip_asset["browser_download_url"]

    if not zip_url:
        print("  ✗ No downloadable asset found in this release.")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, "update.zip")
        download_zip(zip_url, zip_path)
        updated, backed_up, skipped = update_vault(zip_path, latest)

    print(f"\n  ✓ Updated to v{latest}")
    print(f"    {len(updated)} file(s) updated")
    if backed_up:
        print(f"    {len(backed_up)} tool file(s) backed up as .bak before overwriting:")
        for f in backed_up:
            print(f"      • {f}")
    print(f"    {len(skipped)} campaign data file(s) left untouched")
    print("\n  Reopen Obsidian to apply the update.")


if __name__ == "__main__":
    main()
