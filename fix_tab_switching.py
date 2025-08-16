#!/usr/bin/env python3
"""
Fix the tab switching functionality
"""

import re

# Read current HTML
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the switchTab function
old_switch_function = r'function switchTab\(tabName\) \{[^}]*\{[^}]*\}[^}]*\}'

new_switch_function = '''function switchTab(tabName) {
            console.log('Switching to tab:', tabName);
            
            // Hide all tab contents
            const allTabContents = document.querySelectorAll('.tab-content');
            allTabContents.forEach(tab => {
                tab.classList.add('hidden');
                console.log('Hidden tab:', tab.id);
            });
            
            // Remove active class from all tabs
            const allTabs = document.querySelectorAll('.tab');
            allTabs.forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            const selectedTab = document.getElementById(tabName + '-tab');
            if (selectedTab) {
                selectedTab.classList.remove('hidden');
                console.log('Showing tab:', tabName + '-tab');
            } else {
                console.error('Tab not found:', tabName + '-tab');
            }
            
            // Add active class to clicked tab
            const clickedTab = event ? event.target : document.querySelector(`[onclick*="${tabName}"]`);
            if (clickedTab) {
                clickedTab.classList.add('active');
            }
            
            // Load status if status tab is selected
            if (tabName === 'status') {
                loadSystemStatus();
            }
        }'''

# Replace using more flexible pattern
pattern = r'function switchTab\([^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}'
content = re.sub(pattern, new_switch_function, content, flags=re.DOTALL)

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Tab switching function fixed")