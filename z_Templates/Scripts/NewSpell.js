module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  const name = await qa.inputPrompt("New Spell", "Enter spell name...");
  if (!name) return;

  const destPath = `Possessions/Spells/${name}.md`;
  if (app.vault.getAbstractFileByPath(destPath)) {
    new Notice(`"${name}" already exists!`);
    return;
  }

  const tpl = app.vault.getAbstractFileByPath("z_Templates/Possessions/Template - Spell.md");
  if (!tpl) { new Notice("Spell template not found!"); return; }

  const content = await app.vault.read(tpl);
  const file = await app.vault.create(destPath, content);
  await getMainLeaf(app).openFile(file);
  new Notice(`"${name}" created!`);
};

function getMainLeaf(app) {
  return app.workspace.getLeavesOfType("markdown")
    .find(l => l.view?.file?.path !== "1.Tools/Buttons.md")
    ?? app.workspace.getLeaf();
}
