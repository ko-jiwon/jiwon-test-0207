# 뉴스 분석 및 콘텐츠 생성 시스템

검색 키워드를 입력하면 관련 뉴스 기사를 크롤링하고, 분석하여 다양한 콘텐츠를 자동으로 생성하는 시스템입니다.

## 주요 기능

1. **뉴스 크롤링**: 네이버 뉴스에서 키워드로 검색하여 최대 10개의 뉴스 기사 수집
2. **기사 분석**: 각 기사별로 제목, 요약, 핵심 키워드 추출
3. **키워드 필터링**: 핵심 키워드를 선택하여 관련 기사만 필터링하여 보기
4. **종합 분석**: 모든 기사를 종합하여 핵심 주제 추출
5. **콘텐츠 생성**:
   - 1200자 블로그 글
   - 200자 내외 스레드 콘텐츠
   - 인스타그램 5장짜리 카드뉴스

## 설치 방법

### 1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. KoNLPy 설정 (선택사항)

KoNLPy는 Java가 필요합니다. Java가 설치되어 있지 않은 경우, 키워드 추출 기능이 제한적으로 작동할 수 있습니다.

**macOS:**
```bash
brew install openjdk
```

**Linux:**
```bash
sudo apt-get install default-jdk
```

**Windows:**
[Oracle JDK](https://www.oracle.com/java/technologies/downloads/) 또는 [OpenJDK](https://adoptium.net/) 설치

### 3. OpenAI API 키 설정 (선택사항)

더 나은 요약 및 콘텐츠 생성을 위해 OpenAI API 키를 설정할 수 있습니다.

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```
OPENAI_API_KEY=your_openai_api_key_here
```

API 키가 없어도 기본 기능은 작동하지만, 요약과 콘텐츠 생성 품질이 제한적일 수 있습니다.

## 실행 방법

```bash
python app.py
```

브라우저에서 `http://localhost:5000`으로 접속하세요.

## 사용 방법

1. 검색창에 원하는 키워드를 입력합니다 (예: "인공지능", "반도체", "K-팝")
2. "검색" 버튼을 클릭합니다
3. 뉴스 기사가 분석되고 결과가 표시됩니다
4. 핵심 키워드를 클릭하여 해당 키워드로 필터링된 기사만 볼 수 있습니다
5. 생성된 콘텐츠(블로그, 스레드, 카드뉴스)를 확인하고 복사할 수 있습니다

## 프로젝트 구조

```
오팔실습/
├── app.py                 # Flask 메인 애플리케이션
├── crawler.py             # 뉴스 크롤링 모듈
├── analyzer.py            # 뉴스 분석 모듈 (요약, 키워드 추출)
├── content_generator.py   # 콘텐츠 생성 모듈
├── requirements.txt       # 필요한 패키지 목록
├── templates/
│   └── index.html        # 메인 HTML 템플릿
└── static/
    ├── css/
    │   └── style.css     # 스타일시트
    └── js/
        └── main.js       # 프론트엔드 JavaScript
```

## 주의사항

- 뉴스 크롤링은 네이버 뉴스 검색 결과를 기반으로 합니다
- 일부 뉴스 사이트는 크롤링을 제한할 수 있습니다
- OpenAI API를 사용하지 않는 경우, 요약과 콘텐츠 생성은 기본 템플릿을 사용합니다
- KoNLPy가 제대로 작동하지 않는 경우, 간단한 키워드 추출 방식으로 대체됩니다

## 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

