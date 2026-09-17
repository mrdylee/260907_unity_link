# Blender ESS v2 → Unity

완료 씬: `Assets/ESS_Blender_v2/ESS_Blender_v2_Demo.unity`
재사용 모델: `Assets/ESS_Blender_v2/ESS_Blender_v2.prefab`
화면: `unity_game_final.png` (실제 Unity Game View 2560×1440)

Blender MCP로 최종 v2 파일에서 1,260개 노드와 1,068개 평가된 메시를 내보냈습니다. 주요 네 재질(외함 도장, 프레임, 철물, 고무)의 절차적 표면을 1024px Normal 및 Metallic/Smoothness 텍스처 총 8장으로 베이크했습니다. Unity URP Lit로 13개 모델 재질을 구성했습니다. 마스크 R은 metallic, A는 1−roughness입니다. 베이크는 CPU 2스레드로 수행했습니다.

Cycles와 URP의 조명 및 반사 계산은 달라 픽셀 단위로 동일하지 않습니다. 주요 표면은 25cm 반복 타일로 근사했고, 나머지 재질은 기본 색과 PBR 상수로 변환했습니다.

## 확인 결과
- 실제 Play Mode: 측면문 6개 열림 각도 −105°, 전체 힌지 8개 닫힘 복귀 통과.
- 문 클릭 레이 검출 통과. FACP가 Front_Left_Hinge와 함께 이동함을 확인.
- Unity 콘솔 조회: 오류 0, 경고 0.
- 최종 씬 저장 완료, Play Mode 종료 확인.
- 원본 SampleScene SHA256 일치 및 Blender 원본과 베이크 전 복사본 바이트 일치 확인.

씬을 열고 Play를 누르면 문 클릭과 Open All / Close All을 사용할 수 있습니다. 프리팹을 다른 씬에 배치할 경우 ESSDoorController의 viewCamera에 해당 씬 카메라를 연결하세요.
