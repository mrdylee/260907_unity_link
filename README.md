# ESS 컨테이너 — TypeScript 포터블 뷰어

사진을 참고해 Unity에서 만든 ESS 3D 목업을 Three.js로 옮긴 발표용 예제입니다.
실측 CAD, 전기 회로 시뮬레이터 또는 실제 장비 제어 프로그램이 아닙니다.

## 최신 개선본 (2026-09-17)

Blender v2의 도장·철물·고무 표면을 웹 뷰어에 반영했습니다. GLB에는 13개 PBR 재질과 8개 Normal/Metallic-Roughness 텍스처가 포함됩니다. 웹, Unity URP, Blender Cycles는 조명과 반사 계산이 달라 픽셀 단위로 동일하지 않습니다.

- 최신 Unity 씬: `UnityProject/Assets/ESS_Blender_v2/ESS_Blender_v2_Demo.unity`
- 재사용 프리팹: `UnityProject/Assets/ESS_Blender_v2/ESS_Blender_v2.prefab`
- Blender 원본: `Blender/ESS_Realistic_Materials_v2/ESS_Realistic_Materials_v2.blend`
- 웹 모델: `public/models/ess-container.glb`
- 재생성: Pillow가 설치된 Python으로 `python scripts/export-v2.py` 실행 후 `npm run build`

이 저장소의 TypeScript가 카메라와 문을 제어하며, 3D 형상·재질은 GLB 파일로 로드합니다. ZIP에도 최신 웹 모델과 실행 빌드를 포함했습니다. Unity의 기존 SampleScene은 보존되어 있습니다.

## ZIP 다운로드부터 실행까지

