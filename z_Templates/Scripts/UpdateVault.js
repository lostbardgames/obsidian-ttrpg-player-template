// ── Config ────────────────────────────────────────────────────────────────────

const PYTHON_SCRIPT = "UpdateVault.py"; // relative to vault root

// ── Python detection ────────────────────────────────────────────────────────

async function detectPython() {
  // On Windows "python3" triggers the Microsoft Store stub — try "python" first.
  const candidates = process.platform === "win32"
    ? ["python", "py", "python3"]
    : ["python3", "python"];

  for (const cmd of candidates) {
    const found = await checkPython3(cmd);
    if (found) return cmd;
  }
  return null;
}

function checkPython3(cmd) {
  return new Promise((resolve) => {
    const { exec } = require("child_process");
    exec(`"${cmd}" --version`, { timeout: 8000 }, (err, stdout, stderr) => {
      const output = (stdout + stderr).trim();
      resolve(!err && /Python 3\./.test(output) ? cmd : null);
    });
  });
}

function commandExists(cmd) {
  return new Promise((resolve) => {
    const { exec } = require("child_process");
    const check = process.platform === "win32" ? `where ${cmd}` : `which ${cmd}`;
    exec(check, { timeout: 5000 }, (err) => resolve(!err));
  });
}

function runCommand(command, timeout = 120000) {
  return new Promise((resolve, reject) => {
    const { exec } = require("child_process");
    exec(command, { timeout }, (err, stdout, stderr) => {
      if (err) reject(new Error(stderr?.trim() || err.message));
      else resolve({ stdout, stderr });
    });
  });
}

async function handleMissingPython(qa) {
  const platform = process.platform;
  const options = [];

  if (platform === "darwin") {
    const hasBrew = await commandExists("brew");
    if (hasBrew) {
      options.push({ label: "Install via Homebrew (recommended)", action: async () => {
        const notice = new Notice("⏳ Installing Python 3 via Homebrew… this may take a few minutes.", 0);
        try {
          await runCommand("brew install python3", 300000);
          notice.hide();
          new Notice("✅ Python 3 installed. Retrying update check…", 5000);
          return await detectPython();
        } catch (e) {
          notice.hide();
          new Notice(`❌ Homebrew install failed:\n${e.message}\n\nTry installing manually from python.org.`, 10000);
          return null;
        }
      }});
    } else {
      options.push({ label: "Install Homebrew + Python", action: async () => {
        const confirm = await qa.yesNoPrompt(
          "Install Homebrew?",
          "This will open a Terminal window to install Homebrew and Python 3. Your system password may be required. Continue?"
        );
        if (!confirm) return null;
        const { exec } = require("child_process");
        exec(`osascript -e 'tell application "Terminal" to do script "/bin/bash -c \\"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\\" && brew install python3"'`);
        new Notice("⏳ Homebrew installer opened in Terminal.\n\nFollow the prompts there, then click Check for Updates again.", 12000);
        return null;
      }});
    }
    options.push({ label: "Open python.org download page", action: () => {
      require("electron").shell.openExternal("https://www.python.org/downloads/");
      new Notice("🌐 Opening python.org.\n\nAfter installing Python 3, restart Obsidian and click Check for Updates again.", 10000);
      return null;
    }});
  } else if (platform === "win32") {
    const hasWinget = await commandExists("winget");
    if (hasWinget) {
      options.push({ label: "Install via winget (recommended)", action: async () => {
        const notice = new Notice("⏳ Installing Python 3 via winget… this may take a few minutes.", 0);
        const versions = ["3.13", "3.12", "3.11", "3.10"];
        let installed = false;
        for (const v of versions) {
          try {
            await runCommand(`winget install --id Python.Python.${v} --source winget --silent`, 300000);
            installed = true;
            break;
          } catch (_) { /* try next version */ }
        }
        notice.hide();
        if (installed) {
          new Notice("✅ Python 3 installed. You may need to restart Obsidian for the PATH to update.", 8000);
          return await detectPython();
        }
        new Notice("❌ winget install failed for all Python versions.\n\nTry installing manually from python.org.", 10000);
        return null;
      }});
    }
    options.push({ label: "Open python.org download page", action: () => {
      require("electron").shell.openExternal("https://www.python.org/downloads/");
      new Notice("🌐 Opening python.org.\n\nInstall Python 3 and check \"Add Python to PATH\", then restart Obsidian and click Check for Updates again.", 12000);
      return null;
    }});
  } else {
    options.push({ label: "Open python.org download page", action: () => {
      require("electron").shell.openExternal("https://www.python.org/downloads/");
      new Notice("🌐 Opening python.org.\n\nAfter installing Python 3, restart Obsidian and click Check for Updates again.", 10000);
      return null;
    }});
  }

  options.push({ label: "Cancel", action: null });

  const labels = options.map(o => o.label);
  const choice = await qa.suggester(labels, labels, "How do you want to install Python 3?");
  if (!choice || choice === "Cancel") return null;

  const selected = options.find(o => o.label === choice);
  return selected?.action ? await selected.action(qa) : null;
}

