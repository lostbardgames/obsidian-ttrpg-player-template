#!/usr/bin/env python3
"""
UpdateVault.py — LBG TTRPG Player Template updater
Checks GitHub for a newer version and updates template files.
Your campaign data (My Character/, Campaign Notes/, Possessions/, Lore/) is NEVER touched.

Modes:
  (no flags)        Interactive terminal mode — prompts for confirmation.
  --check           Machine mode: prints one JSON line describing update status, no prompts.
  --apply           Machine mode: downloads and applies the latest release, no prompts.
                     Prints one JSON line with the result.

--check and --apply are used by z_Templates/Scripts/UpdateVault.js so the whole
update flow runs from inside Obsidian — the player never has to open a terminal.
"""

import argparse
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
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Folders and files that contain campaign data — NEVER touched by the updater
PROTECTED = {
    "My Character",
    "Campaign Notes",
    "Possessions",
    "Lore",
    "z_Assets/Character",
    "z_Assets/Unsorted",
    "z_Excalidraw",
    "z_Uncategorized",
}

# Tool files that get a .bak backup before overwriting (user may have customised them)
TOOL_FILES = {
    "1.Tools/Homepage.md",
    "1.Tools/Player Screen.md",
    "1.Tools/Buttons.md",
    "HOW TO USE.md",
    "START HERE.md",
}


def get_current_version(vault_root):
    version_file = os.path.join(vault_root, "version.json")
    try:
        with open(version_file) as f:
            return json.load(f).get("version", "0.0.0")
    except Exception:
        return "0.0.0"


def version_tuple(v):
    return tuple(int(x) for x in v.split("."))


def fetch_latest_release():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "LBG-Player-Updater"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def download_zip(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "LBG-Player-Updater"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as f:
        shutil.copyfileobj(resp, f)


def is_protected(rel_path):
    parts = rel_path.replace("\\", "/")
    for p in PROTECTED:
        if parts == p or parts.startswith(p + "/"):
            return True
    return False


def get_zip_url(release):
    assets = release.get("assets", [])
    zip_asset = next((a for a in assets if a["name"].endswith(".zip")), None)
    return zip_asset["browser_download_url"] if zip_asset else release.get("zipball_url")


def apply_zip(zip_path, vault_root, new_version):
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

            dest = os.path.join(vault_root, rel)
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
    version_file = os.path.join(vault_root, "version.json")
    with open(version_file, "w") as f:
        json.dump({"version": new_version}, f, indent=2)

    return updated, backed_up, skipped


def check_for_update(vault_root):
    """Pure check — no prompts, no side effects. Returns a JSON-serializable dict."""
    current = get_current_version(vault_root)
    try:
        release = fetch_latest_release()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"status": "failed", "current_version": current,
                     "error": "No release has been published yet for this template."}
        return {"status": "failed", "current_version": current, "error": f"GitHub error: {e}"}
    except (urllib.error.URLError, TimeoutError) as e:
        return {"status": "failed", "current_version": current, "error": f"Could not reach GitHub: {e}"}
    except Exception as e:
        return {"status": "failed", "current_version": current, "error": str(e)}

    latest_tag = release.get("tag_name", "")
    latest = latest_tag.lstrip("v")
    if not latest:
        return {"status": "failed", "current_version": current, "error": "No release found on GitHub."}

    if version_tuple(latest) <= version_tuple(current):
        return {"status": "up_to_date", "current_version": current, "latest_version": latest}

    zip_url = get_zip_url(release)
    if not zip_url:
        return {"status": "failed", "current_version": current, "error": "No downloadable asset found in latest release."}

    return {
        "status": "update_available",
        "current_version": current,
        "latest_version": latest,
        "latest_tag": latest_tag,
        "changelog": (release.get("body") or "").strip(),
        "zip_url": zip_url,
    }


def apply_update(vault_root):
    """Fetches the latest release and applies it — no prompts. Returns a JSON-serializable dict."""
    current = get_current_version(vault_root)
    try:
        release = fetch_latest_release()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"status": "failed", "error": "No release has been published yet for this template."}
        return {"status": "failed", "error": f"GitHub error: {e}"}
    except Exception as e:
        return {"status": "failed", "error": f"Could not reach GitHub: {e}"}

    latest_tag = release.get("tag_name", "")
    latest = latest_tag.lstrip("v")
    if not latest:
        return {"status": "failed", "error": "No release found on GitHub."}

    if version_tuple(latest) <= version_tuple(current):
        return {"status": "success", "new_version": current, "updated": [], "backed_up": [], "skipped": [],
                "note": "Already up to date."}

    zip_url = get_zip_url(release)
    if not zip_url:
        return {"status": "failed", "error": "No downloadable asset found in latest release."}

    try:
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = os.path.join(tmp, "update.zip")
            download_zip(zip_url, zip_path)
            updated, backed_up, skipped = apply_zip(zip_path, vault_root, latest)
    except Exception as e:
        return {"status": "failed", "error": str(e)}

    return {
        "status": "success",
        "new_version": latest,
        "updated": updated,
        "backed_up": backed_up,
        "skipped": skipped,
    }


def interactive_main(vault_root):
    print("=" * 60)
    print("  LBG TTRPG Player Template — Update Check")
    print("=" * 60)

    current = get_current_version(vault_root)
    print(f"\n  Installed version : v{current}")
    print("  Checking GitHub for updates...\n")

    check = check_for_update(vault_root)
    if check["status"] == "failed":
        print(f"  ✗ {check['error']}")
        sys.exit(1)

    if check["status"] == "up_to_date":
        print("\n  ✓ You are already on the latest version. Nothing to do.")
        sys.exit(0)

    latest = check["latest_version"]
    print(f"  Latest version    : v{latest}")
    print(f"\n  A new version is available: v{current} → v{latest}")
    if check.get("changelog"):
        print("\n  Release notes:")
        for line in check["changelog"].splitlines()[:20]:
            print(f"    {line}")
    print()

    answer = input("  Update now? [y/N] ").strip().lower()
    if answer != "y":
        print("  Update cancelled.")
        sys.exit(0)

    print("  Downloading and applying update...")
    result = apply_update(vault_root)

    if result["status"] != "success":
        print(f"\n  ✗ Update failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)

    print(f"\n  ✓ Updated to v{result['new_version']}")
    print(f"    {len(result['updated'])} file(s) updated")
    if result["backed_up"]:
        print(f"    {len(result['backed_up'])} tool file(s) backed up as .bak before overwriting:")
        for f in result["backed_up"]:
            print(f"      • {f}")
    print(f"    {len(result['skipped'])} campaign data file(s) left untouched")
    print("\n  Reopen Obsidian to apply the update.")


def main():
    parser = argparse.ArgumentParser(description="LBG TTRPG Player Template updater")
    parser.add_argument("--vault", dest="vault_path", default=SCRIPT_DIR,
                         help="Path to the vault root (defaults to this script's own directory)")
    parser.add_argument("--check", action="store_true",
                         help="Check for updates only; print JSON result, no prompts")
    parser.add_argument("--apply", action="store_true",
                         help="Download and apply the latest release; print JSON result, no prompts")
    args = parser.parse_args()

    vault_root = os.path.abspath(args.vault_path)

    if args.check:
        print(json.dumps(check_for_update(vault_root)))
        return

    if args.apply:
        print(json.dumps(apply_update(vault_root)))
        return

    interactive_main(vault_root)


if __name__ == "__main__":
    main()
