#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import KFold
import xgboost as xgb
import time
from sklearn.grid_search import GridSearchCV

'''
ID                          UniqueID
Estimated_Insects_Count     Estimated insects count per square meter
Crop_Type                   Category of Crop(0,1)
Soil_Type                   Category of Soil (0,1)
Pesticide_Use_Category      Type of pesticides uses (1- Never, 2-Previously Used, 3-Currently Using)
Number_Doses_Week           Number of doses per week
Number_Weeks_Used           Number of weeks used
Number_Weeks_Quit           Number of weeks quit
Season                      Season Category (1,2,3)
Crop_Damage                 Crop Damage Category (0=alive, 1=Damage due to other causes, 2=Damage due to Pesticides)
'''
train = pd.read_csv("data/train.csv")
train_y = train['Crop_Damage']
train_x = train.drop(['ID','Crop_Damage'], axis=1)
test  = pd.read_csv("data/test.csv")
test_uid = test['ID']
test_x  = test.drop(['ID'], axis=1)

print("Filled Missing Values")
train_x = train_x.fillna(value = -1)
test_x = test_x.fillna(value = -1)

xgb_train = xgb.DMatrix(train_x, label= train_y)
xgb_test  = xgb.DMatrix(test_x)

num_round = 2000
params = {
    'booster':'gbtree',
    'objective': 'multi:softmax',
    'num_class':3, # 类数，与 multisoftmax 并用
    'eval_metric': 'merror',
    'early_stopping_rounds': 120,
    'gamma':0.05, # 在树的叶子节点下一个分区的最小损失，越大算法模型越保守
    'lambda': 0.05,# L2 正则项权重
    'min_child_weight': 50, # 节点的最少特征数
    'subsample': 0.7, # 采样训练数据，设置为0.5，随机选择一般的数据实例 (0:1]
    'max_depth':6, # 构建树的深度
    'eta': 0.05,
    'seed': 88888,
    'colsample_bytree': 0.75, # 构建树树时的采样比率 (0:1]
    'scale_pos_weight':0.5,
}

watchlist = [(xgb_train, 'train')]

bst = xgb.train(params, xgb_train, num_boost_round=num_round, evals=watchlist)
#bst.save_model('./model/xgb.model') # 用于存储训练出的模型

pred = bst.predict(xgb_test, ntree_limit=bst.best_ntree_limit).astype('int')

result = pd.DataFrame({"ID":test_uid, "Crop_Damage":pred}, columns=['ID','Crop_Damage'])
result.to_csv('submission/xgb_MultiSoftmax.csv', index=False)