// ── Run UpdateVault.py and parse its JSON result ────────────────────────────
// The script prints exactly one JSON line as its last line of stdout.

async function runPython(vaultPath, args, python) {
  const { exec } = require("child_process");
  const { promisify } = require("util");
  const path = require("path");
  const execAsync = promisify(exec);

  const scriptPath = path.join(vaultPath, PYTHON_SCRIPT);
  const shellQuote = a => `"${String(a).replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
  const cmd = [shellQuote(python), shellQuote(scriptPath), ...args.map(shellQuote)].join(" ");

  const { stdout } = await execAsync(cmd, { maxBuffer: 10 * 1024 * 1024, timeout: 120000 });

  const lines = stdout.trim().split("\n").filter(Boolean);
  return JSON.parse(lines[lines.length - 1]);
}

// ── Main ─────────────────────────────────────────────────────────────────────

module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;
  const vaultPath = app.vault.adapter.basePath;

  let python = await detectPython();
  if (!python) {
    python = await handleMissingPython(qa);
    if (!python) return;
  }

  // ── Step 1: Check for updates ──────────────────────────────────────────────
  const checkingNotice = new Notice("Checking for updates…", 0);

  let check;
  try {
    check = await runPython(vaultPath, ["--vault", vaultPath, "--check"], python);
  } catch (e) {
    checkingNotice.hide();
    new Notice(`❌ Update check failed: ${e.message}`, 10000);
    console.error("[UpdateVault] check error:", e);
    return;
  }
  checkingNotice.hide();

  if (check.status === "failed") {
    new Notice(`❌ Update check failed: ${check.error}`, 10000);
    return;
  }

  if (check.status === "up_to_date") {
    new Notice(`✅ Already up to date (v${check.current_version})`, 5000);
    return;
  }

  // ── Step 2: Show changelog and confirm ─────────────────────────────────────
  const changelog = check.changelog
    ? check.changelog.slice(0, 800) + (check.changelog.length > 800 ? "…" : "")
    : "No changelog provided.";

  new Notice(
    `Update available: v${check.current_version} → v${check.latest_version}\n\nWhat's New:\n${changelog}`,
    20000
  );

  const proceed = await qa.yesNoPrompt(
    `Update vault to v${check.latest_version}?`,
    `Your character, journal, session recaps, quests, and possessions are never touched. Tool files (Homepage, Player Screen, Buttons, guides) are backed up as .bak before being replaced.\n\nContinue?`
  );
  if (!proceed) return;

  // ── Step 3: Apply update ────────────────────────────────────────────────────
  const applyingNotice = new Notice("⬇️ Downloading and applying update…", 0);

  let result;
  try {
    result = await runPython(vaultPath, ["--vault", vaultPath, "--apply"], python);
  } catch (e) {
    applyingNotice.hide();
    new Notice(`❌ Update failed: ${e.message}`, 12000);
    console.error("[UpdateVault] apply error:", e);
    return;
  }
  applyingNotice.hide();

  if (result.status !== "success") {
    new Notice(`❌ Update failed: ${result.error || "Unknown error"}`, 12000);
    console.error("[UpdateVault] result:", result);
    return;
  }

  const updatedCount = (result.updated || []).length;
  const backedUpCount = (result.backed_up || []).length;
  const skippedCount = (result.skipped || []).length;

  let msg = `✅ Updated to v${result.new_version}!\n${updatedCount} file(s) replaced.`;
  if (backedUpCount > 0) {
    msg += `\n\n${backedUpCount} tool file(s) backed up as .bak:\n${result.backed_up.map(f => `• ${f}`).join("\n")}`;
  }
  msg += `\n\n${skippedCount} campaign data file(s) left untouched.`;
  msg += `\n\nReloading Obsidian…`;

  new Notice(msg, 8000);
  console.log("[UpdateVault] result:", result);

  // Reload so the updated Homepage/Buttons/templates/scripts take effect immediately.
  setTimeout(() => app.commands.executeCommandById("app:reload"), 3500);
};
