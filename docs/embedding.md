# AKeeON-T 위젯 임베딩 가이드

## 개요

AKeeON-T 챗봇 위젯을 웹사이트에 임베드하는 방법을 설명합니다.

## 기본 임베딩

### 1. 스크립트 태그 추가

HTML 페이지의 `<head>` 또는 `<body>` 태그에 다음 스크립트를 추가합니다:

```html
<script src="https://your-domain.com/snopsql-widget.min.js" 
        data-project-id="YOUR_PROJECT_ID" 
        data-theme="auto">
</script>
```

### 2. 설정 옵션

| 속성 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `data-project-id` | string | - | 프로젝트 ID (필수) |
| `data-theme` | string | "auto" | 테마 설정 ("light", "dark", "auto") |
| `data-position` | string | "bottom-right" | 버튼 위치 ("bottom-right", "bottom-left") |
| `data-language` | string | "ko" | 언어 설정 ("ko", "en") |

### 3. 완전한 예제

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AKeeON-T 위젯 예제</title>
    
    <!-- AKeeON-T 위젯 스크립트 -->
    <script src="https://your-domain.com/snopsql-widget.min.js" 
            data-project-id="demo-project-123" 
            data-theme="auto"
            data-position="bottom-right"
            data-language="ko">
    </script>
</head>
<body>
    <h1>AKeeON-T 챗봇 위젯 예제</h1>
    <p>우하단의 채팅 버튼을 클릭하여 매출 데이터를 분석해보세요!</p>
</body>
</html>
```

## 고급 설정

### 1. JavaScript API 사용

위젯을 프로그래밍 방식으로 제어할 수 있습니다:

```javascript
// 위젯 초기화
window.AKeeONWidget.init({
    projectId: 'your-project-id',
    theme: 'light',
    position: 'bottom-right',
    language: 'ko'
});

// 위젯 열기
window.AKeeONWidget.open();

// 위젯 닫기
window.AKeeONWidget.close();

// 위젯 토글
window.AKeeONWidget.toggle();

// 이벤트 리스너 등록
window.AKeeONWidget.on('open', () => {
    console.log('위젯이 열렸습니다');
});

window.AKeeONWidget.on('close', () => {
    console.log('위젯이 닫혔습니다');
});

window.AKeeONWidget.on('message', (data) => {
    console.log('새 메시지:', data);
});
```

### 2. 커스텀 스타일링

CSS를 사용하여 위젯의 외관을 커스터마이징할 수 있습니다:

```css
/* 위젯 버튼 커스터마이징 */
.akeeon-widget-button {
    background-color: #007bff !important;
    border-radius: 50% !important;
    box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3) !important;
}

/* 위젯 패널 커스터마이징 */
.akeeon-widget-panel {
    border-radius: 12px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
}

/* 위젯 헤더 커스터마이징 */
.akeeon-widget-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}
```

## 보안 설정

### 1. Origin 허용 목록

백엔드에서 허용된 도메인을 설정해야 합니다:

```python
# backend/app/core/config.py
ALLOWED_ORIGINS = [
    "https://your-domain.com",
    "https://www.your-domain.com",
    "http://localhost:3000"  # 개발 환경
]
```

### 2. CSP (Content Security Policy)

웹사이트에 CSP를 설정하는 경우 다음 정책을 추가하세요:

```html
<meta http-equiv="Content-Security-Policy" 
      content="frame-src 'self' https://your-domain.com; 
               script-src 'self' 'unsafe-inline' https://your-domain.com;">
```

## React/Vue/Angular 통합

### React 예제

```jsx
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    // 위젯 스크립트 동적 로드
    const script = document.createElement('script');
    script.src = 'https://your-domain.com/snopsql-widget.min.js';
    script.setAttribute('data-project-id', 'your-project-id');
    script.setAttribute('data-theme', 'auto');
    document.head.appendChild(script);

    return () => {
      document.head.removeChild(script);
    };
  }, []);

  return (
    <div>
      <h1>AKeeON-T 위젯이 포함된 React 앱</h1>
    </div>
  );
}
```

### Vue 예제

```vue
<template>
  <div>
    <h1>AKeeON-T 위젯이 포함된 Vue 앱</h1>
  </div>
</template>

<script>
export default {
  mounted() {
    // 위젯 스크립트 동적 로드
    const script = document.createElement('script');
    script.src = 'https://your-domain.com/snopsql-widget.min.js';
    script.setAttribute('data-project-id', 'your-project-id');
    script.setAttribute('data-theme', 'auto');
    document.head.appendChild(script);
  }
}
</script>
```

## 트러블슈팅

### 1. 위젯이 로드되지 않는 경우

- 브라우저 개발자 도구에서 콘솔 에러 확인
- 네트워크 탭에서 스크립트 로드 상태 확인
- `data-project-id`가 올바르게 설정되었는지 확인

### 2. CORS 오류가 발생하는 경우

- 백엔드의 `ALLOWED_ORIGINS` 설정 확인
- 도메인이 허용 목록에 포함되어 있는지 확인

### 3. 위젯이 표시되지 않는 경우

- CSS 충돌 확인
- z-index 값 확인
- 페이지 로드 완료 후 위젯이 초기화되는지 확인

## 성능 최적화

### 1. 지연 로딩

페이지 로드 완료 후 위젯을 로드하여 초기 로딩 성능을 개선할 수 있습니다:

```javascript
window.addEventListener('load', () => {
    const script = document.createElement('script');
    script.src = 'https://your-domain.com/snopsql-widget.min.js';
    script.setAttribute('data-project-id', 'your-project-id');
    document.head.appendChild(script);
});
```

### 2. 조건부 로딩

사용자 상호작용 후에만 위젯을 로드할 수 있습니다:

```javascript
document.getElementById('chat-button').addEventListener('click', () => {
    if (!window.AKeeONWidget) {
        // 위젯 로드
        const script = document.createElement('script');
        script.src = 'https://your-domain.com/snopsql-widget.min.js';
        script.setAttribute('data-project-id', 'your-project-id');
        document.head.appendChild(script);
    } else {
        window.AKeeONWidget.open();
    }
});
```
