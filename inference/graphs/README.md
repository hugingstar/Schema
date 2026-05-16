# Graph 생성 과정

flowchart LR
    %% 스타일 바인딩
    classDef pg fill:#E1F5FE,stroke:#0277BD,stroke-width:1.5px,color:#01579B;
    classDef sg fill:#E8F5E9,stroke:#2E7D32,stroke-width:1.5px,color:#1B5E20;
    classDef smg fill:#F3E5F5,stroke:#6A1B9A,stroke-width:1.5px,color:#4A148C;
    classDef ext fill:#ECEFF1,stroke:#37474F,stroke-width:1px,color:#263238;

    %% 외부 데이터 부하
    In([tokenizedPoints]) :::ext

    %% 1. POINT GRAPH (좌우 배치)
    subgraph PG [1. PointGraph 엔진]
        PG_1[그래프 객체 생성]
        PG_2[__addNodeToGraph<br>물리 계층 에지 연결]
        PG_3[leafNodes 추출<br>POINT 타입 마킹]
        
        PG_1 --> PG_2 --> PG_3
    end
    style PG fill:#F6FBFD,stroke:#0277BD,stroke-width:1px,stroke-dasharray: 5 5
    class PG_1,PG_2,PG_3 pg;

    %% 2. SIMILARITY GRAPH (좌우 배치)
    subgraph SG [2. SimilarityGraph 엔진]
        SG_1[findSimilarNodes<br>전수 스캔 기동]
        SG_2[__areNodesSimilar<br>자식 구조 유사도 계산]
        SG_3[ConceptNode 생성<br>& 기저 클러스터링]
        SG_4[__cleanUp<br>중복 구조 제거]

        SG_1 --> SG_2 --> SG_3 --> SG_4
    end
    style SG fill:#F9FDF9,stroke:#2E7D32,stroke-width:1px,stroke-dasharray: 5 5
    class SG_1,SG_2,SG_3,SG_4 sg;

    %% 3. SEMANTIC GRAPH (좌우 배치)
    subgraph SMG [3. SemanticGraph 엔진]
        SMG_1[inferSemanticGraph<br>부모 노드 역추적]
        SMG_2[ASSOCIATION 구축<br>기본 포함관계 맵핑]
        SMG_3[__handleDerivation<br>상속/확장 구조 분석]
        SMG_4[DERIVATION 전환<br>최종 지식 그래프 확정]
        
        SMG_1 --> SMG_2 --> SMG_3 --> SMG_4
    end
    style SMG fill:#FAF7FC,stroke:#6A1B9A,stroke-width:1px,stroke-dasharray: 5 5
    class SMG_1,SMG_2,SMG_3,SMG_4 smg;

    %% 데이터 최종 출력
    Out([semanticGraph.svg]) :::ext

    %% 파이프라인 메인 에지 연결
    In --> PG_1
    PG_3 --> SG_1
    SG_4 --> SMG_1
    SMG_4 --> Out