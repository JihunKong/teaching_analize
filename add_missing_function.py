#!/usr/bin/env python3
"""
Add the missing pollJobStatus function to the HTML
"""

# Read current HTML
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the position to insert the function (before the switchTab function)
missing_function = '''
        async function pollJobStatus(jobId, type) {
            const maxAttempts = 24; // 2 minutes with 5-second intervals
            let attempts = 0;
            
            const pollInterval = setInterval(async () => {
                attempts++;
                
                try {
                    const response = await fetch(`/api/transcribe/${jobId}`, {
                        headers: {
                            'X-API-Key': API_KEY
                        }
                    });
                    
                    const data = await response.json();
                    const status = data.status;
                    
                    console.log(`Poll attempt ${attempts}: Status = ${status}`);
                    
                    if (status === 'completed') {
                        clearInterval(pollInterval);
                        displayTranscriptionResult(data);
                    } else if (status === 'failed') {
                        clearInterval(pollInterval);
                        const resultDiv = document.getElementById('transcription-result');
                        resultDiv.innerHTML = `<div style="color: red;">❌ 전사 실패: ${data.error || '알 수 없는 오류'}</div>`;
                    } else if (attempts >= maxAttempts) {
                        clearInterval(pollInterval);
                        const resultDiv = document.getElementById('transcription-result');
                        resultDiv.innerHTML = `<div style="color: orange;">⏰ 시간 초과: 전사가 예상보다 오래 걸리고 있습니다.</div>`;
                    }
                } catch (error) {
                    console.error('Poll error:', error);
                    if (attempts >= maxAttempts) {
                        clearInterval(pollInterval);
                        const resultDiv = document.getElementById('transcription-result');
                        resultDiv.innerHTML = `<div style="color: red;">❌ 상태 확인 실패: ${error.message}</div>`;
                    }
                }
            }, 5000); // Poll every 5 seconds
        }
        
        function displayTranscriptionResult(data) {
            const resultDiv = document.getElementById('transcription-result');
            let html = '<h4>🎙️ 전사 완료!</h4>';
            
            if (data.transcript) {
                html += `
                    <div style="margin: 15px 0;">
                        <strong>전사 결과:</strong><br>
                        <div style="max-height: 200px; overflow-y: auto; padding: 10px; background: #f8f9fa; border-radius: 5px; margin-top: 5px;">
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
        }
        '''

# Insert the function before switchTab function
switch_tab_pos = content.find('function switchTab(tabName)')
if switch_tab_pos > 0:
    content = content[:switch_tab_pos] + missing_function + '\n        ' + content[switch_tab_pos:]
else:
    # If switchTab not found, insert before closing script tag
    script_end = content.rfind('</script>')
    content = content[:script_end] + missing_function + '\n    ' + content[script_end:]

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Missing pollJobStatus function added")