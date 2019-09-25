import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State
import os
import io
import plotly.graph_objs as go
import base64

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df_KCLT = pd.read_csv('us-weather-history/KCLT.csv')
features = df_KCLT.columns[1:-1]
opts = [{'label' : i, 'value' : i} for i in features]

df_KCLT['date'] = pd.to_datetime(df_KCLT.date)
dates = ['2014-07', '2014-08', '2014-09', '2014-10', '2014-11', '2014-12', '2015-01', '2015-02', '2015-03', '2015-04', '2015-05', '2015-06']
date_mark = {i : dates[i] for i in range(len(dates))}

graph_1 = go.Scatter(x = df_KCLT['date'], y = df_KCLT['actual_mean_temp'], name = 'Actual-Mean-Temperature', line = dict(width = 2, color = 'rgb(229,151,50)'))
layout = go.Layout(title = 'Temperature Plot', hovermode = 'closest')
fig = go.Figure(data = [graph_1], layout = layout)

app.layout = html.Div([
                        html.H1(children='US Weather Report'),
                        html.Div([
                                    html.H1(' A graph to show the fluctuations in temperature: ')
                                 ],
                                 style = {'padding' : '50px', 'backgroundColor' : '#3avab2'}
                                 ),
                        dcc.Upload(id='upload-data',
                                    children=html.Div(['Drag and Drop or ',html.A('Select Files')]),
                                    style={'width': '100%','height': '60px',
                                           'lineHeight': '60px','borderWidth': '1px',
                                           'borderStyle': 'dashed','borderRadius': '5px',
                                           'textAlign': 'center','margin': '10px'} 
                                  ),
                                  html.Div(id = 'output-data-upload'),                
                        dcc.Graph(id = 'plot' , figure = fig),
                        html.P([
                                html.Label('Choose a feature for Y-Axis'),
                                dcc.Dropdown(id = 'opt', options= opts, 
                                             value = opts[0]['value'],placeholder = 'Selct Y-axis')
                               ],style = {'width': '400px', 'fontSize' : '20px',
                                          'padding-left' : '100px' ,'display': 'inline-block'}
                              ), 
                        # html.P([
                        #         html.Label('Choose multiple dimensions for Y-axis'),
                        #         dcc.Dropdown(id = 'opt', options= opts, 
                        #                      value = opts[0]['value'], placeholder = 'Select Y-axis', multi = True)
                        #        ],style = {'width': '400px', 'fontSize' : '20px',
                        #                   'padding-left' : '100px' ,'display': 'inline-block'}
                            #   ),
                        html.P([
                                html.Label('Time Period'),
                                dcc.RangeSlider(id = 'slider', marks = date_mark, min = 0, max = 11, value = [3,4])
                               ],style = {'width' : '80%','fontSize' : '20px',
                                          'padding-left' : '100px','display': 'inline-block'}
                              )      
                         ])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  

        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')])

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(Output('plot', 'figure'),
             [Input('opt', 'value'),
             Input('slider', 'value')])             

def update_graph(X,Y):
    df = df_KCLT[(df_KCLT.date > dates[Y[0]])& (df_KCLT.date < dates[Y[1]])]

    graph_1 = go.Scatter(x = df.date, y = df['actual_mean_temp'], name = Y,
                         line = dict(width = 2, color='rgb(106,181,135)'))
    graph_2 = go.Scatter(x = df.date, y = df[X], name = Y,
                         line = dict(width = 2, color='rgb(106,181,135)'))
    
    fig = go.Figure(data = [graph_1,graph_2], layout = layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug= True)
