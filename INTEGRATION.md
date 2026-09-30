# 다른 시스템으로 이식하기: 인터페이스 우선 안내

## 핵심 연결 흐름

**컨테이너 선택 → 컨테이너 ID로 데이터 조회 → 오른쪽 패널과 말풍선 갱신**이 연결의 중심입니다.

현재 프로젝트는 TypeScript + Three.js 웹 앱입니다. 독립적인 npm SDK나 React 컴포넌트는 아닙니다. 현재 구현과 아래 권장 통합 계약을 구분해 사용하세요.

## 1. 가장 적은 수정으로 포함하기

`npm run build`로 생성한 `dist/` 전체를 대상 웹 서버의 한 경로에 배포합니다. `index.html`만 복사하면 안 됩니다. `assets/`와 `models/`를 함께 유지해야 합니다.

```html
<iframe src="/ess-viewer/" title="ESS 3D 모니터링"
        style="width:100%;height:800px;border:0"></iframe>
```

이 방식은 기존 전역 CSS와 DOM ID 충돌을 피합니다. **현재 iframe과 부모 시스템 사이의 메시지 API는 구현되어 있지 않습니다.** 부모에서 장비 선택이나 데이터를 전달하려면 별도 연결 코드가 필요합니다.

## 2. 소스 수준으로 이식할 파일

| 파일 | 역할과 변경 범위 |
|---|---|
| `src/ESSModel.ts` | GLB 로드, 복제, 문 개폐. 모델 이름과 계층을 유지하면 재사용 가능 |
| `public/models/ess-container.glb` | 실제 형상과 재질. 정적 URL로 제공 |
| `src/main.ts` | Three.js 장면, 카메라, 컨테이너 선택. 대상 앱의 초기화·해제 수명주기에 맞춰 변경 |
| `src/diagnostics.ts` | 오른쪽 패널과 말풍선. 데이터 공급자 교체 지점 |
| `src/telemetry.ts` | 데이터 타입 및 현재 모의 공급자 |
| `src/style.css` | 현재 전역 스타일. 직접 포함할 경우 뷰어 루트 아래로 범위를 제한 |

현재 코드는 `#app` 내용을 교체하고 `document` 전역 이벤트와 고정 DOM ID를 사용합니다. 같은 페이지에 여러 뷰어를 붙일 수 있는 구조는 아닙니다. React/Vue 등에서는 초기화 함수를 분리하고 해제 시 렌더 루프, 이벤트 리스너, ResizeObserver/MutationObserver, OrbitControls, WebGLRenderer를 정리해야 합니다. 현재 완성된 mount/unmount API는 없습니다.

## 3. 컨테이너와 장치 식별 규칙 — 가장 중요

- 표시·데이터용 컨테이너 ID: **1~6**. 화면 표기는 ESS 01~06.
- 현재 선택 메뉴 값과 `models` 인덱스: **0~5**. 공급자 호출 시 `+1` 변환.
- 랙 ID: 각 컨테이너 내부 **1~6**.
- 제어기 ID: `LCS`, `eBSC`.
- 실제 데이터의 키는 반드시 **컨테이너 ID + 장치 ID**로 구성합니다. RACK 01만으로 조회하면 서로 다른 컨테이너 데이터가 섞입니다.

현재 각 레코드에는 containerId 필드가 없고 조회 인자로 구분합니다. 외부 시스템에서는 응답에 containerId를 포함하여 요청 대상과 일치하는지 확인하는 방식을 권장합니다.

## 4. 현재 데이터 공급 인터페이스

```ts
interface TelemetryProvider {
  readonly source: 'simulation' | 'modbus';
  read(containerId?: number): Promise<RackTelemetry[]>;
}
```

현재 `SampleTelemetryProvider`는 `readEquipment(containerId = 1)`도 제공합니다. **readEquipment는 아직 TelemetryProvider 인터페이스에는 선언되어 있지 않고, diagnostics.ts가 구체 클래스에 직접 의존합니다.** 외부 공급자로 교체할 때 이 메서드를 인터페이스에 추가하고 공급자를 주입하도록 수정하세요.

랙 레코드의 필드는 다음과 같습니다.

| 필드 | 형식·단위 |
|---|---|
| rackId | number, 1~6 |
| temperatureC | number, °C |
| voltageV | number, V |
| currentA | number, A. 실제 연동 시 충전/방전 부호 규칙 합의 필요 |
| socPercent / sohPercent | number, 0~100 % |
| state | 현재 `'CHARGING' \| 'IDLE'` |
| status | 현재 `'normal' \| 'warning'` |
| diagnosticCode | 현재 `'NORMAL' \| 'OVER_TEMPERATURE'` |
| diagnosticMessage | string, 사용자 설명 |

제어기는 id, communication (`ONLINE`/`OFFLINE`), mode, diagnosticCode, diagnosticMessage를 사용합니다. LCS에는 선택적 dsState (`OPEN`/`CLOSED`)가 있고 화면은 CLOSED를 CLOSE로 표시합니다. 현재 제어기 diagnosticCode 타입은 NORMAL만 지원합니다. 실제 장비의 오류·방전·오프라인 등 상태를 지원하려면 타입과 렌더링을 함께 확장해야 합니다.

