import subprocess
import os

html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Test</title>
<style>
@page { size: A4; margin: 10mm; }
body { font-family: sans-serif; color: #0b2b5b; }
</style>
</head>
<body>
<h1>CardioVision AI PDF Test</h1>
<p>Testing headless Chrome print to PDF.</p>
</body>
</html>"""

with open('temp_test.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
cmd = [chrome_path, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--print-to-pdf=test_chrome.pdf', os.path.abspath('temp_test.html')]
res = subprocess.run(cmd, capture_output=True, timeout=15)
print('Returncode:', res.returncode)
print('PDF exists:', os.path.exists('test_chrome.pdf'), 'Size:', os.path.getsize('test_chrome.pdf') if os.path.exists('test_chrome.pdf') else 0)

if os.path.exists('temp_test.html'):
    os.remove('temp_test.html')
if os.path.exists('test_chrome.pdf'):
    os.remove('test_chrome.pdf')
