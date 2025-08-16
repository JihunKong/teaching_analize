#!/usr/bin/env python3
"""
Manually fix the displayTranscriptionResult function
"""

# Read the clean HTML file
with open('/Users/jihunkong/teaching_analize/clean_aiboa_ui.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the old function with the correct one
old_function = """function displayTranscriptionResult(data) {
            const resultDiv = document.getElementById('transcription-result');
            let html = '<h4>🎙️ 전사 완료!</h4>';
            
            if (data.transcript) {
                html += `
                    <div style="margin: 15px 0;">
                        <strong>전사 결과:</strong><br>
                        <div style="max-height: 200px; overflow-y: auto; padding: 15px; background: #f8f9fa; border-radius: 5px; margin-top: 10px; border: 1px solid #dee2e6;">
                            ${data.transcript}
                        </div>
                    </div>
                `;
            }
            
            if (data.video_title) {
                html += `<div style="margin: 10px 0;"><strong>영상 제목:</strong> ${data.video_title}</div>`;
            }
            
            if (data.language_detected) {
                html += `<div style="margin: 10px 0;"><strong>감지된 언어:</strong> ${data.language_detected}</div>`;
            }
            
            resultDiv.innerHTML = html;
        }"""

new_function = """function displayTranscriptionResult(data) {
            console.log('Transcription data received:', data);
            const resultDiv = document.getElementById('transcription-result');
            let html = '<h4>🎙️ 전사 완료!</h4>';
            
            // Handle the actual API response format
            let transcriptText = '';
            if (data.result && data.result.text) {
                transcriptText = data.result.text;
            } else if (data.transcript) {
                transcriptText = data.transcript;
            }
            
            if (transcriptText) {
                html += `
                    <div style="margin: 15px 0;">
                        <strong>📄 전사 결과:</strong><br>
                        <div style="max-height: 300px; overflow-y: auto; padding: 15px; background: #f8f9fa; border-radius: 8px; margin-top: 10px; border: 1px solid #dee2e6; white-space: pre-wrap; font-family: monospace; line-height: 1.5;">
                            ${transcriptText}
                        </div>
                    </div>
                `;
            } else {
                html += `
                    <div style="margin: 15px 0; padding: 15px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; color: #856404;">
                        ⚠️ 전사 텍스트를 찾을 수 없습니다.<br>
                        <details style="margin-top: 10px;">
                            <summary>디버그 정보 보기</summary>
                            <pre style="font-size: 0.8em; max-height: 200px; overflow-y: auto;">${JSON.stringify(data, null, 2)}</pre>
                        </details>
                    </div>
                `;
            }
            
            // Show video info if available
            if (data.result) {
                if (data.result.title) {
                    html += `<div style="margin: 10px 0; padding: 10px; background: #e3f2fd; border-radius: 5px;"><strong>🎬 영상 제목:</strong> ${data.result.title}</div>`;
                }
                if (data.result.language) {
                    html += `<div style="margin: 10px 0; padding: 10px; background: #f3e5f5; border-radius: 5px;"><strong>🌐 언어:</strong> ${data.result.language}</div>`;
                }
                if (data.result.duration) {
                    html += `<div style="margin: 10px 0; padding: 10px; background: #e8f5e8; border-radius: 5px;"><strong>⏱️ 길이:</strong> ${data.result.duration}</div>`;
                }
            }
            
            if (data.completed_at) {
                const completedTime = new Date(data.completed_at).toLocaleString();
                html += `<div style="margin: 15px 0; font-size: 0.9em; color: #666; text-align: right;">✅ 전사 완료: ${completedTime}</div>`;
            }
            
            resultDiv.innerHTML = html;
        }"""

# Replace the function
content = content.replace(old_function, new_function)

# Write to a new file
with open('fixed_aiboa_ui.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed HTML created with working displayTranscriptionResult function")