# Wider rack doors implementation plan

> **For agentic workers:** REQUIRED EXECUTION SKILL: Use superpowers:executing-plans for inline execution. No subagents requested.

**Goal:** RACK 2/3와 같은 구조의 4/5 문을 80도 이상 비관통 개방한다.

**Architecture:** GLB의 네 문 테두리 16개만 15mm 낮춘다. 기존 `DoorContact`의 메시 검사·공통 각도 계산은 그대로 사용한다.

**Tech Stack:** GLB JSON transforms, Python, Three.js, Node tests.

- [x] `tests/verify.mjs`의 동시·순차 개방 최소각을 80도로 높이고 `npm test`가 기존 GLB에서 실패하는지 확인한다.
- [x] `scripts/recess-door-rims.py`로 GLB JSON chunk의 해당 16개 translation Z만 보정한다. 이미 보정된 값은 다시 이동하지 않는다. 바이너리 chunk는 그대로 보존한다.
- [x] `npm run build`, `ESS_TEST_URL=http://127.0.0.1:3006 npm test`로 개방·닫힘·순서 전환·좌우형·배치 회귀를 확인한다.
- [x] 실제 페이지에서 RACK 2/3 개방을 확인하고 화면을 저장한다. 가이드의 약 59도를 약 81도로 갱신하고 Blender 원본과 GLB 보정의 차이를 명시한다.
- [x] ZIP을 현재 파일로 재생성하고 CRC/파일 일치 및 `git diff --check`를 확인한다.
