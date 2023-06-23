# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 09:29:26 2021

@author: derek
"""

import pandas as pd


################################################################
################      修改参数区域       #######################
################################################################

Student_name  = '王程' # 学生姓名
Student_group = '理'     # '文' 或者 '理'
Student_rank  =  50000     # 同位分 
Rank_high     =  51000	 # 向上冲刺-同位分
Rank_low      =  49000	 # 向下保底-同位分





################################################################
##########      运行代码区域（请勿改动）       ##################
################################################################



#Student_group
def rank_resrv(a):
    return a >= Rank_low and a <= Rank_high

if Student_group == '理':
    df = pd.read_excel("2023_pool_Wuli.xlsx", converters = {u'院校代码':str,u'专业代码':str})
else:
    df = pd.read_excel("2023_pool_Lishi.xlsx", converters = {u'院校代码':str,u'专业代码':str})

df['去年提档位次']= pd.to_numeric(df['去年提档位次'],errors='coerce')


df = df.loc[df['去年提档位次'].apply(rank_resrv)]

df = df.sort_values(by=["专业名称","去年提档位次"],ascending=True)

writer = pd.ExcelWriter( '志愿2023-'+ Student_group + '-' + Student_name + '.xlsx') 

df.to_excel(writer, 'Sheet1', index = False) 

writer.close()





