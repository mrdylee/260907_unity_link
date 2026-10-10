# 여기부터 읽기 — ESS 웹 뷰어 AI 인계

이 문서는 다른 AI나 개발자가 대화 기록 없이 작업을 이어가기 위한 시작점입니다. 먼저 사용자의 새 요청을 확인하고, 아래 상태를 현재 파일과 대조하세요.

## 1. 읽는 순서

1. **이 문서**: 실행 방법, 현재 구현, 남은 일.
2. [VIEWER_GUIDELINES.md](VIEWER_GUIDELINES.md): 사용자가 확인한 화면 배치와 동작 기준.
3. [INTEGRATION.md](INTEGRATION.md): 컨테이너 ID, 데이터 공급자, 이벤트, 다른 시스템에 이식할 때의 제약.
4. 요청과 관련된 `src/` 파일. 전체 Unity 프로젝트를 먼저 읽을 필요는 없습니다.

## 2. 프로젝트 받기

```sh
git clone https://github.com/mrdylee/260907_unity_link.git
cd 260907_unity_link
git status --short
```

이미 작업 폴더가 있다면 다시 복제하거나 기존 변경을 덮지 말고 현재 브랜치·차이부터 확인합니다. 저장소의 `main`은 배포용 소스와 빌드를 포함합니다. 포터블 ZIP만 받은 경우에는 `.git`이 없을 수 있습니다.

## 3. 실행과 검증

Node.js 22.18 이상이 필요합니다. 수정할 때:

```sh
npm ci
npm run build
```

첫 번째 터미널에서:

```sh
PORT=3006 npm start
```

브라우저에서 `http://127.0.0.1:3006/`를 열고, 별도 터미널에서:

```sh
ESS_TEST_URL=http://127.0.0.1:3006 npm test
```

위 환경 변수 문법은 macOS/Linux 셸 기준입니다. Windows PowerShell은 `$env:PORT='3006'; npm start`, 테스트 터미널은 `$env:ESS_TEST_URL='http://127.0.0.1:3006'; npm test`를 사용합니다.

`npm start`의 기본 포트는 3000이고, 모델 테스트의 기본 대상은 3006입니다. 서버와 테스트 주소를 반드시 맞추세요. 서버는 `dist/`를 제공하므로 소스를 고친 뒤에는 다시 빌드하고 브라우저를 새로고침해야 합니다. 다른 서버가 포트를 점유하면 종료하지 말고 빈 포트를 사용합니다.

실행만 할 때는 이미 포함된 `dist/`와 Node.js로 `npm start`를 사용할 수 있습니다. HTML을 파일로 직접 열지 마세요.

## 4. 현재 구현되어 있는 것

- 동일한 컨테이너 6대, 3열 × 2행 배치. 각 컨테이너는 랙 6개·팩 42개.
- 전체 보기에서 컨테이너 본체·번호 라벨을 클릭하면 한 대를 확대하고 오른쪽 패널을 열어 해당 컨테이너 데이터로 변경.
- 하단 메뉴로도 컨테이너 선택 가능. 상세 보기에서는 나머지 다섯 대를 숨김.
- 랙 라벨·진단 카드 클릭은 랙 확대 + 해당 양문 열기 + 진단 말풍선 고정.
- 랙 문은 1–2, 3–4, 5–6번이 한 쌍. 서로 반대 방향으로 바깥쪽 개폐. FACP는 앞문을 따라 움직임.
- 오른쪽 진단 패널과 반투명 개별 말풍선. SOC·SOH·온도·전류·전압·STATE·진단 표시.
- LCS DS 상태와 eBSC 통신 정보. eBSC는 LAN 포트 4개 장치이며 주변 스위치와 구분.
- 컨테이너별로 구분되는 **고정 모의 데이터**. 실제 장비 계측이나 실시간 갱신은 아님.
- 늦은 이전 데이터 응답이 최신 컨테이너 선택을 덮지 않도록 선택 버전 비교.

