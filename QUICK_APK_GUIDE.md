# 🚀 빠른 APK 생성 가이드 (5분 완성)

## 📋 준비사항
- Flask 서버 실행
- 브라우저 (Chrome 권장)
- 인터넷 연결

## ⚡ 단계별 APK 생성

### 1단계: Flask 서버 실행
```bash
cd schedule_app
python app.py
```

### 2단계: IP 주소 확인
```bash
python get_ip.py
```

### 3단계: PWA Builder 접속
1. 브라우저에서 [PWA Builder](https://www.pwabuilder.com/) 접속
2. URL 입력란에 IP 주소 입력 (예: `http://192.168.1.100:5000`)
3. "Start" 버튼 클릭

### 3단계: APK 생성
1. "Build My PWA" 버튼 클릭
2. "Android" 탭 선택
3. "Generate Package" 버튼 클릭
4. APK 파일 다운로드

## 📱 APK 설치 방법

### Android 설정
1. 설정 → 휴대전화 정보 → 빌드 번호 7번 탭
2. 설정 → 개발자 옵션 → "알 수 없는 소스" 활성화

### APK 설치
1. 다운로드한 APK 파일 클릭
2. "설치" 버튼 클릭
3. 설치 완료 후 앱 실행

## 🎯 결과
- ✅ 네이티브 앱처럼 홈 화면에 아이콘 표시
- ✅ 오프라인 기능 지원
- ✅ 모든 일정관리 기능 사용 가능
- ✅ 센터별 색상 구분
- ✅ 정산관리 및 세금제외 기능

## 🔧 문제 해결

### PWA Builder에서 오류 발생 시
1. **HTTPS 필요 오류**: 무시하고 진행 (로컬 개발용)
2. **아이콘 오류**: 기본 아이콘 사용
3. **매니페스트 오류**: manifest.json 파일 확인

### APK 설치 오류 시
1. **"알 수 없는 소스" 활성화 확인
2. **기존 앱 제거 후 재설치
3. **다른 APK 생성기 사용

## 🌐 대안 방법

### 온라인 APK 생성기
- [AppMySite](https://www.appmysite.com/)
- [BuildFire](https://buildfire.com/)
- [AppMakr](https://appmakr.com/)

### 사용법
1. 앱 이름: "일정관리"
2. 앱 URL: `http://localhost:5000`
3. 아이콘: 기본 아이콘 사용
4. "Build App" 클릭

## 📞 지원

문제가 발생하면:
1. Flask 서버가 실행 중인지 확인
2. 브라우저에서 `http://localhost:5000` 접속 테스트
3. 다른 브라우저로 시도
4. PWA Builder 대신 다른 도구 사용

## 🎉 완료!

APK 파일이 성공적으로 생성되면 안드로이드 기기에 설치하여 네이티브 앱처럼 사용할 수 있습니다! 