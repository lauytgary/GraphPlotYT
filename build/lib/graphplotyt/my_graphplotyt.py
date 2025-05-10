import os
import sys

import pandas as pd
import plotly.graph_objects as go  # use plotly version 5.24.1
from plotly.subplots import make_subplots
import random


def random_color():
    # ensure dark color for rgb average <=128
    while True:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        avg = (r+g+b)/3
        if avg <= 128:
            return f'rgb({r}, {g}, {b})'



def graphplot(stock_name, file_name_list, num_of_lines=100):
    if not file_name_list:
        print('file_name_list empty')
        return

    if num_of_lines <= len(file_name_list) / 2:
        first_n_file_name_list = file_name_list[:num_of_lines]
        last_n_file_name_list = file_name_list[-1 * num_of_lines:]
        file_name_list = first_n_file_name_list + last_n_file_name_list

    # Initialization
    df_list = []

    for file_name in file_name_list:
        file_path = os.path.join('backtest_output', file_name + '.csv')
        df = pd.read_csv(file_path)

        # find overall pct change compared to starting date
        df['cum_pct_change'] = (df['close'] - df['close'].iloc[0]) / df['close'].iloc[0]
        df_list.append(df)

    # Create subplots (2 rows, 1 column, shared x-axis)
    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,  # Share the x-axis
                        vertical_spacing=0.05,
                        row_heights=[0.8, 0.2])  # Adjust spacing between subplots

    # First line：close（main y-axis, left)  Stock price
    fig.add_trace(go.Scatter(x=df_list[0]['date'], y=df_list[0]['cum_pct_change'],
                             name='Stock price',
                             text=[f"Date: {date}<br>Close Price: {close:.2f}" for date, close in zip(df_list[0]['date'], df_list[0]['close'])],
                             hoverinfo='text',
                             line=dict(color='blue', width=1), yaxis='y1'),
                  row=1, col=1)

    # Line in subplot: Volume
    fig.add_trace(go.Scatter(x=df_list[0]['date'], y=df_list[0]['volume'],
                             name='Volume',
                             text=[f"Date: {date}<br>Close Price: {close:.2f}<br>Volume: {volume:.2f}" for date, close, volume in zip(df_list[0]['date'], df_list[0]['close'], df_list[0]['volume'])],
                             hoverinfo='text',
                             line=dict(color='red')),
                  row=2, col=1)

    # Customize axes per subplot
    fig.update_yaxes(title_text='Volume', row=2, col=1)
    fig.update_xaxes(title_text='Date', row=2, col=1)  # Only label bottom x-axis


    for i in range(len(df_list)):
        df = df_list[i]
        df['equity_cum_pct_change'] = (df['equity_value'] - df['equity_value'].iloc[0]) / df['equity_value'].iloc[0]

        # Second line：equity_value
        fig.add_trace(go.Scatter(x=df['date'], y=df['equity_cum_pct_change'],
                                 name=f'Equity value {i+1}/{len(df_list)}',
                                 text=[f"Equity Value: {equity_value:.2f}<br>Pct change: {equity_cum_pct_change:.2%}" for equity_value, equity_cum_pct_change in zip(df['equity_value'], df['equity_cum_pct_change'])],
                                 hoverinfo='text',
                                 line=dict(color=random_color(), width=3),
                                 visible='legendonly', yaxis='y1'),
                      row=1, col=1)

        # Filter buy/sell actions
        df_buy = (df['action'] == 'BUY')
        df_sell = (df['action'] == 'SELL')
        df_tp = (df['action'] == 'TAKE_PROFIT')
        df_sl = (df['action'] == 'STOP_LOSS')

        fig.add_trace(go.Scatter(x=df[df_buy]['date'], y=df[df_buy]['cum_pct_change'],
                                 mode='markers', name='Buy',
                                 text=[f"Date: {date}<br>Buy Price: {close:.2f}" for date, close in zip(df[df_buy]['date'], df[df_buy]['close'])],
                                 hoverinfo='text',
                                 marker=dict(symbol='triangle-up', size=15, color='green'),
                                 visible='legendonly', yaxis='y1'),
                      row=1, col=1)

        fig.add_trace(go.Scatter(x=df[df_sell]['date'], y=df[df_sell]['cum_pct_change'],
                                 mode='markers', name='Sell',
                                 text=[f"Date: {date}<br>Sell Price: {close:.2f}" for date, close in zip(df[df_sell]['date'], df[df_sell]['close'])],
                                 hoverinfo='text',
                                 marker=dict(symbol='triangle-down', size=15, color='orange'),
                                 visible='legendonly', yaxis='y1'),
                      row=1, col=1)

        fig.add_trace(go.Scatter(x=df[df_tp]['date'], y=df[df_tp]['cum_pct_change'],
                                 mode='markers', name='Take Profit',
                                 text=[f"Date: {date}<br>Close Price (take profit): {close:.2f}" for date, close in zip(df[df_tp]['date'], df[df_tp]['close'])],
                                 hoverinfo='text',
                                 marker=dict(symbol='star', size=15, color='gold'),
                                 line=dict(width=1, color='black'),
                                 visible='legendonly', yaxis='y1'),
                      row=1, col=1)

        fig.add_trace(go.Scatter(x=df[df_sl]['date'], y=df[df_sl]['cum_pct_change'],
                                 mode='markers', name='Stop loss',
                                 text=[f"Date: {date}<br>Close Price (stop loss): {close:.2f}" for date, close in zip(df[df_sl]['date'], df[df_sl]['close'])],
                                 hoverinfo='text',
                                 marker=dict(symbol='x', size=15, color='red'),
                                 line=dict(width=2, color='black'),
                                 visible='legendonly', yaxis='y1'),
                      row=1, col=1)


    # 手動設置次 y 軸
    fig.update_layout(title=stock_name + ' price & equity curve',
                      xaxis=dict(title='日期 Date',
                                 showspikes=True,  # 顯示懸停十字線
                                 spikemode='across',  # 跨軸顯示
                                 spikesnap='data',  # 吸附到數據點
                                 spikecolor='grey',  # 線條顏色
                                 spikethickness=1,  # 線條粗細
                                 spikedash='dot'),

                      yaxis=dict(title='Equity value',
                                 tickformat='.1%',
                                 side='left',
                                 showgrid=True,  # 顯示網格線
                                 showspikes=True,
                                 spikemode='across',
                                 spikecolor='grey',
                                 spikethickness=1,
                                 spikedash='dot',
                                 autorange=True,
                                 #range=[all_equity_min, all_equity_max],
                                 ),

                      legend=dict(x=1.1, y=1), # 調整圖例位置（避免被右軸覆蓋）
                      hovermode='x unified',  # 統一懸停模式，顯示所有 y 值
                      spikedistance=1000,     # 防止意外觸發（單位：像素）
                      )

    # Construct the 'visible' list for 'reset' button
    reset_visible_list = [True, True]  # the first 2 graphs are stock price and volume, keep them visible
    for j in range(len(fig.data) - 2):
        reset_visible_list.append('legendonly')

    # Construct the 'visible' list for 'show all' button
    show_all_visible_list = [True, True]
    for k in range(len(fig.data) - 2):
        if k % 5 == 0:    # since every equity curve diff by 5 units, with 'buy', 'sell', 'take_profit', 'stop_loss' in between
            show_all_visible_list.append(True)
        else:
            show_all_visible_list.append('legendonly')


    fig.update_layout(updatemenus=[dict(type="buttons",
                                        buttons=[dict(label="Reset",
                                                      method="update",
                                                      args=[{"visible": reset_visible_list}]),
                                                 dict(label="Show All",
                                                      method="update",
                                                      args=[{"visible": show_all_visible_list}])],
                                        x=1,  # Horizontal position (to the right of the plotting area)
                                        y=1,  # Vertical position (aligned with the top of the plotting area)
                                        xanchor="left",  # Anchor point for horizontal alignment
                                        yanchor="top")  # Anchor point for vertical alignment
                                   ]
                      )

    fig.show()
    return

if __name__ == '__main__':
    file_name_list = ['0388.HK_541021']
    graphplot('HKEX', file_name_list)

# use the following 2 lines to update pypi
#python3.11 setup.py sdist bdist_wheel
#python3.11 -m twine upload dist/*