1. [ESS-TypeScript-Portable.zip 다운로드](https://github.com/mrdylee/260907_unity_link/raw/refs/heads/main/downloads/ESS-TypeScript-Portable.zip)를 누릅니다.
2. macOS는 ZIP을 더블클릭합니다. Windows는 ZIP을 우클릭해 **모두 압축 풀기**를 선택합니다.
3. 압축을 푼 **ess-portable** 폴더를 엽니다.
4. Node.js 22.18 이상이 설치돼 있는지 터미널에서 `node --version`으로 확인합니다. 없으면 [Node.js 공식 사이트](https://nodejs.org/)에서 설치합니다.
5. macOS는 `start.command`, Windows는 `start.cmd`를 실행합니다. 실행이 막히면 아래 터미널 방법을 사용합니다.
6. 브라우저 주소창에 **http://127.0.0.1:3000** 을 입력합니다. 검색창이 아닌 주소창에 입력하세요.
7. 터미널을 열어둔 상태로 사용합니다. 종료할 때 터미널에서 **Ctrl+C**를 누릅니다.

터미널 방법: `cd `를 입력한 뒤 **ess-portable** 폴더를 터미널로 드래그하고 Enter를 누르세요. 그다음:

```sh
node server.ts
```

발표용 실행에는 `npm install`이 필요 없습니다. 실행용 빌드와 모델이 ZIP 안에 포함돼 있습니다.
`index.html`을 직접 더블클릭하면 모델 로딩이 제한될 수 있으므로 위 서버 방식으로 실행하세요.
다른 컴퓨터에서는 ZIP과 Node.js가 필요하며, 위 주소는 실행 중인 그 컴퓨터에서 접속하는 주소입니다.

## 저장소 구성

- `src/`: 수정 가능한 TypeScript 문 제어와 발표용 화면 코드
- `server.ts`: 로컬 웹 서버
- `public/models/`: GLB 모델과 구성 정보
- `dist/`: 바로 실행할 수 있는 웹 빌드
- `downloads/`: 포터블 ZIP
- `UnityProject/`: 원본 Unity 프로젝트의 Assets, Packages, ProjectSettings
- `tests/`: 웹 모델의 문 동작·팩 수 검증 코드

Unity 원본은 Unity Hub에서 **Add / 디스크에서 프로젝트 추가**로 `UnityProject` 폴더를 선택하세요.
작업 버전은 Unity **6000.6.0f1**이며, 최신 장면은 `Assets/ESS_Blender_v2/ESS_Blender_v2_Demo.unity`입니다.
캐시와 사용자 설정은 포함하지 않았으므로 첫 실행 때 패키지 다운로드와 재임포트 시간이 필요합니다.
이전 상태는 `Assets/Scenes/Before_*.unity`에 백업했습니다.

## 바로 실행

**Node.js 22.18 이상**이 필요합니다. ZIP을 풀고 이 폴더에서:

```sh
node server.ts
```

브라우저에서 **http://127.0.0.1:3000** 을 엽니다.
이미 빌드된 `dist/`가 포함되어 있어, 보기만 할 때는 npm 설치나 인터넷 연결이 필요 없습니다.
macOS는 `start.command`, Windows는 `start.cmd`를 실행해도 됩니다.
종료는 터미널에서 Ctrl+C. 포트가 사용 중이면 `PORT` 환경변수로 변경하세요.
HTML 파일을 직접 더블클릭하지 말고 서버를 통해 접속하세요.

## 조작과 발표 순서

- 마우스 왼쪽 드래그: 회전 / 휠 또는 +·− 버튼: 확대·축소 / 우클릭 드래그: 이동
- 문 클릭: 해당 문 열기·닫기. 드래그 후에는 문 클릭으로 처리하지 않습니다.
- 전체 열기·닫기: 긴 면 도어 6개와 짧은 면 장비실 도어 2개를 함께 조작
- 전체 보기 → 배터리 랙 → 내부 패널 → eBSC 순으로 발표
- 전체화면: 오른쪽 버튼. 종료는 Esc
- 터치: 한 손가락 회전, 두 손가락 확대·이동

## 포함된 모델

- 랙 6개 × 세로 팩 7개 = 총 42팩
- 긴 면 도어 6개, 짧은 면 양문 2개와 독립 경첩
- 문 안쪽 FACP: 해당 문을 열면 함께 움직임
- 지붕 패널 2개, 칠러 그릴, HVAC
- 내부 E패널: 스위치 본체 및 확장 모듈 포트 27개, eBSC LAN 4개,
  LCS, 전원장치, 차단기, 단자대, 단순화한 배선

배선은 사진의 외형을 참고한 시각적 표현입니다. 실제 포트 연결을 시뮬레이션하지 않습니다.
사진에서 가려진 부분은 단순화했습니다. 단위는 미터이지만 치수는 실측값이 아닙니다.

## TypeScript 프로젝트에 가져오기

`public/models/ess-container.glb`와 `src/ESSModel.ts`를 복사하고 `three`를 설치하세요.
Three.js `GLTFLoader`를 이용한 단일 GLB라 Unity 런타임이나 WebGL 빌드가 필요 없습니다.

```ts
import { ESSModel } from './ESSModel';

const ess = await ESSModel.load('/models/ess-container.glb');
scene.add(ess.root);
ess.setAll(true);
ess.setDoor('Door_Hinge_01', false);

// 기존 렌더 루프에서 매 프레임 호출 (dt 단위: 초)
ess.update(dt);

// Three.js Raycaster로 선택한 첫 번째 오브젝트
ess.toggleObject(intersection.object);

// 화면 해제 시
// ess.dispose();
```

회전·확대 카메라는 `OrbitControls`이며 사용 예시는 `src/main.ts`에 있습니다.
GLB에는 형상·재질·텍스처·계층을 넣었고 문 애니메이션 동작은 `ESSModel.ts`가 담당합니다.
GLB만 다른 뷰어에 열면 문은 닫힌 정적 모델입니다.
Unity의 좌수 좌표계를 glTF 우수 좌표계로 변환했으므로 문 회전 부호는 Unity와 다릅니다.
`public/models/manifest.json`에 문 이름·열림각·모델 구성을 기록했습니다.

## 수정해서 빌드

```sh
npm ci
npm run dev
# 개발 화면 주소는 터미널에 표시됩니다.
npm run build
npm start
```

`src/`: TypeScript 뷰어와 문 제어 / `server.ts`: Node 기본 모듈만 사용하는 로컬 서버
`public/models/`: 원본 GLB / `dist/`: 즉시 실행할 웹 파일 / `tests/`: 동작 검증

다른 웹 서버에는 `dist/`를 배포하세요. 기본 빌드는 도메인 루트 경로를 기준으로 합니다.
다른 기기에서 접근하려면 호스트 설정과 네트워크 구성이 필요합니다.
현재 서버는 로컬 컴퓨터에서만 접근하도록 설정했습니다. 인터넷에 공개 배포된 상태는 아닙니다.

## 검증

TypeScript 검사와 배포 빌드 통과.
브라우저에서 모델 로딩, 전체 문 열림, 랙 보기, 내부 패널 보기 확인.
자동 검증에서 6랙·42팩, 문 열기·닫기, 개별 문 전환,
문과 FACP의 동반 이동 및 랙 고정을 확인했습니다.

서버 실행 후 개발 의존성을 설치한 환경에서:

```sh
node tests/verify.mjs
```

## 출처 및 라이선스

모델의 참고 사진은 사용자가 제공했습니다. 제3자 제품명·배치의 권리는 해당 권리자에게 있습니다.
Three.js는 MIT 라이선스이며 `THIRD_PARTY_LICENSES.txt`를 포함했습니다.
공식 로더 문서: https://threejs.org/docs/pages/GLTFLoader.html
