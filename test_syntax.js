const fs = require("fs");
const ui = fs.readFileSync("ibd_reigns/ui/swipe_component_v2/index.html", "utf-8");
const match = ui.match(/<script>(.*?)<\/script>/s);
if (match) {
    const code = match[1];
    try {
        new Function(code);
        console.log("Syntax OK!");
    } catch (e) {
        console.error("Syntax Error:", e);
    }
} else {
    console.log("No script tag found");
}
