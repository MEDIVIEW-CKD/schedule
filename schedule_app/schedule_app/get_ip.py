#!/usr/bin/env python3
"""
컴퓨터의 IP 주소를 확인하는 스크립트
"""

import socket
import requests

def get_local_ip():
    """로컬 IP 주소 가져오기"""
    try:
        # 로컬 IP 주소 가져오기
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"로컬 IP 주소를 가져올 수 없습니다: {e}")
        return None

def get_public_ip():
    """공개 IP 주소 가져오기"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except Exception as e:
        print(f"공개 IP 주소를 가져올 수 없습니다: {e}")
        return None

def main():
    print("🌐 IP 주소 확인")
    print("=" * 40)
    
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    if local_ip:
        print(f"📱 로컬 IP 주소: {local_ip}")
        print(f"🔗 로컬 접속 URL: http://{local_ip}:5000")
        print()
    
    if public_ip:
        print(f"🌍 공개 IP 주소: {public_ip}")
        print(f"🔗 공개 접속 URL: http://{public_ip}:5000")
        print()
    
    print("📋 PWA Builder에서 사용할 URL:")
    if local_ip:
        print(f"   로컬 네트워크: http://{local_ip}:5000")
    if public_ip:
        print(f"   인터넷: http://{public_ip}:5000")
    
    print()
    print("💡 참고사항:")
    print("- 같은 Wi-Fi 네트워크: 로컬 IP 사용")
    print("- 다른 네트워크: 공개 IP 사용 (방화벽 설정 필요)")
    print("- PWA Builder: 공개 IP 권장")

if __name__ == "__main__":
    main() 