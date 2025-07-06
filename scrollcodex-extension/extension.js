const vscode = require('vscode');
const { exec } = require('child_process');

function activate(context) {
    let disposable = vscode.commands.registerCommand('scrollcodex.runScroll', function () {
        const editor = vscode.window.activeTextEditor;
        const filePath = editor.document.fileName;
        exec(`python run_scroll_file.py "${filePath}"`, (err, stdout, stderr) => {
            vscode.window.showInformationMessage(stdout || stderr);
        });
    });

    context.subscriptions.push(disposable);
}
exports.activate = activate; 