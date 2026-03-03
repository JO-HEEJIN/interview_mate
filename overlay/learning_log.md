# InterviewMate Overlay — Learning Log

macOS 네이티브 투명 오버레이 앱을 개발하면서 겪은 문제들과 해결 방안을 기록합니다.

---

## 1. WKWebView 투명 윈도우가 빈 화면으로 표시됨

### 문제
`NSWindow`에 `backgroundColor = .clear`, `isOpaque = false`를 설정하고 WKWebView에 `drawsBackground = false`를 적용하면, 웹 콘텐츠는 물론 윈도우 자체도 완전히 투명해져서 타이틀바만 보이는 현상.

### 원인
세 가지 투명도 설정이 동시에 적용되면 모든 레이어가 투명해져 콘텐츠가 보이지 않음.

### 해결
`backgroundColor`, `isOpaque`, `drawsBackground` 설정을 모두 제거하고 **`NSWindow.alphaValue`만 사용**하여 전체 윈도우 투명도를 조절. `alphaValue = 0.85`로 설정하면 웹 콘텐츠가 보이면서 뒤의 앱도 비쳐 보임.

---

## 2. WKWebView가 키보드 이벤트를 소비하여 단축키 작동 안 함

### 문제
`NSEvent.addLocalMonitorForEvents`로 등록한 `⌘↑/↓` (투명도), `⌘⇧T` (클릭 통과) 등의 단축키가 WKWebView에 포커스가 있을 때 작동하지 않음.

### 원인
WKWebView가 키보드 이벤트를 우선 소비하여 NSEvent 모니터에 전달되지 않음.

### 해결
`NSWindow` 서브클래스(`OverlayWindow`)에서 **`performKeyEquivalent(with:)`를 override**하여 WKWebView보다 먼저 이벤트를 가로챔. `OverlayWindowDelegate` 프로토콜을 만들어 AppDelegate에 위임.

```swift
override func performKeyEquivalent(with event: NSEvent) -> Bool {
    let flags = event.modifierFlags.intersection(.deviceIndependentFlagsMask)
    if flags == .command && event.keyCode == 126 { // ⌘↑
        shortcutDelegate?.overlayWindowAdjustOpacity(by: 0.1)
        return true
    }
    return super.performKeyEquivalent(with: event)
}
```

---

## 3. Click-Through 모드를 다시 끌 수 없음

### 문제
`⌘⇧T`로 `ignoresMouseEvents = true`를 설정하면, 윈도우가 포커스를 잃어 키보드 이벤트를 받을 수 없게 되어 다시 토글 불가.

### 시도 1: NSEvent.addGlobalMonitorForEvents
글로벌 이벤트 모니터를 사용했으나, macOS 접근성(Accessibility) 권한이 필요하고 권한이 있어도 불안정하게 작동 (처음 한 번만 되고 이후 무반응).

### 해결: Carbon RegisterEventHotKey
**Carbon API의 `RegisterEventHotKey`** 사용. 접근성 권한 없이 작동하며, 앱이 포커스가 없어도 안정적으로 작동.

```swift
let hotKeyID = EventHotKeyID(signature: OSType(0x494D4F56), id: 1)
RegisterEventHotKey(UInt32(kVK_ANSI_T), UInt32(cmdKey | shiftKey), hotKeyID,
                    GetApplicationEventTarget(), 0, &hotKeyRef)
```

### 추가 문제: 더블 토글
`performKeyEquivalent`과 Carbon 핫키가 동시에 `⌘⇧T`를 잡아서 두 번 토글됨. → `performKeyEquivalent`에서 `⌘⇧T` 제거, Carbon 핫키만 사용.

---

## 4. WKWebView에서 getDisplayMedia "user gesture" 에러

### 문제
WKWebView에서 `navigator.mediaDevices.getDisplayMedia()`를 호출하면 "user gesture" 에러 발생. React의 비동기 이벤트 체인에서 사용자 제스처 컨텍스트가 소실됨.

### 시도한 방법들
1. **WebKit private preferences** (`screenCaptureEnabled`, `mediaDevicesEnabled`) — 도움 안 됨
2. **`requiresUserGestureForGetDisplayMedia` KVC** — 키가 존재하지 않아 앱 크래시
3. **`mockCaptureDevicesEnabled`** — 마이크가 가짜 장치로 대체되어 실제 음성 입력 불가

### 해결
프론트엔드에서 "user gesture" 에러 발생 시 **클릭 가능한 팝업 오버레이**를 표시. 사용자가 "Enable Screen Sharing" 버튼을 클릭하면 새로운 제스처 컨텍스트에서 `getDisplayMedia`를 재시도.

```typescript
if (err.message.includes('user gesture')) {
    // DOM 오버레이 생성 → 버튼 클릭 → doCapture() 재시도
}
```

---

## 5. WKWebView/Safari getDisplayMedia에 오디오 트랙 없음

