const fs = require('fs');
const path = require('path');

// Config: โฟลเดอร์ที่ไม่ต้องการวิเคราะห์
const ignoreDirs = ['node_modules', '.git', 'dist', 'build', '.vscode'];
const ignoreFiles = ['package-lock.json', 'yarn.lock', '.DS_Store', 'audit.js'];
const extensions = ['.js', '.json', '.ts', '.md', '.html', '.css', '.env.example'];

function getAllFiles(dirPath, arrayOfFiles) {
  const files = fs.readdirSync(dirPath);

  arrayOfFiles = arrayOfFiles || [];

  files.forEach(function(file) {
    if (fs.statSync(dirPath + "/" + file).isDirectory()) {
      if (!ignoreDirs.includes(file)) {
        arrayOfFiles = getAllFiles(dirPath + "/" + file, arrayOfFiles);
      }
    } else {
      if (!ignoreFiles.includes(file) && extensions.includes(path.extname(file))) {
        arrayOfFiles.push(path.join(dirPath, "/", file));
      }
    }
  });

  return arrayOfFiles;
}

const allFiles = getAllFiles(__dirname);
let output = `--- PROJECT ANALYSIS: NamoNexus Enterprise v3.5.1 ---\nTotal Files: ${allFiles.length}\n\n`;

allFiles.forEach(file => {
    const content = fs.readFileSync(file, 'utf8');
    const relativePath = path.relative(__dirname, file);
    output += `\n========================================\nFile: ${relativePath}\n========================================\n${content}\n`;
});

fs.writeFileSync('project_context.txt', output);
console.log('✅ Analysis Ready! เปิดไฟล์ project_context.txt แล้วก๊อปข้อมูลมาให้นะโมได้เลยครับ');
