# Left/right LINK Implementation Plan

> **For agentic workers:** REQUIRED EXECUTION SKILL: Use superpowers:executing-plans by default for continuous inline implementation. Use superpowers:subagent-driven-development only when the user explicitly requested subagents or parallel agent work. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 두 LINK 타입을 구분하고 바깥 방향 2×2 배치의 양 축 간격을 0.1524m로 맞춘다.

**Architecture:** `ESSModel.clone(panelSide)`가 좌우형과 인쇄 방향을 담당하고 `ContainerLayout.ts`가 회전·위치와 타입 순서를 정의한다. 기존 카메라 오프셋에 root scale을 반영한다.

**Tech Stack:** TypeScript, Three.js, 기존 Node GLB 검사, Vite, in-app browser.

---

### Task 1: 실제 모델 회귀 검사

**Files:** Modify `tests/verify.mjs`.

- [x] 01/02는 L/R, 03/04는 R/L, 05/06은 L/R로 복제하고 각 타입의 E-panel X 부호와 인쇄 map 반전을 검사한다. 좌측형 map과 지오메트리는 수정되지 않아야 한다.
- [x] `right.min.x-left.max.x === .1524`, `row0.min.z-row1.max.z === .1524`를 1e-6 오차로 검사한다. 각 행의 랙 앞문 방향은 01/02와 03/04에서 반대이고 묶음의 바깥을 향해야 한다.
- [x] `ESS_TEST_URL=http://127.0.0.1:3006 npm test`로 기존 코드가 새 조건에서 실패함을 확인한다.

### Task 2: 최소 구현

**Files:** Modify `src/ESSModel.ts`, `src/ContainerLayout.ts`, `src/main.ts`.

- [x] `clone(panelSide=this.panelSide)`에서 타입이 바뀌는 경우 root X scale과 인쇄 map U를 반전한다. map 재질은 복제하여 기존 타입에 영향을 주지 않는다.
- [x] 타입 순서 L/R/R/L/L/R, 행 회전 0/π/0, 좌우 간격 .1524m, 앞뒤 간격 .1524m, 별도 쌍까지 통로 4m를 적용한다.
- [x] 카메라 방향 오프셋을 scale 적용 후 quaternion 적용으로 변경한다. 전체 상태와 컨테이너 선택에 좌우형 정보를 표시한다. 100도 장비실 문 간섭을 재현한 결과에 따라 개방각은 90도로 제한한다.
- [x] `npm run build`, `ESS_TEST_URL=http://127.0.0.1:3006 npm test`가 통과하는지 확인한다. 문 개폐 중 실제 외곽 간 비관통 검사를 유지한다.

### Task 3: 안내·실행본·화면

**Files:** Modify `AI_START_HERE.md`, `VIEWER_GUIDELINES.md`, `README.md`, generated `dist/` and `downloads/ESS-TypeScript-Portable.zip`.

- [x] 이전의 단일 모델 짝수 회전 및 2m 줄 사이 통로 설명을 새 조건으로 갱신한다. 우측형 내부는 목업임을 명시한다. 기존 설계 문서는 새 문서로 대체되었다고 표시한다.
- [x] 로컬 페이지를 새로고침해 전체 배치, 두 타입 확대, 문 개폐와 Contactor 진단을 확인한다.
- [x] 포터블 ZIP의 기존 파일 목록을 유지하면서 현재 파일 내용으로 갱신한다. ZIP CRC와 포함 파일 일치를 검사하고 `git diff --check`를 확인한다.