### 문제
`getDisplayMedia({ audio: true, video: true })` 호출 후 반환된 스트림에 오디오 트랙이 없음. Safari/WKWebView는 화면/윈도우 공유 시 오디오 트랙을 제공하지 않음 (Chrome만 탭 오디오 지원).

### 해결 방향
WKWebView의 getDisplayMedia 한계를 우회하기 위해 **macOS ScreenCaptureKit으로 네이티브 시스템 오디오 캡처** 구현.

---

## 6. ScreenCaptureKit 네이티브 오디오 캡처 구현

### 구조
`SystemAudioCapture.swift` — ScreenCaptureKit의 `SCStream`을 사용하여 시스템 오디오를 캡처.

```
SCShareableContent → SCContentFilter → SCStream → SCStreamOutput
→ CMSampleBuffer → Float32 PCM → base64 → evaluateJavaScript → JS
```

### 주요 설정
```swift
config.capturesAudio = true
config.excludesCurrentProcessAudio = true  // 오버레이 앱 자체 오디오 제외
config.channelCount = 1
config.sampleRate = 16000
```

### TCC 권한
macOS의 Screen Recording 권한이 필요. 첫 실행 시 시스템 다이얼로그가 표시되며, 거부되면 `The user declined TCCs for application, window, display capture` 에러 발생. **시스템 설정 > 개인정보 보호 > 화면 기록**에서 수동 허용 필요.

---

## 7. WebKit이 getDisplayMedia 패치를 지속적으로 리셋 (핵심 문제)

### 문제
WKUserScript로 `navigator.mediaDevices.getDisplayMedia`를 오버라이드하면 초기에는 적용되지만, **WebKit이 2초마다 원래 함수로 복원**함.

### 시도한 방법들

#### 시도 1: 직접 프로퍼티 할당
```javascript
navigator.mediaDevices.getDisplayMedia = patchedFunction;
```
→ WebKit이 주기적으로 리셋. Watchdog 로그로 확인:
```
[NativeAudio] WATCHDOG: patch was removed! Re-applying...
```

#### 시도 2: Object.defineProperty (프로토타입 + 인스턴스)
```javascript
Object.defineProperty(MediaDevices.prototype, 'getDisplayMedia', { value: patchedFn });
Object.defineProperty(navigator.mediaDevices, 'getDisplayMedia', { value: patchedFn });
```
→ 동일하게 WebKit이 리셋. 프로토타입 레벨 패치도 무효화됨.

#### 해결: JavaScript Proxy
`navigator.mediaDevices` 자체를 `Proxy` 객체로 교체. `.getDisplayMedia` 프로퍼티 접근을 가로채서 항상 패치된 함수를 반환. WebKit이 원본 객체의 프로퍼티를 아무리 리셋해도, Proxy를 통해 접근하기 때문에 영향 없음.

```javascript
var realMediaDevices = navigator.mediaDevices;
var proxy = new Proxy(realMediaDevices, {
    get: function(target, prop) {
        if (prop === 'getDisplayMedia') return patchedGetDisplayMedia;
        var val = target[prop];
        return typeof val === 'function' ? val.bind(target) : val;
    },
    set: function(target, prop, value) {
        target[prop] = value;
        return true;
    }
});

Object.defineProperty(navigator, 'mediaDevices', {
    get: function() { return proxy; },
    configurable: true
});
```

이 접근 방식은 **Watchdog 재적용 없이 영구적으로 작동**함을 로그로 확인.

---

## 8. ScriptProcessorNode 오디오 버퍼 처리 버그

### 문제
ScreenCaptureKit은 320 samples(20ms) 단위로 오디오를 전달하지만, ScriptProcessorNode의 `onaudioprocess`는 4096 samples 출력 버퍼를 사용. 원래 코드는 한 번에 하나의 chunk만 소비하여 **4096 samples 중 320만 실제 오디오, 나머지 3776은 무음** (오디오의 92% 손실).

### 증상
`audioQueue`가 무한히 증가: 0 → 93 → 186 → 278 → ... → 739+

### 해결
`onaudioprocess` 콜백에서 **여러 chunk를 합쳐서 출력 버퍼를 완전히 채우도록** 수정:

```javascript
scriptNode.onaudioprocess = function(e) {
    var output = e.outputBuffer.getChannelData(0);
    var offset = 0;
    while (offset < output.length && audioQueue.length > 0) {
        var chunk = audioQueue.shift();
        var copyLen = Math.min(chunk.length, output.length - offset);
        for (var i = 0; i < copyLen; i++) {
            output[offset + i] = chunk[i];
        }
        offset += copyLen;
        if (copyLen < chunk.length) {
            audioQueue.unshift(chunk.subarray(copyLen));
        }
    }
    for (var j = offset; j < output.length; j++) output[j] = 0;
};
```

수정 후 큐가 안정적으로 유지됨 (20-40 범위).

---

## 9. Cross-AudioContext MediaStream 전달 실패 (WebKit 핵심 문제)

