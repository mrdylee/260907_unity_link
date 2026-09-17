# ESS 도장 금속 외함 — 재질 개선 v2

이전 `../ESS_Surface_Study/ESS_Surface_Study.blend`를 보존하고 별도 버전으로 작업했습니다. 이번 Blender 편집·저장·렌더는 모두 MCP SDK → blender-mcp → 실행 중인 Blender 경로로 수행했습니다.

## 웹 조사와 사진 비교

- [LG 공식 JF2S DC LINK 소개 및 전시 사진](https://inside.lgensol.com/en/2025/11/lg-energy-solutions-ess-solutions-capturing-the-european-battery-market/): 밝은 외함과 어두운 배터리/장비 대비를 확인했습니다. LG LINK 제품군의 존재를 확인한 자료이며, 사용자가 제공한 JF3 eBSC 사진과 동일 제품이라는 근거는 아닙니다.
- [LG Energy Solution Vertech JF2 2HR AC LINK 자료](https://lgensol-vt.com/wp-content/uploads/2024/11/JF2-2HR-AC-LINK.pdf): 관련 LINK 제품군 확인에 사용했습니다. 외함 코팅 조성이나 정확한 도장 거칠기는 이 자료로 확인하지 못했습니다.
- [Rittal VX ESS 9690043 제조사 사양](https://www.rittal.com/com-en/products/PG20231215POW101/PG20240930STR301/PRO136611?variantId=9690043): 강판 외함의 문·지붕·후면에 질감 있는 분체도장을 사용한다고 명시합니다. 이는 다른 회사의 실내 IP20 외함 사례이며, LINK의 재질·색상·두께·등급 사양으로 전용하지 않았습니다. 미세 도장 질감의 일반적인 참고로만 사용했습니다.
- 사용자 사진 `IMG_7733 2.HEIC.png`: 밝은 회색 프레임, 루버, 어두운 실링과 제어 장비를 직접 비교했습니다. 촬영된 화면의 모아레는 표면 텍스처로 복사하지 않았습니다.
- 사용자 사진 `IMG_7728.HEIC.png`, `IMG_7146.HEIC.png`: CAD 외관과 제어반의 코팅/금속/플라스틱 반사 차이를 확인했습니다.

## 반영한 변화

도장면은 금속성 0으로 유지하면서 판넬을 따라 흐르는 반사와 미세 요철을 구현했습니다. 노출 하드웨어는 금속성 1, 고무 실링은 낮은 반사와 높은 거칠기로 구분했습니다. 기존 개별 부품의 크기 영향을 받던 텍스처 좌표를 공통 미터 좌표로 바꿔 미세 질감 크기를 일관되게 만들었습니다. 밝기를 낮추고 긴 조명 반사를 사용해 외함 면과 모서리를 읽기 쉽게 했습니다.

물리 재질 수치는 사진에 기반한 시각적 추정입니다. 강종·도장 방식·색상 코드·정확한 미세 요철 치수를 해당 LINK 제품의 확정 사양으로 주장하지 않습니다. 녹, 오염, 긁힘, 낡음은 추가하지 않았습니다. 모델의 부품 위치·크기·메시 구조는 유지했습니다.

## 결과

- `ESS_Realistic_Materials_v2.blend`: 편집 가능한 최종 재질과 카메라
- `01_exterior.png`: 전체 외관
- `02_material_closeup.png`: 도장면·실링·힌지 확대
- `validation.json`: 구조 보존 및 재질값 기록
- `mcp_result.json`: 실제 MCP 편집·렌더 호출 응답
