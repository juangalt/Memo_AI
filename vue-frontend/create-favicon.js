const fs = require('fs');
const path = require('path');

// Read the brain emoji SVG
const svgPath = path.join(__dirname, 'public', 'brain.svg');
const svgContent = fs.readFileSync(svgPath, 'utf8');

// Create a simple HTML file that will generate a favicon
const htmlContent = `
<!DOCTYPE html>
<html>
<head>
    <title>Favicon Generator</title>
</head>
<body>
    <canvas id="canvas" width="32" height="32" style="display:none;"></canvas>
    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        // Create an image from the SVG
        const img = new Image();
        img.onload = function() {
            // Draw the brain emoji on the canvas
            ctx.drawImage(img, 0, 0, 32, 32);
            
            // Convert to favicon format
            const link = document.createElement('a');
            link.download = 'favicon.ico';
            link.href = canvas.toDataURL('image/x-icon');
            link.click();
        };
        
        // Convert SVG to data URL
        const svgBlob = new Blob(['${svgContent}'], {type: 'image/svg+xml'});
        const url = URL.createObjectURL(svgBlob);
        img.src = url;
    </script>
</body>
</html>
`;

// Write the HTML file
const htmlPath = path.join(__dirname, 'public', 'favicon-generator.html');
fs.writeFileSync(htmlPath, htmlContent);

console.log('Favicon generator HTML created at:', htmlPath);
console.log('Open this file in a browser to download the favicon.ico');
