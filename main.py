# TICKER별 가격, 거래량 가져오는 함수입니다.
# 수익률, 누적 수익률 산출합니다.

import datetime
import pandas_datareader.data as web
import pandas as pd
import plotly.express as px
from datetime import date


def get_data(start, end):
    TICKER = ['INTC', 'NVDA', 'QCOM', 'GOOGL', 'FB']
    # start = date(2016, 1, 1)
    # end = datetime.datetime.now()
    # 수익률, 거래량 데이터를 산출합니다.
    dfs = web.DataReader(TICKER[0], 'yahoo', start, end)
    dfs.reset_index(inplace=True)
    dfs.set_index("Date", inplace=True)
    dfs['Return'] = (dfs['Close'] / dfs['Close'].shift(1)) - 1
    dfs['Return(cum)'] = (1 + dfs['Return']).cumprod()
    dfs = dfs.dropna()
    dfs.loc[:, 'TICKER'] = TICKER[0]
    df = dfs

    for i in range(1, len(TICKER)):
        dfs = web.DataReader(TICKER[i], 'yahoo', start, end)
        dfs.reset_index(inplace=True)
        dfs.set_index("Date", inplace=True)
        dfs['Return'] = (dfs['Close'] / dfs['Close'].shift(1)) - 1
        dfs['Return(cum)'] = (1 + dfs['Return']).cumprod()
        dfs = dfs.dropna()
        dfs.loc[:, 'TICKER'] = TICKER[i]
        df = df.append(dfs)

    df_A = df[(df['TICKER'] == 'INTC') | (df['TICKER'] == 'NVDA') | (df['TICKER'] == 'QCOM')]
    df_B = df[(df['TICKER'] == 'GOOGL') | (df['TICKER'] == 'FB')]
    df_A.insert(9, 'Sector', 'Telecom_Service')
    df_B.insert(9, 'Sector', 'IT')

    dff = pd.concat([df_A, df_B])

    # 데이터타입(Date)변환 문제로 csv 저장 후, 다시 불러옵니다. (파일 경로 설정 필요!!)
    dff = dff.reset_index().rename(columns={"index": "id"})
    dff.to_csv('pricevolume.csv', index=False, encoding='cp949')
    dff = pd.read_csv('C:/Users/ysj/PycharmProjects/group_datatable/pricevolume.csv')
    dff.iloc[:, 1:9] = round(dff.iloc[:, 1:9], 2)
    data = dff
    return data

