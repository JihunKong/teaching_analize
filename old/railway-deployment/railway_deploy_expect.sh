#!/usr/bin/expect -f

# Railway 대화형 배포 자동화 스크립트
set timeout 30

puts "🚀 Railway 자동 배포 (Expect 사용)"
puts "==================================\n"

# 1. Transcription 서비스 선택 및 배포
puts "📦 Transcription Service 배포..."
cd services/transcription

spawn railway service
expect {
    "Select a service" {
        send "1\r"
        expect eof
    }
    timeout {
        puts "Service selection timeout"
    }
}

# 배포 실행
spawn railway up --detach
expect {
    "Uploading" {
        puts "✓ Transcription 업로드 중..."
    }
    timeout {
        puts "Upload timeout"
    }
}
expect eof

# 2. Analysis 서비스 선택 및 배포
puts "\n📦 Analysis Service 배포..."
cd ../analysis

spawn railway service
expect {
    "Select a service" {
        send "2\r"
        expect eof
    }
    timeout {
        puts "Service selection timeout"
    }
}

# 배포 실행
spawn railway up --detach
expect {
    "Uploading" {
        puts "✓ Analysis 업로드 중..."
    }
    timeout {
        puts "Upload timeout"
    }
}
expect eof

puts "\n✅ 배포 완료!"
puts "Dashboard에서 확인: https://railway.app/project/379dfeea-b7f3-47cf-80c8-4d6d6b72329f"