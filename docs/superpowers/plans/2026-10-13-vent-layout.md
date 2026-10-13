# 환기구 대각선 배치 Implementation Plan

> **For agentic workers:** REQUIRED EXECUTION SKILL: Use superpowers:executing-plans for continuous inline implementation. Steps use checkbox syntax.

**Goal:** 1·2·5·6번 문에 하나씩 대각선으로 배치하고 가운데 3·4번 문은 제외한다.

**Architecture:** 기존 덮개와 재질을 재사용한다. Blender 및 GLB 계층을 함께 수정하고 웹의 개수·짝 연결만 변경한다.

**Tech Stack:** Blender Python, GLB, TypeScript, Three.js.

- [x] `tests/verify.mjs`에서 네 덮개, 3·4번 문 덮개 없음, 번호별 부모, 홀수 하단·짝수 상단, 인접 양문 짝을 검증한다. 변경 전 모델에서 실패를 확인한다.
- [x] `scripts/vent-layout.py`로 네 기존 덮개를 재배치한다. 최신 Blender를 별도 저장하고 GLB의 BIN 재질 데이터는 그대로 유지한다.
- [x] `src/ESSModel.ts`의 덮개 번호를 1·2·5·6으로, 짝을 홀수 다음·짝수 이전으로 변경한다. `src/main.ts`의 상태 메시지를 맞춘다.
- [x] `npm run build && npm test`가 통과하는지 확인한다. 브라우저에서 가운데 문에 덮개가 없고 하단 버튼이 네 개를 여는지 확인한다.
- [x] 안내 문서의 배치 설명을 수정하고 실행 ZIP을 갱신한다.

이후 요청 범위만 커밋하고 기존 승인 범위에 따라 푸시한 뒤 성공 여부를 확인한다.