### 문제
네이티브 오디오 bridge의 `ScriptProcessorNode → MediaStreamDestination → MediaStream`으로 생성한 오디오 스트림을, 프론트엔드의 `AudioContext.createMediaStreamSource()`로 읽으면 **오디오가 전달되지 않음**.

### 증상
- Bridge의 ScriptProcessorNode는 정상 출력 (`filled 4096/4096, maxAmp=0.17`)
- 프론트엔드의 MediaRecorder는 chunks를 녹음 (`Processed 50 audio chunks`)
- 하지만 transcription에 시스템 오디오가 전혀 나타나지 않음

### 원인
WebKit에서 **서로 다른 AudioContext 간의 MediaStream 연결이 제대로 작동하지 않음**. Bridge의 AudioContext에서 생성한 `MediaStreamDestination.stream`의 오디오 트랙이, 프론트엔드의 AudioContext에서 `MediaStreamAudioSourceNode`로 읽힐 때 실제 오디오 데이터가 전달되지 않는 WebKit 고유의 제한.

### 해결: 공유 오디오 큐 (window.__nativeAudioQueue)
AudioContext 간 MediaStream 연결을 완전히 우회. 네이티브 오디오 데이터를 **전역 JavaScript 배열**로 공유하여, 프론트엔드의 AudioContext 내에서 직접 읽도록 변경.

#### Bridge JS (overlay)
```javascript
window.__nativeAudioQueue = audioQueue;
window.__nativeAudioCapturing = false;

window.__nativeAudioReceive = function(base64) {
    // base64 → Float32Array → audioQueue.push()
};
```
Bridge는 ScriptProcessorNode/MediaStreamDestination 없이, 큐에 데이터만 축적. getDisplayMedia는 더미 오디오 트랙이 있는 스트림을 반환 (프론트엔드가 "display capture active" 상태를 인식하도록).

#### Frontend (useAudioRecorder.ts)
```typescript
const nativeQueue = (window as any).__nativeAudioQueue;
if (nativeQueue && (window as any).__nativeAudioCapturing) {
    // 프론트엔드 AudioContext 내에서 ScriptProcessorNode 생성
    const nativeProcessor = audioCtx.createScriptProcessor(4096, 1, 1);
    nativeProcessor.onaudioprocess = (e) => {
        // nativeQueue에서 직접 읽어서 output 버퍼 채움
    };
    nativeProcessor.connect(destinationRef);  // 녹음 믹싱 노드에 연결
}
```

#### 최종 데이터 흐름
```
ScreenCaptureKit (Native)
  → Float32 PCM → base64
  → evaluateJavaScript("window.__nativeAudioReceive('...')")
  → JS: base64 decode → Float32Array → window.__nativeAudioQueue

Frontend AudioContext (Same context as mic):
  → ScriptProcessorNode reads from __nativeAudioQueue
  → Output → MediaStreamAudioDestinationNode (mixed with mic)
  → MediaRecorder → WebSocket → Transcription Server
```

**모든 오디오 처리가 하나의 AudioContext 안에서 이루어져** WebKit 호환성 문제 없음.

---

## 10. 앱 종료 및 Dock 아이콘 문제

### 문제 1: ⌘Q로 종료 불가
`LSUIElement = true` (Dock 아이콘 없음)로 설정하면 메인 메뉴가 없어서 ⌘Q 단축키가 작동하지 않음.

### 해결
- `LSUIElement = false`로 변경 (Dock에 아이콘 표시)
- `setupMainMenu()`에서 `NSMenu` 생성하여 ⌘Q 등록
- `applicationShouldTerminateAfterLastWindowClosed` → `true` 반환

### 문제 2: 윈도우 닫아도 프로세스 남음
창을 닫아도 앱 프로세스가 종료되지 않아 Activity Monitor에서 수동 종료 필요.

### 해결
`applicationShouldTerminateAfterLastWindowClosed(_:)` delegate 메서드에서 `true` 반환.

---

## 핵심 교훈 요약

| 영역 | 교훈 |
|------|------|
| WKWebView 투명도 | `alphaValue`만 사용. `backgroundColor = .clear`와 `drawsBackground = false`는 동시 사용 금지 |
| WKWebView 키 이벤트 | `NSWindow.performKeyEquivalent` override로 WKWebView보다 먼저 가로채기 |
| 글로벌 단축키 | `NSEvent.addGlobalMonitorForEvents`보다 Carbon `RegisterEventHotKey`가 안정적 |
| WebKit 프로퍼티 패치 | `Object.defineProperty`도 WebKit이 리셋함. **JavaScript Proxy**가 유일한 영구 해결책 |
| Cross-AudioContext | WebKit에서 다른 AudioContext의 MediaStream을 읽을 수 없음. **전역 배열 공유**로 우회 |
| ScriptProcessorNode | 입력 chunk 크기 ≠ 출력 버퍼 크기일 때, **여러 chunk를 합쳐서 버퍼를 완전히 채워야** 함 |
| ScreenCaptureKit | TCC 권한 필수. `excludesCurrentProcessAudio = true`로 자체 앱 오디오 제외 |
