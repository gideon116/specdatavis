import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
import plotly.express as px

from dash import no_update
import os

import pandas as pd

def uvvis(file, reffile):

    lines = file.splitlines()
    line = [i.split('\t') for i in lines]
    dictionary = {'WAVELENGTH': [], 'REFLECTANCE': []}

    ref_lines = reffile.splitlines()
    ref_line = [i.split('\t') for i in ref_lines]
    ref_dict = {'WAVELENGTH': [], 'REFLECTANCE': []}

    for index, l in enumerate(line):
        if index > 17:
            dictionary['WAVELENGTH'].append(float(l[0]))
            dictionary['REFLECTANCE'].append(float(l[1]))

    for index, l in enumerate(ref_line):
        ref_dict['WAVELENGTH'].append(float(l[0]))
        ref_dict['REFLECTANCE'].append(float(l[1]))

    df = pd.DataFrame.from_dict(dictionary)
    df_ref = pd.DataFrame.from_dict(ref_dict)
    print(df_ref)

    df_new = pd.DataFrame()
    df_new['WAVELENGTH'] = df['WAVELENGTH']
    df_new['REFLECTANCE'] = df['REFLECTANCE'] * df_ref['REFLECTANCE'] / 10000
    df_new['ABSORBANCE'] = 1 - df_new['REFLECTANCE']

    fig = px.line(df_new, x='WAVELENGTH', y='ABSORBANCE')

    fig.update_yaxes(nticks=20, type='linear')
    fig.update_xaxes(nticks=20)

    return fig

def ftir(file):

    lines = file.splitlines()
    line = [i.split('\t') for i in lines]
    dictionary = {'WAVENUMBER': [], 'Y': []}

    for index, l in enumerate(line):
        dictionary['WAVENUMBER'].append(float(l[0]))
        dictionary['Y'].append(float(l[1]))

    df = pd.DataFrame.from_dict(dictionary)
    df['Y'] = 100 - df['Y']
    df['WAVELENGTH'] = 10_000 / df['WAVENUMBER']
    # df.drop(df.tail(2500).index, inplace=True)

    fig = px.line(df, x='WAVELENGTH', y='Y')
    fig.update_yaxes(nticks=20, type='linear', range=[0, 100])
    fig.update_xaxes(nticks=20, range=[3, 12])

    return fig

def xrd(file):
    lines = file.splitlines()
    line = [i.split('\t') for i in lines]
    dictionary = {'DEGREE': [], 'INTENSITY': []}

    for index, l in enumerate(line):
        if index > 17:
            dictionary['DEGREE'].append(l[0])
            dictionary['INTENSITY'].append(l[1])

    df = pd.DataFrame.from_dict(dictionary)
    fig = px.line(df, x='DEGREE', y='INTENSITY')
    fig.update_yaxes(nticks=20, type='linear')
    fig.update_xaxes(nticks=20)
    return fig








colors = {
    'background': '#444444',
    'text': '#7FDBFF'
}
def rfig():
    fig = px.line(x=[0], y=[0])
    return fig

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

