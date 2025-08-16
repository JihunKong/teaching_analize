#!/usr/bin/env python3
"""
Clean up the HTML UI to remove port warning popup
"""

import re

# Read the current HTML file
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the popup warning completely
popup_pattern = r'setTimeout\(\(\) => \{[^}]*confirm\([^}]*\)\;[^}]*\}, 2000\)\;'
content = re.sub(popup_pattern, '// Popup warning removed - ports are working', content, flags=re.DOTALL)

# Remove the entire setTimeout block more aggressively if above doesn't work
popup_pattern2 = r'// Show instructions\s*setTimeout\(.*?2000\);'
content = re.sub(popup_pattern2, '// Instructions removed - all ports working', content, flags=re.DOTALL)

# Even more aggressive removal
lines = content.split('\n')
cleaned_lines = []
skip_until_semicolon = False

for line in lines:
    if 'Show instructions' in line:
        cleaned_lines.append('        // Instructions removed - all ports working')
        skip_until_semicolon = True
        continue
    
    if skip_until_semicolon:
        if '}, 2000);' in line:
            skip_until_semicolon = False
        continue
    
    cleaned_lines.append(line)

content = '\n'.join(cleaned_lines)

# Write back the cleaned content
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ UI cleaned - popup warning removed")