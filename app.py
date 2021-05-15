# -*- coding: utf-8 -*-

# 특정 섹터 내 종목 정보를 찾아오는 함수
# 기준 일자를 입력하고, 섹터, TICKER 정보를 클릭하여 데이터를 불러옵니다.
# 기준 일자를 입력합니다. (1차)
# 섹터에 속한 TICKER 리스트가 보여집니다. (2차)
# 섹터별 TICKER 데이터를 호출 후 datatable로 보여집니다. (3차)

import dash  # Dash 1.16 or higher
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from datetime import date
import datetime
import pandas_datareader.data as web
import dash_bootstrap_components as dbc
import dash_table

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# TICKER를 입력합니다.
TICKER = ['INTC','NVDA','QCOM','GOOGL','FB']

start = date(2016, 1, 1)
end = datetime.datetime.now()

# 수익률, 거래량 데이터를 산출합니다.
dfs = web.DataReader(TICKER[0], 'yahoo', start, end)
dfs.reset_index(inplace=True)
dfs.set_index("Date", inplace=True)
dfs['Return'] = (dfs['Close'] / dfs['Close'].shift(1)) - 1
dfs['Return(cum)'] = (1 + dfs['Return']).cumprod()
dfs = dfs.dropna()
dfs.loc[:,'TICKER'] = TICKER[0]
df = dfs

for i in range(1,len(TICKER)):
    start = date(2016, 1, 1)
    end = datetime.datetime.now()
    dfs = web.DataReader(TICKER[i], 'yahoo', start, end)
    dfs.reset_index(inplace=True)
    dfs.set_index("Date", inplace=True)
    dfs['Return'] = (dfs['Close'] / dfs['Close'].shift(1)) - 1
    dfs['Return(cum)'] = (1 + dfs['Return']).cumprod()
    dfs = dfs.dropna()
    dfs.loc[:,'TICKER'] = TICKER[i]
    df = df.append(dfs)

df_A = df[(df['TICKER'] == 'INTC')|(df['TICKER'] == 'NVDA')|(df['TICKER'] == 'QCOM')]
df_B = df[(df['TICKER'] == 'GOOGL')|(df['TICKER'] == 'FB')]
df_A.insert(9,'Sector','Telecom_Service')
df_B.insert(9,'Sector','IT')

dff = pd.concat([df_A, df_B])

# 데이터타입(Date)변환 문제로 csv 저장 후, 다시 불러옵니다. (파일 경로 설정 필요!!)
dff = dff.reset_index().rename(columns={"index": "id"})
dff.to_csv('pricevolume.csv', index=False, encoding='cp949')
dff = pd.read_csv('C:/Users/ysj/PycharmProjects/group_datatable/pricevolume.csv')
dff.iloc[:, 1:9] = round(dff.iloc[:, 1:9], 2)
df = dff[dff['Date'] == '2020-05-13']

app.layout = html.Div([
    html.H3("Get the 'TICKER' data"),
    html.Br(),
    html.H4(" * Date 입력"),
    dcc.DatePickerSingle(
        id='date-picker',
        date='2021-05-13',
        display_format='YYYY-MM-DD',
    ),
    html.Br(),
    html.H4(" * Sector, TICKER 입력"),
    dcc.Dropdown(
        id='dropdown-sector',
        options=[{'label': s, 'value': s} for s in ['Telecom_Service', 'IT']],
        value='Telecom_Service',
        clearable=False),
    dbc.Checklist(
        id='checklist-ticker',
        options=[],
        labelStyle={'display': 'inline-block'},
        inline=True
       ),
    html.H4(" * TICKER 데이터"),
    dash_table.DataTable(
        id='datatable',
        data=df.to_dict('records'),
        columns=[
            {
                "name": i,
                "id": i,
                "deletable": True,
                "selectable": True,
                "hideable": True,
            }
            if i == "High" or i == "Low" or i == "Open" or i == "Adj Close"
            else {"name": i, "id": i, "deletable": True, "selectable": True}
            for i in df.columns
        ],
        page_size=50,
        sort_action="native",
        column_selectable="multi",
        row_deletable=True,
        style_as_list_view=True
    )
 ])


@app.callback(
    Output('checklist-ticker', 'options'),
    [Input('dropdown-sector', 'value')]
)
def set_available_options(sector):
    dfs = df[df['Sector'] == sector]
    dfs = dfs.reset_index(drop=True)
    return [{'label': c, 'value': c} for c in sorted(dfs.TICKER.unique())]
@app.callback(
    Output('checklist-ticker', 'value'),
    Input('checklist-ticker', 'options')
)
def define_value(available_options):
    return [x['value'] for x in available_options]

@app.callback(
    Output('datatable', 'data'),
    [Input('dropdown-sector', 'value'),
     Input('checklist-ticker', 'value')]
)
def update_data(sector,TICKERs):
    dfs = df[df['Sector'] == sector]
    dfs = dfs.reset_index(drop=True)
    if len(TICKERs) == 0:
        return dash.no_update
    else:
        mask = dfs.TICKER.isin(TICKERs)
        data = dfs[mask].to_dict("records")
        return data

if __name__ == "__main__":
    app.run_server(debug=True)