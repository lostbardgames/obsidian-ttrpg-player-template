// ── Helpers ────────────────────────────────────────────────────────────────

function extractCharId(input) {
  const trimmed = input.trim();
  const match = trimmed.match(/\/characters?\/(\d+)/i);
  if (match) return match[1];
  if (/^\d+$/.test(trimmed)) return trimmed;
  return null;
}

// ── Python detection (same pattern as RunImport.js / UpdateVault.js) ───────

async function detectPython() {
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
          new Notice("✅ Python 3 installed. Retrying import…", 5000);
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
        new Notice("⏳ Homebrew installer opened in Terminal.\n\nFollow the prompts there, then click Import from D&D Beyond again.", 12000);
        return null;
      }});
    }
    options.push({ label: "Open python.org download page", action: () => {
      require("electron").shell.openExternal("https://www.python.org/downloads/");
      new Notice("🌐 Opening python.org.\n\nAfter installing Python 3, restart Obsidian and try again.", 10000);
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
      new Notice("🌐 Opening python.org.\n\nInstall Python 3 and check \"Add Python to PATH\", then restart Obsidian and try again.", 12000);
      return null;
    }});
  } else {
    options.push({ label: "Open python.org download page", action: () => {
      require("electron").shell.openExternal("https://www.python.org/downloads/");
      new Notice("🌐 Opening python.org.\n\nAfter installing Python 3, restart Obsidian and try again.", 10000);
      return null;
    }});
  }

  options.push({ label: "Cancel", action: null });

  const labels = options.map(o => o.label);
  const choice = await qa.suggester(labels, labels);
  if (!choice || choice === "Cancel") return null;

  const selected = options.find(o => o.label === choice);
  return selected?.action ? await selected.action(qa) : null;
}

// ── Main ───────────────────────────────────────────────────────────────────

module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;
  const vaultPath = app.vault.adapter.basePath;

  // ── Character URL / ID ─────────────────────────────────────────────────────
  const input = await qa.inputPrompt(
    "D&D Beyond character URL or ID",
    "https://www.dndbeyond.com/characters/123456789"
  );
  if (!input) return;

  const charId = extractCharId(input);
  if (!charId) {
    new Notice("❌ Could not find a character ID in that input.", 6000);
    return;
  }

  // Overwrite guard — this vault holds one character per person, not one per party
  const existing = app.vault.getMarkdownFiles().filter(f => f.path.startsWith("My Character/"));
  if (existing.length > 0) {
    const names = existing.map(f => f.basename).join(", ");
    const proceed = await qa.yesNoPrompt(
      "Character already exists",
      `My Character/ already has: ${names}\n\nImporting will create an additional file there (or overwrite one with the same name). Continue?`
    );
    if (!proceed) return;
  }

  // ── Campaign name (optional, plain text — no party system in this vault) ───
  const campaignName = (await qa.inputPrompt("Campaign name (optional)", "")) || "";

  // ── Detect Python ────────────────────────────────────────────────────────
  let python = await detectPython();
  if (!python) {
    python = await handleMissingPython(qa);
    if (!python) return;
  }

  // ── Run Python importer ─────────────────────────────────────────────────
  const { exec } = require("child_process");
  const { promisify } = require("util");
  const path = require("path");
  const execAsync = promisify(exec);

  const shellQuote = a => `"${String(a).replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
  const scriptPath = path.join(vaultPath, "ImportDnDBeyond.py");
  const cmd = [shellQuote(python), shellQuote(scriptPath), shellQuote(vaultPath), shellQuote(charId), shellQuote(campaignName)].join(" ");

  const fetchingNotice = new Notice("⏳ Fetching character from D&D Beyond…", 0);

  let result;
  try {
    const { stdout } = await execAsync(cmd, { maxBuffer: 10 * 1024 * 1024, timeout: 60000 });
    const lines = stdout.trim().split("\n").filter(Boolean);
    result = JSON.parse(lines[lines.length - 1]);
  } catch (e) {
    fetchingNotice.hide();
    new Notice(`❌ Import failed: ${e.message}`, 10000);
    console.error("[ImportDnDBeyond] error:", e);
    return;
  }
  fetchingNotice.hide();

  // ── Private character ────────────────────────────────────────────────────
  if (result.error === "character_private") {
    new Notice(
      "🔒 This character is set to private on D&D Beyond.\n\nGo to your character sheet → Share → set visibility to Public, then try importing again.",
      15000
    );
    return;
  }

  if (result.error) {
    new Notice(`❌ Import failed: ${result.error}`, 10000);
    console.error("[ImportDnDBeyond] result:", result);
    return;
  }

  // ── Success — reload so the new character note and any downloaded art load ──
  new Notice(`✅ Imported ${result.name}! Reloading vault…`, 5000);
  console.log("[ImportDnDBeyond] result:", result);
  setTimeout(() => app.commands.executeCommandById("app:reload"), 2000);
};
