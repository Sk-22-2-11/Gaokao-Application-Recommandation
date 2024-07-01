# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 18:52:10 2024

@author: derek
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findSystemFonts
from sqlalchemy import create_engine
from azure.storage.blob import BlobServiceClient
import os

# Constants
AZURE_STORAGE_CONNECTION_STRING = 'your_connection_string_here'
CONTAINER_NAME = 'your_container_name_here'
SQL_CONNECTION_STRING = 'sqlite:///data.db'  # Change this to your actual SQL database connection string

# 获取宋体字体路径
def get_font_path(font_name):
    fonts = findSystemFonts(fontpaths=None, fontext='ttf')
    for font in fonts:
        if font_name in font:
            return font
    raise ValueError(f"未找到字体: {font_name}")

# 获取网页内容函数
def get_webpage_content(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  # 设置编码
    return response.text

# 提取表格数据函数
def extract_table_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')  # 根据实际HTML结构调整
    if table is None:
        raise ValueError("网页中未找到表格")
    
    data = []
    for row in table.find_all('tr')[2:]:  # 跳过表头
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append(cols)
    return data

# 创建DataFrame并处理数据类型
def create_dataframe(data):
    df = pd.DataFrame(data, columns=['分数档次', '物理(人数)', '物理(累计人数)', '历史(人数)', '历史(累计人数)'])
    df['分数档次'] = df['分数档次'].apply(lambda x: int(x.split('及以上')[0]) if '及以上' in x else int(x))
    df['物理(人数)'] = df['物理(人数)'].replace('', 0).fillna(0).astype(int)
    df['物理(累计人数)'] = df['物理(累计人数)'].replace('', 0).fillna(0).astype(int)
    df['历史(人数)'] = df['历史(人数)'].replace('', 0).fillna(0).astype(int)
    df['历史(累计人数)'] = df['历史(累计人数)'].replace('', 0).fillna(0).astype(int)
    return df

# 绘制每五分的人数统计分布图
def plot_distribution(df, subject, title, filename):
    # 筛选300分以上的数据
    df = df[df['分数档次'] >= 300]
    
    # 分组统计每五分的总人数
    df['分数段'] = (df['分数档次'] // 5) * 5
    grouped = df.groupby('分数段')[subject].sum().reset_index()
    
    # 自动获取宋体字体路径
    font_path = get_font_path('simsun')  # 'simsun' 是宋体的英文名
    font_prop = FontProperties(fname=font_path)

    # 绘图
    plt.figure(figsize=(16, 9))
    plt.gca().invert_xaxis()
    plt.bar(grouped['分数段'], grouped[subject], width=4.5, align='edge', color='lightgray')  # 设置柱状图颜色为浅灰色
    plt.xticks(grouped['分数段'], rotation=90, fontproperties=font_prop)
    plt.grid(axis='y')
    plt.title(title, fontproperties=font_prop)
    plt.savefig(filename)
    plt.close()

# 上传文件到Azure Blob Storage
def upload_to_azure(file_path, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)

    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

# 保存数据到SQL数据库
def save_to_sql(df, table_name):
    engine = create_engine(SQL_CONNECTION_STRING)
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)

# Main execution
url = "https://www.dxsbb.com/news/117915.html"
html_content = get_webpage_content(url)
data = extract_table_data(html_content)
df = create_dataframe(data)

# 保存数据到Excel
output_filename = '分数统计.xlsx'
df.to_excel(output_filename, index=False)

# 绘制物理和历史人数统计分布图
plot_distribution(df, '物理(人数)', '300分以上每五分的物理人数统计分布', '物理人数统计分布.png')
plot_distribution(df, '历史(人数)', '300分以上每五分的历史人数统计分布', '历史人数统计分布.png')

# 上传文件到Azure Blob Storage
upload_to_azure(output_filename, output_filename)
upload_to_azure('物理人数统计分布.png', '物理人数统计分布.png')
upload_to_azure('历史人数统计分布.png', '历史人数统计分布.png')

# 保存数据到SQL数据库
save_to_sql(df, 'score_distribution')

print(f'Files have been uploaded to Azure Blob Storage and data saved to SQL database.')
