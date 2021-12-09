import plotly.express as px
import pandas as pd
import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance import BinanceSocketManager
from dash import Dash, dcc, html, Input, Output
import os
app = Dash(__name__)
server = app.server
api_key = 'vpKHHlYxqsPU2VC7G7UP9QMNohCwZVudqZE8g1tfAfJBgMc8kOAUAoBnIQisd4UI'
api_secret = 'Z4fU3e46cXYPltbvGN2VgQkojBnoKwv20RfDDrsHxN9MUxlKWolEU1XRYOPXjbbD'
loop = asyncio.get_event_loop()
dataBTC = pd.read_csv('out.csv')
def convertTime(data):
    df = pd.DataFrame([data])
    df = df.loc[:,['E','p']]
    df.columns = ['Time','Price']
    df.Price =df.Price.astype(float)
    df.Time = pd.to_datetime(df.Time,unit ='ms')
    return df

def saveCSV(data):
    data.to_csv('out.csv', mode='a', index=False, header=False)

async def readCSV():
    symbol = 'BTCUSDT'
    client = await AsyncClient.create(api_key=api_key, api_secret=api_secret)
    bsm = BinanceSocketManager(client)
    socket = bsm.trade_socket(symbol)
    await socket.__aenter__()
    res = await socket.recv()
    dataBTC = convertTime(res)
    saveCSV(dataBTC)
    await client.close_connection()


    return pd.read_csv('out.csv')

app.layout = html.Div([

    html.H1("Auto Update BitCoin After 5 Minute", style={'text-align': 'center'}),
    dcc.Graph(id='bitcoin_map', figure={}),
    dcc.Interval(
            id='interval-component',
            interval=300*1000, # in milliseconds
            n_intervals=0
        )
])

@app.callback(
    Output(component_id='bitcoin_map',component_property='figure'),
    Input(component_id='interval-component', component_property='n_intervals')
)
def update_graph(n):
    dataBTC = loop.run_until_complete(readCSV())
    line_fig = px.line(dataBTC,x='Time',y='Price')
    return line_fig
if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
