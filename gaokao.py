# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 09:29:26 2021

@author: derek
"""
#databriks scripts for manual analyze
import pandas as pd
import matplotlib.pyplot as plt
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

################################################################
################      修改参数区域       #######################
################################################################

Student_name = '王程'  # 学生姓名
Student_group = '理'  # '文' 或者 '理'
Student_rank = 50000  # 同位分
Rank_high = 51000  # 向上冲刺-同位分
Rank_low = 49000  # 向下保底-同位分

AZURE_STORAGE_CONNECTION_STRING = 'your_connection_string_here'
CONTAINER_NAME = 'your_container_name_here'


################################################################
##########      运行代码区域（请勿改动）       ##################
################################################################


# Student_group
def rank_resrv(a):
    return Rank_low <= a <= Rank_high


if Student_group == '理':
    df = pd.read_excel("2023_pool_Wuli.xlsx", converters={u'院校代码': str, u'专业代码': str})
else:
    df = pd.read_excel("2023_pool_Lishi.xlsx", converters={u'院校代码': str, u'专业代码': str})

df['去年提档位次'] = pd.to_numeric(df['去年提档位次'], errors='coerce')

df = df.loc[df['去年提档位次'].apply(rank_resrv)]

df = df.sort_values(by=["专业名称", "去年提档位次"], ascending=True)

# Save to Excel
output_filename = f'志愿2023-{Student_group}-{Student_name}.xlsx'
writer = pd.ExcelWriter(output_filename)
df.to_excel(writer, 'Sheet1', index=False)
writer.close()

# Generate Data Visualizations
plt.figure(figsize=(10, 6))
df.groupby('专业名称')['去年提档位次'].mean().sort_values().plot(kind='bar')
plt.title('Average Rank by Major')
plt.ylabel('Average Rank')
plt.xlabel('Major')
visualization_filename = f'志愿2023-{Student_group}-{Student_name}.png'
plt.savefig(visualization_filename)
plt.close()

# Upload files to Azure Blob Storage
def upload_to_azure(file_path, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)

    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

upload_to_azure(output_filename, output_filename)
upload_to_azure(visualization_filename, visualization_filename)

print(f'Files {output_filename} and {visualization_filename} have been uploaded to Azure Blob Storage.')
