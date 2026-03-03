# InterviewMate Overlay

InterviewMate 웹앱을 Zoom/Google Meet 위에 반투명하게 띄우는 macOS 네이티브 앱.

## 요구사항

- macOS 13+ (Ventura)
- Swift 5.9+

## 빌드 & 실행

```bash
bash build.sh
open ".build/InterviewMate Overlay.app"
```

## 기능

### 투명 플로팅 윈도우

- `https://interviewmate.ing`을 WKWebView로 로드
- 기본 투명도 85%, 항상 최상위에 표시
- 윈도우 위치 자동 저장/복원

### 메뉴바 컨트롤

- **투명도 슬라이더** (10% ~ 100%)
- **항상 위에 토글**
- **클릭 통과 토글** — 투명 창 뒤의 Zoom/Meet 조작용
- **URL 변경** — localhost 개발용
- **새로고침** (⌘R)

### 키보드 단축키

| 단축키 | 기능 |
|--------|------|
| `⌘ ↑/↓` | 투명도 조절 (10% 단위) |
| `⌘⇧T` | 클릭 통과 토글 |
| `⌘⇧P` | 항상 위에 토글 |

## 파일 구조

```
overlay/
├── Package.swift
├── build.sh
├── Sources/
│   └── InterviewMateOverlay/
│       ├── main.swift
│       ├── AppDelegate.swift
│       ├── OverlayWindow.swift
│       └── WebViewController.swift
└── Resources/
    └── Info.plist
```
