#!/usr/bin/env python3
"""
Fix the analysis result display function
"""

import re

# Read current HTML
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the displayAnalysisResult function
old_function_pattern = r'function displayAnalysisResult\(data\) \{[^}]*\{[^}]*\}[^}]*\}'
new_function = '''function displayAnalysisResult(data) {
            console.log('Analysis data received:', data);
            const resultDiv = document.getElementById('analysis-result');
            let html = '<h4>📊 CBIL 분석 결과</h4>';
            
            // Display the actual analysis data
            if (data.cbil_scores) {
                html += `
                    <div style="margin: 15px 0; padding: 15px; background: #f0f8ff; border-radius: 8px;">
                        <strong>🎯 전체 점수:</strong> <span style="font-size: 1.2em; color: #2196F3;">${data.overall_score || 'N/A'}</span><br>
                        <strong>📊 CBIL 레벨별 점수:</strong><br>
                        <div style="margin: 10px 0; font-family: monospace;">
                `;
                
                const levelNames = {
                    "1": "단순 확인",
                    "2": "사실 회상", 
                    "3": "개념 설명",
                    "4": "분석적 사고",
                    "5": "종합적 이해",
                    "6": "평가적 판단",
                    "7": "창의적 적용"
                };
                
                for (const [level, score] of Object.entries(data.cbil_scores)) {
                    const percentage = Math.round(score * 100);
                    const barWidth = Math.max(5, percentage);
                    html += `
                        <div style="margin: 5px 0;">
                            <span style="display: inline-block; width: 80px;">레벨 ${level}:</span>
                            <span style="display: inline-block; width: 100px;">${levelNames[level]}</span>
                            <div style="display: inline-block; width: 200px; height: 20px; background: #e0e0e0; border-radius: 10px; vertical-align: middle;">
                                <div style="width: ${barWidth}%; height: 100%; background: linear-gradient(90deg, #4CAF50, #2196F3); border-radius: 10px;"></div>
                            </div>
                            <span style="margin-left: 10px; font-weight: bold;">${percentage}%</span>
                        </div>
                    `;
                }
                
                html += `</div></div>`;
            }
            
            if (data.recommendations && data.recommendations.length > 0) {
                html += `
                    <div style="margin: 15px 0; padding: 15px; background: #fff3e0; border-radius: 8px;">
                        <strong>💡 개선 권장사항:</strong>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                `;
                data.recommendations.forEach(rec => {
                    html += `<li style="margin: 5px 0;">${rec}</li>`;
                });
                html += `</ul></div>`;
            }
            
            if (data.analysis_id) {
                html += `<div style="margin: 15px 0; font-size: 0.9em; color: #666;">
                    <strong>분석 ID:</strong> ${data.analysis_id}<br>
                    <strong>분석 시간:</strong> ${new Date().toLocaleString()}
                </div>`;
            }
            
            resultDiv.innerHTML = html;
        }'''

# Replace the function
content = re.sub(old_function_pattern, new_function, content, flags=re.DOTALL)

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Analysis display function updated with detailed results")