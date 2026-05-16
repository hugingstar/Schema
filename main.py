# -*- coding: utf-8 -*-
import logging
import os
import sys
import pandas as pd

from inference.DataModel import DataModel
from inference.InferenceManager import InferenceManager


class AutoMapping:
    def __init__(self, MetaOrigin, save_path, limit):
        """
        MetaOrigin : 메타데이터 입력 경로 (CSV 파일)
        save_path  : 결과 저장 경로
        limit      : 점수 임계치 필터 필드
        """
        # Python 3 대응: 로거 컴포넌트 이름 정돈
        self.__logger = logging.getLogger(__name__)

        # Original Meta Data
        self.MetaOrigin = MetaOrigin

        # Save path for Mapped metadata
        self.save_path = save_path

        # limit
        self.limit = limit

        # 데이터 모델 및 인퍼런스 매니저 오케스트레이션 구동
        inference_mngr = InferenceManager(DataModel())  
        inference_mngr.loadDatasetFromFile(self.MetaOrigin)
        inference_mngr.tokenizeDataset()
        inference_mngr.cluster()
        
        # 주석 해제 필요 시 가동 가능하도록 매핑 인터페이스 유지
        # inference_mngr.classifyClusters()
        
        inference_mngr.labelDataset(limit=self.limit, unknown=0)

        # 결과 셋 인스턴스화 및 레이블 정제 함수 호출
        self.df_automapped, _ = inference_mngr.saveLabeledDataset(savePath=self.save_path)
        self.LabelCleansing()

    def LabelCleansing(self):
        # Python 3 대응: print문 괄호화
        print(type(self.df_automapped))
        
        # 현대 Pandas 대응 고속 배치 가공 기법: 
        # 최신 Pandas에서 완전 삭제된 df.append() 대신 리스트에 딕셔너리를 모은 뒤 한번에 DataFrame화 진행
        rows_accumulator = []
        
        for i in self.df_automapped.index:
            # Distance
            distList = self.df_automapped.loc[i, 'distance']
            if not distList or len(distList) == 0:
                continue
            num = distList.index(max(distList))

            # ClassName
            classNameList = self.df_automapped.loc[i, 'className']
            # Cluster
            clusterList = self.df_automapped.loc[i, 'clusterID']
            # Label
            labelList = self.df_automapped.loc[i, 'label']

            pDict = {
                'OriginalPoint': i,
                'Equipment': classNameList[num] if num < len(classNameList) else None,
                'Node': clusterList[num] if num < len(clusterList) else None,
                'Distance': distList[num],
                'Representation': labelList[num] if num < len(labelList) else None
            }
            rows_accumulator.append(pDict)
            
        # 단 한번의 호출로 DataFrame 적재 프로세스 완결 (속도 및 호환성 극대화)
        defignatedPoints = pd.DataFrame(
            rows_accumulator, 
            columns=['OriginalPoint', 'Equipment', 'Node', 'Distance', 'Representation']
        )
        
        print(defignatedPoints.shape)
        defignatedPoints.to_csv(os.path.join(self.save_path, "Automapping.csv"), index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    # 설정 경로 및 임계치 정보 지정
    MetaOriginPath = 'C:/Users/yslee/PycharmProjects/PnP/data/buildingData/raw/88.csv'
    save_path = 'C:/Users/yslee/PycharmProjects/PnP/output/'
    limit = 0.0
    
    # 오토매핑 클래스 인스턴스 실행 구동
    AutoMapping(MetaOrigin=MetaOriginPath,
                save_path=save_path,
                limit=limit)