def serve_layout():

    # App Layout
    return html.Div(
        id="root",
        children=[
            # Main body
            html.Div([
                html.Div(
                    id="app-container",
                    children=[
                        html.Div(
                            id="banner",
                            children=[html.H2("Data Visualizer", id="title", style={'font-weight': 300,
                                                                                  "textAlign": "center"})]
                        ),
                        html.Div(id="dots", children=[
                            dcc.Graph(id='dots-graph')
                        ]),
                    ],
                ),
            ], className='eight columns'),

            # Sidebar
            html.Div([
                html.Div(
                    id="sidebar",
                    children=[
                        html.Section(
                            children=[

                                html.Div(
                                    dcc.Dropdown(
                                        id="datatype",
                                        options=[
                                            {"label": "UV-VIS", "value": "1"},
                                            {"label": "FTIR", "value": "2"},
                                            {"label": "XRD", "value": "3"}
                                        ],
                                        searchable=False,
                                        placeholder="Enhance...",
                                        value='1'
                                    ),
                                    style={'margin-top': '5px', 'margin-bottom': '5px'}
                                ),

                            ],
                            style={
                                'padding': 20,
                                'margin': 5,
                                'borderRadius': 5,
                                'border': 'thin lightgrey solid',

                                # Remove possibility to select the text for better UX
                                'user-select': 'none',
                                '-moz-user-select': 'none',
                                '-webkit-user-select': 'none',
                                '-ms-user-select': 'none'
                            }),
                        html.Section(
                            children=[

                                html.Section(
                                    id='calibratediv',
                                    children=[
                                        html.Div(
                                            id='ref',
                                            style={
                                                'display': 'block',
                                                'margin-bottom': '5px',
                                                'margin-top': '5px'
                                            },
                                            children=[
                                                html.P('Calibrated', style={'color': 'rgb(0,0,0)'},
                                                       className='six columns'),
                                                dcc.RadioItems(
                                                    id='calibrate',
                                                    options=[
                                                        {"label": " Yes", "value": "2"},
                                                        {"label": " No", "value": "1"},
                                                    ],
                                                    value="2",
                                                    labelStyle={
                                                        'display': 'inline-block',
                                                        'margin-right': '7px',
                                                        'font-weight': 300
                                                    },
                                                    className='six columns'
                                                )
                                            ],
                                            className='row'
                                        ),

                                    ],
                                    style={
                                        'padding': 10,
                                        'margin': 5,
                                        'borderRadius': 5,
                                        'border': 'thin lightgrey solid',

                                        # Remove possibility to select the text for better UX
                                        'user-select': 'none',
                                        '-moz-user-select': 'none',
                                        '-webkit-user-select': 'none',
                                        '-ms-user-select': 'none'
                                    }),

                                dcc.Upload(
                                    id="upload-ref",
                                    children=[
                                        "Drag and Drop or Reference",
                                        html.A(children="Select File"),
                                    ],
                                ),

                                html.Div(
                                    id="button-group",
                                    children=[
                                        html.Button(
                                            "Run Operation", id="button-run-operation",
                                            style={'color': 'rgb(0,0,0)',
                                                   'margin': 5},
                                            n_clicks_timestamp=0
                                        ),
                                        html.Button("Undo", id="button-undo",
                                                    style={'color': 'rgb(0,0,0)'},
                                                    n_clicks_timestamp=0),
                                    ],
                                ),
                            ],
                            style={
                                'padding': 20,
                                'margin': 5,
                                'borderRadius': 5,
                                'border': 'thin lightgrey solid',

                                # Remove possibility to select the text for better UX
                                'user-select': 'none',
                                '-moz-user-select': 'none',
                                '-webkit-user-select': 'none',
                                '-ms-user-select': 'none'
                            }),
                        html.Section(id='upload-section', children=[
                            dcc.Upload(
                                id="upload-image1",
                                children=[
                                    "Drag and Drop or ",
                                    html.A(children="Select File"),
                                ],
                            )
                        ], style={
                                'padding': 20,
                                'margin': 5,
                                'borderRadius': 5,
                                'border': 'thin lightgrey solid',

                                # Remove possibility to select the text for better UX
                                'user-select': 'none',
                                '-moz-user-select': 'none',
                                '-webkit-user-select': 'none',
                                '-ms-user-select': 'none'
                            }, n_clicks_timestamp=0
                        )

                    ])
            ], className='four columns', style={'backgroundColor': 'rgb(235,235,235)',
                                                'height': '1000px'}),

        ], className='row'
    )


app.layout = serve_layout


@app.callback([dash.dependencies.Output('upload-image1', 'contents')],
              [dash.dependencies.Input('button-undo', 'n_clicks_timestamp'),
               dash.dependencies.Input('upload-section', 'n_clicks_timestamp')])
def undos(undo, section):

    if int(undo) > int(section):
        return [None]
    elif int(undo) <= int(section):
        return no_update


@app.callback([dash.dependencies.Output('upload-image1', 'style'),
               dash.dependencies.Output('upload-ref', 'style'),
               dash.dependencies.Output('calibratediv', 'style'),
               dash.dependencies.Output('dots', 'style'),
               dash.dependencies.Output('upload-image1', 'children'),
               dash.dependencies.Output('upload-ref', 'children')],
              [dash.dependencies.Input('datatype', 'value'),
               dash.dependencies.Input('calibrate', 'value'),
               dash.dependencies.Input('upload-image1', 'contents'),
               dash.dependencies.Input('upload-ref', 'contents')])
