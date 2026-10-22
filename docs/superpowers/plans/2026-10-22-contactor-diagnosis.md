# Contactor Diagnosis Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline. No delegation required.

**Goal:** 기존 http://127.0.0.1:3006 링크에서 3D BPU 위치와 접촉기 진단 시연을 연결한다.

**Architecture:** `contactor.ts`에서 가상 신호/상태를 계산하고 `contactorDiagnostics.ts`에서 전용 패널을 표시한다. `main.ts`는 기존 선택 이벤트와 동일하게 카메라와 추가 강조선만 연결한다. 기존 telemetry/공유 모델 재질은 변경하지 않는다.

**Tech Stack:** TypeScript, Three.js, 기존 Vite 빌드, Node assert, 브라우저 검증.

1. `tests/contactor.test.ts`: 정상의 0.3초 전후, 불일치의 1.0초 경계, 통신 끊김 UNKNOWN을 단언한다. 구현 전 실패 확인 후 `src/contactor.ts`의 `simulateContactor(scenario, elapsedSeconds)`로 통과시킨다. `package.json`의 test에 연결한다.
2. `src/contactorDiagnostics.ts`: 전용 패널과 버튼, ESS/랙 선택 상태, 세 시나리오와 시간 이동, 설명용 단면, 근거와 대응 확인 항목을 표시한다. `contactorfocus`와 `contactorclose` 이벤트로 3D와 연결한다. 통신 끊김에서 내부 위치는 숨긴다.
3. `src/main.ts`: BPU 이름 `BPU_01`~`BPU_06`으로 위치를 찾고 Box3Helper와 라벨을 표시한다. 해당 양문을 열고 랙/BPU가 화면 왼쪽에 보이도록 카메라를 조정한다. 컨테이너 변경 시 대상을 다시 찾고 전체보기/다른 카메라/전체 정보 시 진단을 닫는다. `src/diagnostics.ts`에는 상호 배타적 패널 처리만 추가한다. `src/style.css`에 전용 패널과 반응형 배치를 추가한다.
4. `npm run build`, `ESS_TEST_URL=http://127.0.0.1:3006 npm test`. CUA에서 같은 링크를 새로고침하여 실제 3D·세 상태·시간·짝수 ESS 회전·랙 변경·닫기·기존 전체 정보·모바일 폭을 확인한다. 기존 수정은 보존하고 커밋/푸시하지 않는다.

## 2026-10-22 사용자 피드백 반영

최종 구현은 고정 패널을 말풍선으로 대체한다. `contactorPlaybackFrame`에서 0.6초 준비 구간을 추가하고 명령/피드백/판정 경계를 테스트했다. `contactorDiagnostics.ts`는 자동 재생, 정상 비교, 정지/재생, 시간 이동, UNKNOWN 시연을 제공한다. `main.ts`는 앵커 위치, 연결선, 부드러운 카메라 이동과 고장 강조를 연결한다. 현재 링크에서 정상/고장 및 320/390px 폭을 검증했으며, 시각적 비교와 최종 판단은 `design-qa.md`에 기록했다. 커밋·푸시·공개 배포는 하지 않는다.
