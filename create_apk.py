#!/usr/bin/env python3
"""
일정관리 앱 APK 생성 스크립트
PWA를 APK로 변환하는 간단한 도구
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

def check_requirements():
    """필요한 도구들이 설치되어 있는지 확인"""
    print("🔍 필요한 도구들을 확인하는 중...")
    
    # Node.js 확인
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
        print("✅ Node.js 설치됨")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js가 설치되지 않았습니다.")
        print("   https://nodejs.org/에서 다운로드하세요.")
        return False
    
    # npm 확인
    try:
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
        print("✅ npm 설치됨")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm이 설치되지 않았습니다.")
        return False
    
    return True

def install_bubblewrap():
    """Bubblewrap 설치"""
    print("📦 Bubblewrap 설치 중...")
    try:
        subprocess.run(['npm', 'install', '-g', '@bubblewrap/cli'], check=True)
        print("✅ Bubblewrap 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Bubblewrap 설치 실패: {e}")
        return False

def create_apk_with_bubblewrap():
    """Bubblewrap을 사용하여 APK 생성"""
    print("🔨 APK 생성 중...")
    
    # 현재 디렉토리
    current_dir = Path.cwd()
    apk_dir = current_dir / "apk_build"
    
    # 기존 빌드 디렉토리 정리
    if apk_dir.exists():
        import shutil
        shutil.rmtree(apk_dir)
    
    # Bubblewrap 초기화
    try:
        subprocess.run([
            'bubblewrap', 'init',
            '--manifest', 'http://localhost:5000/static/manifest.json',
            '--directory', str(apk_dir)
        ], check=True)
        print("✅ Bubblewrap 프로젝트 초기화 완료")
    except subprocess.CalledProcessError as e:
        print(f"❌ Bubblewrap 초기화 실패: {e}")
        return False
    
    # APK 빌드
    try:
        subprocess.run(['bubblewrap', 'build'], cwd=apk_dir, check=True)
        print("✅ APK 빌드 완료")
        
        # APK 파일 찾기
        apk_files = list(apk_dir.rglob("*.apk"))
        if apk_files:
            apk_file = apk_files[0]
            target_file = current_dir / "일정관리앱.apk"
            import shutil
            shutil.copy2(apk_file, target_file)
            print(f"🎉 APK 파일 생성 완료: {target_file}")
            return True
        else:
            print("❌ APK 파일을 찾을 수 없습니다.")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ APK 빌드 실패: {e}")
        return False

def create_apk_with_pwa_builder():
    """PWA Builder를 사용하여 APK 생성 (온라인)"""
    print("🌐 PWA Builder를 사용한 APK 생성 방법:")
    print("1. 브라우저에서 https://www.pwabuilder.com/ 접속")
    print("2. URL 입력: http://localhost:5000")
    print("3. 'Start' 버튼 클릭")
    print("4. 'Build My PWA' 클릭")
    print("5. 'Android' 탭 선택")
    print("6. 'Generate Package' 클릭")
    print("7. APK 파일 다운로드")

def main():
    """메인 함수"""
    print("📱 일정관리 앱 APK 생성기")
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
    
    print("\n📋 APK 생성 방법을 선택하세요:")
    print("1. Bubblewrap 사용 (로컬)")
    print("2. PWA Builder 사용 (온라인)")
    print("3. 종료")
    
    choice = input("\n선택 (1-3): ").strip()
    
    if choice == "1":
        if check_requirements():
            if install_bubblewrap():
                create_apk_with_bubblewrap()
        else:
            print("\n💡 대안: PWA Builder를 사용하세요.")
            create_apk_with_pwa_builder()
    
    elif choice == "2":
        create_apk_with_pwa_builder()
    
    elif choice == "3":
        print("👋 종료합니다.")
    
    else:
        print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main() 