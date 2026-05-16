# Database schema inference

1. **컨텍스트 초기화 및 데이터 로드 (`loadDatasetFromFile`)**
   * 입력된 CSV 원본 메타데이터 경로를 인자로 받아 글로벌 컨텍스트 메모리 공간인 `DataModel`을 깨우고, 문자열 포인트 목록을 1차 적재합니다.
2. **텍스트 정제 및 조각화 단계 (`tokenizeDataset`)**
   * 카멜 표기법 해제(`__unCamel`) 기능이 포함된 `SimpleTokenizer`가 실행되어 포인트 이름의 오타 및 특수문자 노이즈를 정제하고, 공백 단위로 쪼개어 정형화된 토큰 셋(`PointTokens`)을 만듭니다.

3. **3대 방향성 계층 그래프 연쇄 구축 (`cluster`)**
   * **PointGraph**: 잘린 단어 조각들을 차례대로 이어 나가는 거대한 트리 형태의 폴더 디렉토리 계층 그래프(`DiGraph`)를 만듭니다.
   * **SimilarityGraph**: 노드별 자식 일치도를 수학적으로 대조하여, 닮은꼴 장비 인스턴스(예: AHU01, AHU02)를 묶는 가상의 `ConceptNode`를 도출하고 기초 도메인 명칭을 지정합니다.
   * **SemanticGraph**: 장비 모델 간의 포함 관계와 상속(Derivation) 구조를 최종 추론하여 의미론적 전체 데이터 관계 지도를 형성합니다.

4. **다차원 탐색 및 후보군 점수 스코어링 (`labelDataset`)**
   * 생성된 그래프 인프라를 바탕으로 바닥(리프 노드)에서부터 역추적하여 전수 조사를 전개합니다.
   * 각 포인트 조각이 우리가 들고 있는 **표준 카탈로그 사전(`EquipmentModels`/`PointModels`)**과 비교하여 획득한 유사도 매칭 스코어가 사용자 설정 임계치(`limit`) 조건에 맞을 경우 `labeledDataset`에 매핑 후보군으로 등록합니다.

5. **공통 분모 딕셔너리 테이블 출력 (`saveLabeledDataset`)**
   * Pandas 프레임워크를 기반으로 포인트별 다중 분류 후보 명세 데이터 테이블을 `AutomapCandidate.csv` 형태의 중간 텍스트 가공물 파일로 일차 저장합니다.

6. **데이터 클렌징 및 최적 매칭 정제 (`LabelCleansing`)**
   * 다중 매핑 후보군 중 수학적 연산 점수(`distance`)가 가장 높게 나타난 **글로벌 최적의 1:1 매칭 쌍**을 추려내기 위해 탐욕적 알고리즘(Greedy Logic) 정제를 전개합니다.
   * 포인트명이 극도로 중복되거나 노이즈가 심해 분류할 수 없었던 항목을 배제 처리합니다.

7. **최종 마스터 매핑 명세서 생성 (`Automapping.csv`)**
   * 정제가 완결된 포인트 식별 매핑 데이터를 최종 산출물인 `Automapping.csv` 마스터 테이블 파일로 디스크에 내보내며 파이프라인 프로세스를 자동 완결합니다.
---

### 📝 Schema inference process

```mermaid
flowchart LR
    %% 1단계: 입력 및 초기화
    subgraph STAGE1 [1. 입력 및 초기화]
        direction TD
        A["원본 메타데이터 CSV<br>(88.csv / R5points.csv)"] -->|1. 파일 입력| B("AutoMapping 클래스 호출")
        B -->|2. 컨텍스트 초기화| C["InferenceManager<br>/ DataModel"]
        C -->|3. 파일 스트림 파싱| D["Dataset<br>.loadDatasetFromFile"]
    end

    %% 2단계: 토큰화 및 그래프 구축
    subgraph STAGE2 [2. 토큰화 및 그래프 분석]
        direction TD
        E["SimpleTokenizer"] -->|CamelCase 변환<br>/ 특수문자 제거| F["PointTokens 생성 및 정렬"]
        F -->|5. 그래프 엔진 가동| G["PointGraph<br>(토큰 폴더 계층 트리 구축)"]
        G -->|하위 노드 구조 대조| H["SimilarityGraph<br>(클러스터링 & Concept 생성)"]
        H -->|장비 명명 및 관계 조율| I["SemanticGraph<br>(상속/포함 관계 최종 추론)"]
    end

    %% 3단계: 스코어링 및 매칭
    subgraph STAGE3 [3. ML 스코어링 및 분류]
        direction TD
        J["InferenceManager<br>.labelDataset"] -->|7. 피처 스코어링 대조| K["Features / PointClassifier<br>(Jaro-Winkler 거리 채점)"]
        K -->|임계치 limit 이상 필터링| L["labeledDataset 캐시 적재"]
        L -->|8. 중간 가공물 출력| M["saveLabeledDataset<br>(AutomapCandidate.csv)"]
    end

    %% 4단계: 정제 및 최종 출력
    subgraph STAGE4 [4. 데이터 정제 및 출력]
        direction TD
        N["AutoMapping<br>.LabelCleansing"] -->|최고 유사도 1:1<br>탐욕적 매칭| O["Pandas 데이터 프레임<br>배치 빌드"]
        O -->|10. 마스터 리포트 출력| P["Automapping.csv<br>최종 저장 완료"]
    end

    %% 서브그래프 간 연결 관계
    D -->|4. 원시 문자열 전달| E
    I -->|6. 그래프 전수 조사| J
    M -->|9. 데이터 정제 엔진 가동| N

    %% 스타일 포맷팅
    style A fill:#ECEFF1,stroke:#37474F,stroke-width:1px
    style B fill:#E8F5E9,stroke:#2E7D32,stroke-width:1px
    style C fill:#E8F5E9,stroke:#2E7D32,stroke-width:1px
    style F fill:#FFF3E0,stroke:#EF6C00,stroke-width:1px
    style G fill:#E1F5FE,stroke:#0277BD,stroke-width:1px
    style H fill:#E1F5FE,stroke:#0277BD,stroke-width:1px
    style I fill:#E1F5FE,stroke:#0277BD,stroke-width:1px
    style K fill:#F3E5F5,stroke:#6A1B9A,stroke-width:1px
    style P fill:#FFEBEE,stroke:#C62828,stroke-width:2px

    %% 서브그래프 스타일 (선택 사항: 시각적 구분을 원치 않으시면 제거 가능)
    style STAGE1 fill:#FAFAFA,stroke:#B0BEC5,stroke-dasharray: 5 5
    style STAGE2 fill:#FAFAFA,stroke:#B0BEC5,stroke-dasharray: 5 5
    style STAGE3 fill:#FAFAFA,stroke:#B0BEC5,stroke-dasharray: 5 5
    style STAGE4 fill:#FAFAFA,stroke:#B0BEC5,stroke-dasharray: 5 5