## 5. 파일 찾기

| 할 일 | 먼저 볼 파일 |
|---|---|
| 배치·카메라·클릭 | `src/main.ts` |
| 오른쪽 패널·말풍선·선택 데이터 갱신 | `src/diagnostics.ts` |
| 데이터 타입·모의 값 | `src/telemetry.ts` |
| 문 동작·모델 복제 | `src/ESSModel.ts` |
| 디자인·반응형 | `src/style.css` |
| 웹 3D 모델 | `public/models/ess-container.glb` |
| 최신 패널 배치 Blender 원본 | `Blender/ESS_Vent_Doors/ESS_Vent_Doors.blend` |
| 이전 양문 Blender 원본 | `Blender/ESS_Paired_Doors/ESS_Paired_Doors.blend` |
| Blender 변환 스크립트 | `scripts/paired-doors.py` |
| 검증 | `tests/telemetry.test.ts`, `tests/verify.mjs` |

`dist/`는 생성물입니다. 여기를 직접 고치지 말고 소스를 수정한 후 빌드합니다. Unity 씬은 별도 산출물로, 웹 변경이 자동 반영되지 않습니다.

## 6. 아직 구현되지 않았거나 해결되지 않은 것

- 실제 Modbus TCP 서버, WebSocket 공급자, 통신 오류·오래된 데이터 처리.
- 공개된 mount/unmount 또는 iframe 메시지 API. INTEGRATION.md의 ViewerAdapter는 권장 설계이며 구현된 API가 아닙니다.
- 약 5년 전 사무용 PC에서의 성능 검증. 전체 보기용 LOD와 변경 시에만 렌더링하는 방식도 미구현입니다.
- 환풍구 반짝임은 원인 미확정·미해결입니다. 사용자가 이 문제를 보류했으므로 새 요청 없이 임의로 재개하지 마세요.

위 항목들은 상태 설명이며 자동으로 수행할 작업 목록이 아닙니다.

## 7. 반드시 유지할 구분

- 외부 데이터 컨테이너 ID는 1~6, 내부 배열·선택 메뉴 값은 0~5입니다.
- 장치 키는 컨테이너 ID와 랙/제어기 ID를 함께 사용합니다.
- 3D 문 애니메이션은 실제 장비 제어 명령이 아닙니다.
- 모의 데이터의 경고 기준과 숫자를 실제 장비 사양으로 취급하지 않습니다.
- 복제 모델은 형상·재질을 공유하므로 자원 해제에 주의합니다. 자세한 내용은 INTEGRATION.md를 확인합니다.

## 8. 작업 완료 확인

1. `git diff`로 요청에 관련된 변경만 있는지 확인합니다. 무관한 미추적 파일은 추가하지 않습니다.
2. `npm run build`와 변경에 해당하는 테스트를 실행합니다.
3. UI 변경이면 실행 화면에서 실제 클릭·전환을 확인합니다. 도구 실행 성공만으로 화면 완료를 보고하지 않습니다.
4. 배포 요청이 있으면 `dist/`와 `downloads/ESS-TypeScript-Portable.zip`을 최신화합니다. ZIP에는 src/public/dist/tests, 실행 파일, package 파일, README 및 세 안내 MD를 포함합니다.
5. 푸시 성공을 확인한 뒤에만 GitHub 반영 완료라고 말합니다. 로컬 완료와 업로드 완료를 구분합니다.

## 다른 AI에게 전달할 짧은 요청

> 이 저장소의 AGENTS.md와 AI_START_HERE.md부터 읽고 현재 소스 상태를 확인해 주세요. VIEWER_GUIDELINES.md의 화면 기준과 INTEGRATION.md의 인터페이스를 유지하며, 제가 요청한 변경만 구현하고 빌드·테스트·화면 검증 후 결과를 알려주세요.