def surface_info(datatype, calibrate, upload, ref):
    style = {
        "color": "darkgray",
        "width": "100%",
        "height": "40px",
        "lineHeight": "50px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "borderColor": "darkgray",
        "textAlign": "center",
        "padding": "2rem 0",
        "margin-bottom": "2rem",
        'backgroundColor': 'rgb(200,200,200)'
    }
    child = ['Upload Complete']

    old_child = ["Drag and Drop or ",
                 html.A(children="Select a File"),
                 ]
    old_style = {
        "color": "darkgray",
        "width": "100%",
        "height": "40px",
        "lineHeight": "50px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "borderColor": "darkgray",
        "textAlign": "center",
        "padding": "2rem 0",
        "margin-bottom": "2rem"
    }

    surface_color_format_style = {
                                    'padding': 10,
                                    'margin': 5,
                                    'borderRadius': 5,
                                    'border': 'thin lightgrey solid',

                                    'user-select': 'none',
                                    '-moz-user-select': 'none',
                                    '-webkit-user-select': 'none',
                                    '-ms-user-select': 'none'
                                    }

    dropdown_style = {'font_color': 'rgb(0,0,0)'}

    if int(datatype) == 1:

        if int(calibrate) == 1:
            if upload is not None:
                if ref is not None:
                    return style, surface_color_format_style, surface_color_format_style, \
                           {'border': 'thin lightgrey solid', "borderStyle": "dashed"}, child, child
                elif ref is None:
                    return style, surface_color_format_style, surface_color_format_style, \
                           {'border': 'thin lightgrey solid', "borderStyle": "dashed"}, child, old_child
            elif upload is None:
                if ref is not None:
                    return style, surface_color_format_style, surface_color_format_style, \
                           {'border': 'thin lightgrey solid', "borderStyle": "dashed"}, old_child, child
                elif ref is None:
                    return style, surface_color_format_style, surface_color_format_style, \
                           {'border': 'thin lightgrey solid', "borderStyle": "dashed"}, old_child, old_child


        if int(calibrate) == 2:
            if upload is not None:
                return style, {'display': 'none'}, surface_color_format_style, \
                       {'border': 'thin lightgrey solid', "borderStyle": "dashed"}, child, child,
            elif upload is None:
                return style, {'display': 'none'}, surface_color_format_style, \
                       {'border': 'thin lightgrey solid', "borderStyle": "dashed"}, old_child, old_child

    elif int(datatype) == 2:
        if upload is not None:
            return style, {'display': 'none'}, {'display': 'none'}, \
                   {'border': 'thin lightgrey solid', "borderStyle": "dashed"}, child, old_child
        elif upload is None:
            return style, {'display': 'none'}, {'display': 'none'}, \
                   {'border': 'thin lightgrey solid', "borderStyle": "dashed"}, old_child, old_child

    elif int(datatype) == 3:
        if upload is not None:
            return style, {'display': 'none'}, {'display': 'none'}, \
                   {'border': 'thin lightgrey solid', "borderStyle": "dashed"}, child, child
        elif upload is None:
            return style, {'display': 'none'}, {'display': 'none'}, \
                   {'border': 'thin lightgrey solid', "borderStyle": "dashed"}, old_child, old_child


@app.callback([dash.dependencies.Output('dots-graph', 'figure')],
              [dash.dependencies.Input('button-run-operation', 'n_clicks_timestamp'),
               dash.dependencies.Input('button-undo', 'n_clicks_timestamp'),
               dash.dependencies.Input('datatype', 'value'),
               dash.dependencies.Input('calibrate', 'value'),
               dash.dependencies.Input('upload-image1', 'contents'),
               dash.dependencies.Input('upload-ref', 'contents')])
def tabcontents(run, undo, datatype, surfcolor, im1, imref):
    data = {'data': [{
            'type': 'line',
            'x': [1],
            'y': [1]}]}

    if int(run) > 0:
        if int(undo) > int(run):
            return [rfig()]
        else:
            if int(datatype) == 1:
                if '1' in surfcolor:
                    string1 = (str(im1)).split(";base64,")[-1]
                    decoded1 = base64.b64decode(string1).decode()

                    string2 = (str(imref)).split(";base64,")[-1]
                    decoded2 = base64.b64decode(string2).decode()

                    return [uvvis(decoded1, decoded2)]
                elif '2' in surfcolor:
                    return rfig()

            elif int(datatype) == 2:
                string1 = (str(im1)).split(";base64,")[-1]
                decoded1 = base64.b64decode(string1).decode()

                return [ftir(decoded1)]

            elif int(datatype) == 3:
                string1 = (str(im1)).split(";base64,")[-1]
                decoded1 = base64.b64decode(string1).decode()

                return [xrd(decoded1)]

    else:
        return [rfig()]


if __name__ == "__main__":
    app.run_server(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8070")), debug=True, )
