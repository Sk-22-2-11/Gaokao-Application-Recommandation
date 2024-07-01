# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 11:24:50 2024
New zhiyuan zhengli liucheng
@author: derek
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from sqlalchemy import create_engine
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Constants
AZURE_STORAGE_CONNECTION_STRING = 'your_connection_string_here'
CONTAINER_NAME = 'your_container_name_here'
SQL_CONNECTION_STRING = 'your_sql_connection_string_here'

# Function to fetch webpage content
def fetch_webpage_content(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  # Ensure correct encoding
    return response.text

# Function to extract table data from HTML
def extract_table_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    headers = [header.get_text() for header in table.find_all('th')]
    rows = []
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cells = row.find_all('td')
        row_data = [cell.get_text().strip() for cell in cells]
        rows.append(row_data)
    if not headers:
        headers = ['Score Range', 'Number of Students', 'Cumulative Number']
    df = pd.DataFrame(rows, columns=headers)
    return df

# Function to save DataFrame to Excel
def save_to_excel(df, filename):
    df.to_excel(filename, index=False)
    print(f'Data has been saved to {filename}')

# Function to clean school names
def remove_suffix(school_name):
    return re.sub(r'[\(\[（【].*?[\)\]）】]', '', school_name)

# Function to merge school information
def merge_school_info(df_zhaosheng, df_yuanxiao_shuoming):
    df_zhaosheng['院校名称_无后缀'] = df_zhaosheng['院校名称'].apply(remove_suffix)
    df_filtered = df_zhaosheng[(df_zhaosheng['计划性质'] == '非定向') & (df_zhaosheng['批次名称'] == '本科批')]
    df_wuli = df_filtered[df_filtered['科类名称'].str.contains('物理')]
    df_lishi = df_filtered[df_filtered['科类名称'].str.contains('历史')]
    df_wuli['学费（学制）'] = df_wuli.apply(lambda row: f"{row['学费']}（{row['学制']}年）", axis=1)
    df_lishi['学费（学制）'] = df_lishi.apply(lambda row: f"{row['学费']}（{row['学制']}年）", axis=1)
    columns = ['院校代码', '院校名称', '专业代码', '专业名称', '简注', '次选科目', '计划数', '学费（学制）']
    df_wuli = df_wuli[columns + ['院校名称_无后缀']]
    df_lishi = df_lishi[columns + ['院校名称_无后缀']]
    df_wuli = df_wuli.merge(df_yuanxiao_shuoming[['院校名称', '省份', '城市', '学校水平']], left_on='院校名称_无后缀', right_on='院校名称', how='left')
    df_lishi = df_lishi.merge(df_yuanxiao_shuoming[['院校名称', '省份', '城市', '学校水平']], left_on='院校名称_无后缀', right_on='院校名称', how='left')
    df_wuli.drop(columns=['院校名称_无后缀', '院校名称_y'], inplace=True)
    df_lishi.drop(columns=['院校名称_无后缀', '院校名称_y'], inplace=True)
    df_wuli.rename(columns={'院校名称_x': '院校名称'}, inplace=True)
    df_lishi.rename(columns={'院校名称_x': '院校名称'}, inplace=True)
    return df_wuli, df_lishi

# Function to merge score information
def merge_score_info(plan_df, scores_df, rank_df):
    plan_df = plan_df.merge(scores_df[['院校名称', '专业名称', '投档分']], on=['院校名称', '专业名称'], how='left')
    plan_df = plan_df.merge(rank_df[['分数', '位次']], left_on='投档分', right_on='分数', how='left')
    plan_df.drop(columns=['分数'], inplace=True)
    return plan_df

# Function to upload file to Azure Blob Storage
def upload_to_azure(file_path, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print(f'{file_path} has been uploaded to {blob_name} in Azure Blob Storage')

# Function to save DataFrame to SQL
def save_to_sql(df, table_name):
    engine = create_engine(SQL_CONNECTION_STRING)
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f'Data has been saved to {table_name} in SQL database')

# Main function to orchestrate the entire process
def main():
    # Step 1: Fetch and parse the webpage content
    url = 'https://gaokao.eol.cn/he_bei/dongtai/202306/t20230625_2446944.shtml'
    html_content = fetch_webpage_content(url)
    df_scores = extract_table_data(html_content)
    save_to_excel(df_scores, 'gaokao_scores.xlsx')
    upload_to_azure('gaokao_scores.xlsx', 'gaokao_scores.xlsx')
    save_to_sql(df_scores, 'gaokao_scores')

    # Step 2: Process historical and physics data
    df_history = pd.read_excel('2023年河北历史本科院校招生计划.xlsx')
    df_physics = pd.read_excel('2023年河北物理本科院校招生计划.xlsx')
    df_combined = pd.concat([df_history, df_physics])

    required_columns = ['院校代码', '院校', '院校省份', '院校城市', '是否省会', '985', '211', '双一流']
    missing_columns = [col for col in required_columns if col not in df_combined.columns]
    if missing_columns:
        raise ValueError(f"缺少必要的列: {missing_columns}")

    df_unique = df_combined.drop_duplicates(subset=['院校'])
    result = pd.DataFrame()
    result['院校名称'] = df_unique['院校']
    result['省份'] = df_unique['院校省份']
    result['城市'] = df_unique.apply(lambda row: row['院校城市'] + '（省会）' if row['是否省会'] == '是' else row['院校城市'], axis=1)
    result['学校水平'] = df_unique.apply(lambda row: ','.join([level for level in ['985', '211', '双一流'] if row[level] == '是']), axis=1)
    result = result.drop_duplicates()
    save_to_excel(result, '2024_院校_说明表.xlsx')
    upload_to_azure('2024_院校_说明表.xlsx', '2024_院校_说明表.xlsx')
    save_to_sql(result, 'school_info')

    # Step 3: Merge school information and create final plans
    df_zhaosheng = pd.read_excel('2024_河北_招生计划.xlsx', dtype={'院校代码': str, '专业代码': str})
    df_yuanxiao_shuoming = pd.read_excel('2024_院校_说明表.xlsx')
    df_wuli, df_lishi = merge_school_info(df_zhaosheng, df_yuanxiao_shuoming)
    save_to_excel(df_wuli, '2024_物理_招生计划.xlsx')
    save_to_excel(df_lishi, '2024_历史_招生计划.xlsx')
    upload_to_azure('2024_物理_招生计划.xlsx', '2024_物理_招生计划.xlsx')
    upload_to_azure('2024_历史_招生计划.xlsx', '2024_历史_招生计划.xlsx')

    # Step 4: Add rank information and save final results
    physics_scores_df = pd.read_excel('2023_提档分数_物理.xlsx')
    history_scores_df = pd.read_excel('2023_提档分数_历史.xlsx')
    physics_rank_df = pd.read_excel('2023_一分一档_物理.xlsx')
    history_rank_df = pd.read_excel('2023_一分一档_历史.xlsx')

    df_wuli = merge_score_info(df_wuli, physics_scores_df, physics_rank_df)
    df_lishi = merge_score_info(df_lishi, history_scores_df, history_rank_df)
    save_to_excel(df_wuli, '2024_物理_招生计划_更新.xlsx')
    save_to_excel(df_lishi, '2024_历史_招生计划_更新.xlsx')
    upload_to_azure('2024_物理_招生计划_更新.xlsx', '2024_物理_招生计划_更新.xlsx')
    upload_to_azure('2024_历史_招生计划_更新.xlsx', '2024_历史_招生计划_更新.xlsx')
    save_to_sql(df_wuli, 'physics_plan')
    save_to_sql(df_lishi, 'history_plan')

if __name__ == "__main__":
    main()
