#!/usr/bin/env python3
"""
Railway 배포 자동화 스크립트
subprocess와 pty를 사용하여 대화형 프롬프트 처리
"""

import subprocess
import os
import sys
import time
import select
import pty
import signal

def run_interactive_command(command, responses):
    """
    대화형 명령 실행 및 자동 응답
    """
    # Create a pseudo-terminal
    master, slave = pty.openpty()
    
    # Start the process
    process = subprocess.Popen(
        command,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        shell=True,
        preexec_fn=os.setsid
    )
    
    os.close(slave)
    
    # Read output and respond
    output = ""
    response_index = 0
    
    while True:
        # Check if process is still running
        if process.poll() is not None:
            break
            
        # Check for available data
        ready, _, _ = select.select([master], [], [], 0.1)
        
        if ready:
            try:
                data = os.read(master, 1024).decode('utf-8')
                output += data
                print(data, end='', flush=True)
                
                # Check if we need to send a response
                if response_index < len(responses):
                    for trigger, response in responses[response_index:]:
                        if trigger in output:
                            time.sleep(0.5)  # Small delay
                            os.write(master, f"{response}\n".encode())
                            response_index += 1
                            break
                            
            except OSError:
                break
    
    os.close(master)
    process.wait()
    
    return process.returncode, output

def main():
    print("🚀 Railway 자동 배포 시작")
    print("=" * 40)
    
    # Change to project root
    os.chdir('/Users/jihunkong/teaching_analize')
    
    # 1. Link to project (if needed)
    print("\n📎 프로젝트 연결 확인...")
    result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
    if 'lively-surprise' in result.stdout:
        print("✓ 프로젝트 연결됨: lively-surprise")
    else:
        print("프로젝트 연결 필요...")
        run_interactive_command(
            'railway link',
            [
                ('Select a project', '1'),  # Select first project
                ('Select an environment', '1')  # Select production
            ]
        )
    
    # 2. Deploy Transcription Service
    print("\n📦 Transcription Service 배포...")
    os.chdir('services/transcription')
    
    # Try to select service and deploy
    print("서비스 선택 중...")
    returncode, output = run_interactive_command(
        'railway service',
        [
            ('Select a service', '1')  # Select first service
        ]
    )
    
    if returncode == 0:
        print("\n배포 시작...")
        subprocess.run(['railway', 'up', '--detach'], check=False)
        print("✓ Transcription 배포 시작됨")
    
    # 3. Deploy Analysis Service
    print("\n📦 Analysis Service 배포...")
    os.chdir('../analysis')
    
    print("서비스 선택 중...")
    returncode, output = run_interactive_command(
        'railway service',
        [
            ('Select a service', '2')  # Select second service
        ]
    )
    
    if returncode == 0:
        print("\n배포 시작...")
        subprocess.run(['railway', 'up', '--detach'], check=False)
        print("✓ Analysis 배포 시작됨")
    
    # 4. Set environment variables
    print("\n🔧 환경변수 설정...")
    os.chdir('../..')
    
    # Transcription service variables
    env_vars_transcription = {
        'PORT': '8000',
        'PYTHONUNBUFFERED': '1',
        'SERVICE_NAME': 'transcription'
    }
    
    for key, value in env_vars_transcription.items():
        subprocess.run(
            ['railway', 'variables', 'set', f'{key}={value}', '--service', 'transcription'],
            capture_output=True
        )
    
    # Analysis service variables
    env_vars_analysis = {
        'PORT': '8001',
        'PYTHONUNBUFFERED': '1',
        'SERVICE_NAME': 'analysis'
    }
    
    for key, value in env_vars_analysis.items():
        subprocess.run(
            ['railway', 'variables', 'set', f'{key}={value}', '--service', 'analysis'],
            capture_output=True
        )
    
    print("✓ 환경변수 설정 완료")
    
    # 5. Check status
    print("\n📊 배포 상태:")
    subprocess.run(['railway', 'status'])
    
    print("\n" + "=" * 40)
    print("✅ 배포 프로세스 완료!")
    print("\n확인 방법:")
    print("1. Dashboard: https://railway.app/project/379dfeea-b7f3-47cf-80c8-4d6d6b72329f")
    print("2. Logs: railway logs --service transcription")
    print("3. Logs: railway logs --service analysis")

if __name__ == "__main__":
    main()