module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  const sessionName = await selectFromFolder(app, qa, "Campaign Notes/Session Recaps", "Session Recap", true);
  if (sessionName === null) return;

  const locationName = await selectFromFolder(app, qa, "Campaign Notes/Locations", "Location Found", true);
  if (locationName === null) return;

  const name = await qa.inputPrompt("New Item", "Enter item name...");
  if (!name) return;

  const destPath = `Possessions/Items/${name}.md`;
  if (app.vault.getAbstractFileByPath(destPath)) {
    new Notice(`"${name}" already exists!`);
    return;
  }

  const charName = await selectFromFolder(app, qa, "My Character", "Owner", true);
  if (charName === null) return;

  const tpl = app.vault.getAbstractFileByPath("z_Templates/Possessions/Template - Item.md");
  if (!tpl) { new Notice("Item template not found!"); return; }

  let content = await app.vault.read(tpl);
  if (sessionName) content = setListField(content, "obtainedIn", sessionName);
  if (locationName) content = setListField(content, "foundAt", locationName);
  if (charName) content = setListField(content, "owner", charName);

  const file = await app.vault.create(destPath, content);
  await getMainLeaf(app).openFile(file);
  new Notice(`"${name}" created!`);
};

async function selectFromFolder(app, qa, folderPath, label, allowSkip = false) {
  const folder = app.vault.getAbstractFileByPath(folderPath);
  const existing = (folder?.children || [])
    .filter(f => !("children" in f) && f.extension === "md")
    .map(f => f.basename)
    .sort();
  const SKIP = "[ None / Skip ]";
  const opts = allowSkip ? [...existing, SKIP] : [...existing];
  if (opts.length === 0 && !allowSkip) return null;
  if (opts.length === 0) return "";
  const choice = await qa.suggester(opts, opts);
  if (!choice) return null;
  if (choice === SKIP) return "";
  return choice;
}

function setListField(content, field, value) {
  return content.replace(new RegExp(`^${field}:.*$`, "m"), `${field}:\n  - "[[${value}]]"`);
}

function getMainLeaf(app) {
  return app.workspace.getLeavesOfType("markdown")
    .find(l => l.view?.file?.path !== "1.Tools/Buttons.md")
    ?? app.workspace.getLeaf();
}
