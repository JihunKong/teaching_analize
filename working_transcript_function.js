        function displayTranscriptionResult(data) {
            console.log('Transcription data received:', data);
            const resultDiv = document.getElementById('transcription-result');
            let html = '<h4>🎙️ 전사 완료!</h4>';
            
            // Handle different response formats
            let transcriptText = '';
            let videoTitle = '';
            let detectedLanguage = '';
            
            if (data.result && data.result.text) {
                transcriptText = data.result.text;
            } else if (data.transcript) {
                transcriptText = data.transcript;
            }
            
            if (data.result && data.result.title) {
                videoTitle = data.result.title;
            } else if (data.video_title) {
                videoTitle = data.video_title;
            }
            
            if (data.result && data.result.language) {
                detectedLanguage = data.result.language;
            } else if (data.language_detected) {
                detectedLanguage = data.language_detected;
            }
            
            // Display transcript text
            if (transcriptText) {
                html += `
                    <div style="margin: 15px 0;">
                        <strong>📄 전사 결과:</strong><br>
                        <div style="max-height: 300px; overflow-y: auto; padding: 15px; background: #f8f9fa; border-radius: 8px; margin-top: 10px; border: 1px solid #dee2e6; white-space: pre-wrap; font-family: 'Courier New', monospace; line-height: 1.5;">
                            ${transcriptText}
                        </div>
                    </div>
                `;
            } else {
                html += `
                    <div style="margin: 15px 0; padding: 15px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; color: #856404;">
                        ⚠️ 전사 텍스트를 찾을 수 없습니다. 원본 응답을 확인해주세요:<br>
                        <pre style="margin-top: 10px; font-size: 0.8em; max-height: 200px; overflow-y: auto;">${JSON.stringify(data, null, 2)}</pre>
                    </div>
                `;
            }
            
            // Display video title if available
            if (videoTitle) {
                html += `
                    <div style="margin: 10px 0; padding: 10px; background: #e3f2fd; border-radius: 5px;">
                        <strong>🎬 영상 제목:</strong> ${videoTitle}
                    </div>
                `;
            }
            
            // Display detected language if available
            if (detectedLanguage) {
                html += `
                    <div style="margin: 10px 0; padding: 10px; background: #f3e5f5; border-radius: 5px;">
                        <strong>🌐 감지된 언어:</strong> ${detectedLanguage}
                    </div>
                `;
            }
            
            // Display segments if available
            if (data.result && data.result.segments && data.result.segments.length > 0) {
                html += `
                    <div style="margin: 15px 0;">
                        <strong>⏰ 시간별 세그먼트:</strong>
                        <div style="max-height: 200px; overflow-y: auto; margin-top: 10px;">
                `;
                data.result.segments.forEach((segment, index) => {
                    html += `
                        <div style="padding: 8px; margin: 5px 0; background: #f8f9fa; border-left: 3px solid #667eea; border-radius: 3px;">
                            <small style="color: #666;">${segment.start}s - ${segment.end}s:</small><br>
                            ${segment.text}
                        </div>
                    `;
                });
                html += `</div></div>`;
            }
            
            // Add completion info
            if (data.completed_at) {
                const completedTime = new Date(data.completed_at).toLocaleString();
                html += `
                    <div style="margin: 15px 0; font-size: 0.9em; color: #666; text-align: right;">
                        ✅ 전사 완료: ${completedTime}
                    </div>
                `;
            }
            
            resultDiv.innerHTML = html;
        }