module.exports = async (params) => {
  const { app, quickAddApi: qa } = params;

  const name = await qa.inputPrompt("New Character", "Enter your character's name...");
  if (!name) return;

  const destPath = `My Character/${name}.md`;
  if (app.vault.getAbstractFileByPath(destPath)) {
    new Notice(`"${name}" already exists!`);
    return;
  }

  const tpl = app.vault.getAbstractFileByPath("z_Templates/Characters/Template - My Character.md");
  if (!tpl) { new Notice("Character template not found!"); return; }

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
