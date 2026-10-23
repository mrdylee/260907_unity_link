# 여기부터 읽기 — ESS 웹 뷰어 AI 인계

이 문서는 다른 AI나 개발자가 대화 기록 없이 작업을 이어가기 위한 시작점입니다. 먼저 사용자의 새 요청을 확인하고, 아래 상태를 현재 파일과 대조하세요.

## 1. 읽는 순서

1. **이 문서**: 실행 방법, 현재 구현, 남은 일.
2. [VIEWER_GUIDELINES.md](VIEWER_GUIDELINES.md): 사용자가 확인한 화면 배치와 동작 기준.
3. [INTEGRATION.md](INTEGRATION.md): 컨테이너 ID, 데이터 공급자, 이벤트, 다른 시스템에 이식할 때의 제약.
4. [LINK 화면 재현 가이드](docs/LINK_RENDERING_GUIDE.md): C#·프런트엔드용 좌표, 좌우형, 배치 계산과 진단 앵커.
5. 요청과 관련된 `src/` 파일. 전체 Unity 프로젝트를 먼저 읽을 필요는 없습니다.

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

- E-panel 좌측형·우측형 컨테이너 6대, 1·2 / 3·4번의 2×2 묶음과 5·6번 별도 한 쌍으로 배치. L/R은 랙 앞문을 바라보는 기준이며 순서는 L/R/R/L/L/R. 각 컨테이너는 랙 6개·팩 42개·BPU 6개. 랙마다 검정색 팩 7개와 하단 BPU 1개.
- 랙 1–2, 3–4, 5–6은 각 쌍의 가운데 틈이 없도록 가로 폭을 늘려 맞붙임. 높이·깊이와 쌍의 바깥 경계는 유지.
- 4대 묶음은 등을 맞댄 두 줄로 랙 앞문이 바깥을 향하며, 좌우·앞뒤 외함 사이 빈 간격 모두 0.5ft(0.1524m). 3·4번 행을 Y축 180도 회전해 E-panel도 양쪽 바깥에 둠. 별도 2대 묶음까지의 4m 통로만 실측이 아닌 목업 임시값. 전체 보기에는 두 그룹 구분선·라벨과 E-panel L/R 표시.
- 우측형은 GLB의 X 반전과 별도 인쇄 map U 보정으로 생성한 목업. 실물 우측형 내부 배선·기기 배치까지 검증한 모델은 아님. 장비실 문은 100도 개방 시 뒤쪽 LINK 문과 겹치는 것을 재현해 목업 개방각을 90도로 제한함. [설계](docs/superpowers/specs/2026-10-23-left-right-link-design.md) 참고.
- 회전·좌우 반전한 컨테이너의 랙·패널·장치 상세 카메라도 같은 변환을 따르며 컨테이너별 선택 데이터는 유지.
- 전체 보기에서 컨테이너 본체·번호 라벨을 클릭하면 한 대를 확대하고 오른쪽 패널을 열어 해당 컨테이너 데이터로 변경.
- 하단 메뉴로도 컨테이너 선택 가능. 상세 보기에서는 나머지 다섯 대를 숨김.
- 랙 라벨·진단 카드 클릭은 랙 확대 + 해당 양문 열기 + 진단 말풍선 고정.
- 랙 문은 1–2, 3–4, 5–6번이 한 쌍. 서로 반대 방향으로 바깥쪽 개폐. FACP는 앞문을 따라 움직임.
- 이웃한 2–3번 및 4–5번 문은 문짝·경첩·손잡이·환기 덮개의 충돌 범위를 검사하고 접촉 직전에 정지. 두 문을 모두 열도록 요청하면 먼저 열린 문도 안전한 공통 각도로 물러나 두 문이 함께 열림. 상대 문을 닫으면 남은 문은 그 순간 각도를 유지하며, 다시 열기 요청을 해야 더 열림. 실제 질량·충격 해석은 아닌 시각화용 접촉 제약.
- 랙 문 회전축은 경첩 원통 중심으로 25mm 보정. 이웃 문 2/3·4/5의 테두리 돌출을 GLB에서 15mm 줄여 동시 개방을 약 59도에서 81도로 확대함. 손잡이를 포함한 접촉 제한은 유지하며 바깥 1·6번은 105도. Blender MCP 미연결로 이번 테두리 수정은 `.blend`에 반영하지 않았으며 재내보내기 후 `python3 scripts/recess-door-rims.py`를 적용해야 함. 노란 경고판 목업 6개는 제거함.
- 1–2번 및 5–6번 양문을 열었을 때 앞을 가리던 외함 기둥 두 개를 제거함. 안쪽 랙 프레임과 나머지 기둥은 유지.
- 환기 덮개는 1번 하단·2번 상단, 5번 하단·6번 상단의 네 개. 가운데 3·4번 문은 제외하며 덮개 클릭은 1–2 또는 5–6 쌍 개폐, 하단 버튼은 네 개 전체 개폐.
- 오른쪽 진단 패널과 반투명 개별 말풍선. SOC·SOH·온도·전류·전압·STATE·진단 표시.
- `Contactor 진단`은 BPU에 연결된 전용 말풍선에서 가상 이슈를 자동 재생함. 정상 비교·시간 이동·일시정지·통신 끊김을 지원하며 일반 진단과 겹치지 않음. 설명과 검증 범위는 [Contactor 진단 안내](docs/CONTACTOR_DIAGNOSTICS.md)를 참고.
- LCS DS 상태와 eBSC 통신 정보. eBSC는 LAN 포트 4개 장치이며 주변 스위치와 구분.
- LCS는 사용자 사진 기준의 얇은 검은 판형 본체, 위아래 녹색 단자대, 네 고정 나사, 하단 Ethernet과 전원선으로 구성. 오른쪽 흰 벽면에 밀착하며 사진의 임시 외부 배치는 재현하지 않음.
- LCS 위쪽 녹색 단자선은 중앙 패널 상단 덕트로, 아래쪽 단자선은 하단 덕트로 이어짐. 가는 빨강·검정 곡선을 번갈아 배치하며 실제 HW/RS-485 핀 배정은 미확인.
- 사진 기준 eBSC 글씨·LED 3개·USB형 단자 2개, 결합된 IE3500/확장 모듈의 인쇄·단자·방열판. 최신 케이블 배정은 VIEWER_GUIDELINES.md 마지막 절을 따름.
- IE3500 보라색 네트워크 케이블 6가닥은 포트와 상단 덕트 연결 위치를 유지한 연속 곡선. 커넥터 앞 짧은 직선 이후 부드럽게 휘어짐.
- eBSC의 흰 랜선 2가닥도 연속 곡선. 노란 커넥터와 LAN1→확장 모듈 2/9, LAN2→IE3500 1/7 연결을 유지함.
- 중앙 패널 사진을 참고한 모듈·단자대 사이 곡선 배선, 오른쪽 파란 케이블 묶음, 녹색·노란 접지 외관. 실제 회로 연결을 검증한 모델은 아님.
- 컨테이너별로 구분되는 **고정 모의 데이터**. 실제 장비 계측이나 실시간 갱신은 아님.
- 늦은 이전 데이터 응답이 최신 컨테이너 선택을 덮지 않도록 선택 버전 비교.

