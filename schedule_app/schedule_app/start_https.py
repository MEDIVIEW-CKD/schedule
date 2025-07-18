#!/usr/bin/env python3
"""
HTTPS 터널을 생성하여 PWA Builder에서 사용할 수 있도록 하는 스크립트
"""

import subprocess
import time
import requests
import json
import os
from pathlib import Path

def check_ngrok():
    """ngrok이 설치되어 있는지 확인"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok이 설치되어 있습니다.")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def install_ngrok():
    """ngrok 설치"""
    print("📦 ngrok 설치 중...")
    try:
        # Windows용 ngrok 다운로드 (간단한 방법)
        print("💡 ngrok을 수동으로 설치해주세요:")
        print("1. https://ngrok.com/ 접속")
        print("2. 무료 계정 가입")
        print("3. ngrok 다운로드")
        print("4. 압축 해제 후 PATH에 추가")
        return False
    except Exception as e:
        print(f"❌ ngrok 설치 실패: {e}")
        return False

def start_ngrok_tunnel(port=5000):
    """ngrok 터널 시작"""
    print(f"🚀 ngrok 터널 시작 중 (포트: {port})...")
    
    try:
        # ngrok 터널 시작
        process = subprocess.Popen(
            ['ngrok', 'http', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 터널 URL 가져오기
        time.sleep(3)  # ngrok이 시작될 때까지 대기
        
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            tunnels = response.json()
            
            if tunnels['tunnels']:
                https_url = tunnels['tunnels'][0]['public_url']
                print(f"✅ HTTPS 터널 생성 완료!")
                print(f"🔗 HTTPS URL: {https_url}")
                print()
                print("📱 PWA Builder에서 사용할 URL:")
                print(f"   {https_url}")
                print()
                print("💡 이 URL을 PWA Builder에 입력하세요!")
                print("🔄 터널을 중지하려면 Ctrl+C를 누르세요.")
                
                return https_url, process
            else:
                print("❌ 터널을 생성할 수 없습니다.")
                process.terminate()
                return None, None
                
        except requests.exceptions.RequestException:
            print("❌ ngrok API에 접속할 수 없습니다.")
            process.terminate()
            return None, None
            
    except Exception as e:
        print(f"❌ ngrok 터널 시작 실패: {e}")
        return None, None

def main():
    print("🌐 HTTPS 터널 생성기")
    print("=" * 40)
    
    # Flask 서버가 실행 중인지 확인
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✅ Flask 서버가 실행 중입니다.")
        else:
            print("❌ Flask 서버에 접속할 수 없습니다.")
            print("   python app.py를 실행하세요.")
            return
    except requests.exceptions.RequestException:
        print("❌ Flask 서버에 접속할 수 없습니다.")
        print("   python app.py를 실행하세요.")
        return
    
    # ngrok 확인 및 설치
    if not check_ngrok():
        print("❌ ngrok이 설치되지 않았습니다.")
        if not install_ngrok():
            print("\n💡 대안 방법:")
            print("1. IP 주소 확인: python get_ip.py")
            print("2. 로컬 IP 주소를 PWA Builder에 입력")
            return
    
    # HTTPS 터널 시작
    https_url, process = start_ngrok_tunnel()
    
    if https_url and process:
        try:
            # 터널이 실행되는 동안 대기
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 터널을 중지합니다...")
            process.terminate()
            print("✅ 터널이 중지되었습니다.")

if __name__ == "__main__":
    main() 