## 5. 선택 이벤트와 갱신 동작

3D 모델의 공개 메서드는 `ESSModel.load(url)`, `clone()`, `setDoor(name, open)`, `setAll(open)`, `toggleObject(object)`, `update(deltaSeconds)`, `dispose()`입니다. `setDoor`는 문 하나를 지정하고, `toggleObject`는 클릭된 랙 문과 짝을 함께 조작합니다. 애니메이션은 매 프레임 `update` 호출이 필요합니다. 복제 모델은 형상·재질을 공유하므로 한 복제본의 `dispose()`가 공유 자원까지 해제할 수 있습니다. 복제본별 제거와 공유 GPU 자원 최종 해제를 분리하는 작업은 이식 시 필요합니다.

| 현재 연결 지점 | 동작 |
|---|---|
| main.ts의 selectContainer(index) | 선택 메뉴, 카메라, 라벨, 패널 제목 변경. 모듈 내부 함수로 외부 export는 아님 |
| document의 `containerchange` | payload 없는 Event. diagnostics.ts가 선택 메뉴 값을 읽어 containerId를 계산 |
| document의 `rackfocus` | CustomEvent<number>, detail은 rackId. 현재 선택한 컨테이너 안에서 확대 |
| 공급자의 read/readEquipment | 선택 대상 데이터를 함께 읽고 카드와 말풍선 데이터 교체 |

컨테이너 변경 시 이전 말풍선을 닫고 오른쪽 패널을 엽니다. 선택 버전 번호를 비교해 늦게 도착한 이전 조회 결과가 최신 선택을 덮지 않도록 합니다. 현재 모의 공급자는 즉시 응답하며 실시간 구독·주기적 갱신은 없습니다.

## 6. 외부 시스템용 권장 계약 — 추가 구현 필요

DOM 메뉴를 외부 시스템이 직접 조작하지 않도록, 이식 시 아래 형태의 어댑터를 구현하는 것을 권장합니다. **아래 API는 설계 예시이며 현재 앱에 구현되어 있지 않습니다.**

```ts
interface ContainerSnapshot {
  containerId: number;
  sampledAt: string; // ISO timestamp; 실제 수집 시각
  source: 'simulation' | 'modbus';
  racks: RackTelemetry[];
  equipment: EquipmentTelemetry[];
}

interface ViewerAdapter {
  selectContainer(containerId: number): void; // 외부 계약은 1부터
  updateSnapshot(snapshot: ContainerSnapshot): void;
  destroy(): void;
}
```

읽기 모델과 렌더링을 분리하고, 외부에서 들어오는 ID·수치·상태를 검증한 후 표시합니다. 진단 설명은 현재 모의 데이터와 달리 외부 입력이므로 textContent 또는 이스케이프된 텍스트로 출력해야 합니다. iframe 메시지로 연결한다면 송신 origin과 메시지 스키마를 검증합니다.

## 7. 실제 Modbus TCP 연결

현재 앱에는 Modbus TCP 클라이언트나 WebSocket 서버가 없습니다. 실제 연동 시 권장 흐름은 다음과 같습니다.

`장비 → Modbus TCP 수집 서버 → HTTP/WebSocket → 데이터 공급자 → 뷰어`

브라우저 화면에서 일반 TCP 소켓으로 직접 Modbus 장비에 접속하는 방식은 사용하지 않습니다. 서버에서 장비별 IP, Unit ID, 레지스터 주소, 데이터형, 배율, 부호, 바이트 순서, 수집 주기를 매핑합니다. 화면에는 수집 시각과 연결 상태를 전달하며 미수신·오래된 값을 정상값이나 0으로 표시하지 않습니다. 현재 SIMULATION 문구는 실제 데이터 경로가 검증된 후에만 변경합니다.

문 열기 버튼은 **3D 애니메이션**입니다. LCS의 DS OPEN/CLOSE도 **표시용 상태**입니다. 실제 장비 명령 전송 인터페이스는 구현되어 있지 않습니다.

## 8. 이식 검증 기준

1. ESS 01과 ESS 02를 번갈아 선택했을 때 제목, 랙 값, 제어기 설명이 같은 containerId를 따릅니다.
2. 연속으로 선택해도 이전 응답이 새로운 선택을 덮지 않습니다.
3. 같은 컨테이너로 돌아오면 그 컨테이너의 데이터가 다시 표시됩니다.
4. 서버 오류·통신 끊김·오래된 데이터가 실제로 구분됩니다. 이 상태 처리는 실제 공급자 구현 시 추가해야 합니다.
5. 화면을 제거하고 다시 열어도 이벤트·렌더러가 중복되지 않습니다. 수명주기 해제 API 구현 시 검증합니다.
6. 대상 PC에서 6대 전체 보기와 1대 상세 보기의 프레임 시간·메모리를 측정합니다.

화면의 배치·색상·문 동작 기준은 [VIEWER_GUIDELINES.md](VIEWER_GUIDELINES.md)를 함께 참조하세요.
