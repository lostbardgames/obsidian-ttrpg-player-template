module.exports = async (params) => {
  const { app } = params;

  try {
    const versionFile = app.vault.getAbstractFileByPath("version.json");
    if (!versionFile) { new Notice("version.json not found."); return; }
    const versionData = JSON.parse(await app.vault.read(versionFile));
    const currentVersion = versionData.version;

    new Notice(`Current version: v${currentVersion}\n\nRun UpdateVault.py from your terminal to check for updates.`, 8000);
  } catch (e) {
    new Notice("Could not read version.json. Please run UpdateVault.py from your terminal.");
  }
};