## 5. 파일 찾기

| 할 일 | 먼저 볼 파일 |
|---|---|
| 전체 배치 계산·간격 | `src/ContainerLayout.ts` |
| 카메라·클릭·그룹 표시 | `src/main.ts` |
| 오른쪽 패널·말풍선·선택 데이터 갱신 | `src/diagnostics.ts` |
| 데이터 타입·모의 값 | `src/telemetry.ts` |
| Contactor 진단 말풍선·재생 | `src/contactorDiagnostics.ts` |
| Contactor 가상 상태·시간 경계 | `src/contactor.ts`, `tests/contactor.test.ts` |
| 문 동작·모델 복제 | `src/ESSModel.ts` |
| 이웃한 랙 문 접촉 제한 | `src/DoorContact.ts` |
| 디자인·반응형 | `src/style.css` |
| 웹 3D 모델 | `public/models/ess-container.glb` |
| 최신 패널·환기구·eBSC·IE3500·랙 BPU·LCS Blender 원본 | `Blender/ESS_Clean_Doors/ESS_Clean_Doors.blend` |
| 이전 양문 Blender 원본 | `Blender/ESS_Paired_Doors/ESS_Paired_Doors.blend` |
| Blender 변환 스크립트 | `scripts/paired-doors.py` |
| Cisco 디테일·케이블 재배치 | `scripts/cisco-face.mjs`, `scripts/cisco-detail.py`, `scripts/cisco-network-routes.py` |
| 중앙 패널 배선 보강 | `scripts/center-wiring-detail.py` |
| 랙 하단 BPU·팩 검정색 외장 | `scripts/bpu-face.mjs`, `scripts/rack-bpu.py` |
| LCS 사진 외형·하단 LAN | `scripts/lcs-face.mjs`, `scripts/lcs-detail.py` |
| LCS 상하 신호선 → 중앙 패널 덕트 | `scripts/lcs-signal-wiring.py` |
| 보라색 네트워크 케이블 곡선 처리 | `scripts/purple-network-curves.py` |
| eBSC 흰 랜선 곡선 처리 | `scripts/ebsc-lan-curves.py` |
| 바깥쪽 랙 양문 앞 외함 기둥 제거 | `scripts/clear-rack-openings.py` |
| 랙 세 쌍 가로 확장·밀착 | `scripts/touch-rack-pairs.py` |
| 랙 문 회전축을 경첩 중심에 맞춤 | `scripts/align-door-hinges.py` |
| 문 위 노란 경고판 제거 | `scripts/remove-door-warning-plates.py` |
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
