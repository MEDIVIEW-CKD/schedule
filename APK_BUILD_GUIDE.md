# 📱 APK 파일 생성 가이드

## 방법 1: PWA Builder 사용 (추천)

### 1단계: Flask 서버 실행
```bash
cd schedule_app
python app.py
```

### 2단계: PWA Builder 접속
1. 브라우저에서 [PWA Builder](https://www.pwabuilder.com/) 접속
2. URL 입력: `http://localhost:5000`
3. "Start" 버튼 클릭

### 3단계: APK 생성
1. "Build My PWA" 클릭
2. "Android" 탭 선택
3. "Generate Package" 클릭
4. APK 파일 다운로드

## 방법 2: Bubblewrap 사용

### 1단계: Node.js 설치
```bash
# Node.js가 설치되어 있지 않은 경우
# https://nodejs.org/에서 다운로드
```

### 2단계: Bubblewrap 설치
```bash
npm install -g @bubblewrap/cli
```

### 3단계: 프로젝트 초기화
```bash
bubblewrap init --manifest https://localhost:5000/static/manifest.json
```

### 4단계: APK 빌드
```bash
bubblewrap build
```

## 방법 3: TWA (Trusted Web Activity) 사용

### 1단계: Android Studio 설치
1. [Android Studio](https://developer.android.com/studio) 다운로드
2. 설치 및 설정

### 2단계: TWA 프로젝트 생성
```bash
git clone https://github.com/GoogleChromeLabs/sample-twa.git
cd sample-twa
```

### 3단계: 설정 수정
`app/src/main/AndroidManifest.xml`에서:
```xml
<meta-data android:name="asset_statements" android:resource="@string/asset_statements" />
```

### 4단계: APK 빌드
```bash
./gradlew assembleRelease
```

## 방법 4: 온라인 APK 생성기 사용

### 1단계: 웹사이트 접속
- [AppMySite](https://www.appmysite.com/)
- [BuildFire](https://buildfire.com/)
- [AppMakr](https://appmakr.com/)

### 2단계: 설정
1. 앱 이름: "일정관리"
2. 앱 URL: `http://localhost:5000`
3. 아이콘 업로드
4. 스플래시 스크린 설정

### 3단계: APK 생성
1. "Build App" 클릭
2. APK 파일 다운로드

## 🎨 앱 아이콘 생성

### 온라인 아이콘 생성기
1. [Favicon.io](https://favicon.io/) - 간단한 아이콘 생성
2. [Canva](https://www.canva.com/) - 전문적인 디자인
3. [Figma](https://www.figma.com/) - 무료 디자인 도구

### 아이콘 요구사항
- 192x192 픽셀 (PNG)
- 512x512 픽셀 (PNG)
- 투명 배경 권장
- 단순한 디자인

## 📱 APK 설치 방법

### 개발자 옵션 활성화
1. 설정 → 휴대전화 정보 → 빌드 번호 7번 탭
2. 설정 → 개발자 옵션 → "알 수 없는 소스" 활성화

### APK 설치
1. APK 파일 다운로드
2. 파일 관리자에서 APK 파일 클릭
3. "설치" 버튼 클릭
4. 설치 완료 후 앱 실행

## 🔧 문제 해결

### PWA Builder 오류
- HTTPS 필요: ngrok 사용
- 매니페스트 오류: manifest.json 확인
- 아이콘 오류: 아이콘 파일 경로 확인

### Bubblewrap 오류
- Java JDK 설치 필요
- Android SDK 설치 필요
- 환경 변수 설정 필요

### TWA 오류
- 서명 키 생성 필요
- 패키지 이름 충돌 확인
- 권한 설정 확인

## 🌐 HTTPS 설정 (PWA Builder용)

### ngrok 사용
```bash
# ngrok 설치
npm install -g ngrok

# HTTPS 터널 생성
ngrok http 5000

# 제공된 HTTPS URL 사용
# 예: https://abc123.ngrok.io
```

## 📋 체크리스트

- [ ] Flask 서버 실행
- [ ] 매니페스트 파일 확인
- [ ] 아이콘 파일 생성
- [ ] HTTPS 설정 (선택사항)
- [ ] PWA Builder 접속
- [ ] APK 생성
- [ ] APK 설치 테스트

## 🎯 최종 결과

성공적으로 APK 파일이 생성되면:
- 안드로이드 기기에 직접 설치 가능
- 네이티브 앱처럼 홈 화면에 아이콘 표시
- 오프라인 기능 지원
- 푸시 알림 지원 (추가 설정 필요) 