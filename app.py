import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL

import plotly.graph_objs as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np
from datetime import date
from scipy.integrate import solve_ivp

#
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title='Vietnam COVID Modelling',
                suppress_callback_exceptions = True)
server = app.server

#
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

colors = {
    'background': '#111111',
    'color': '#7FDBFF'
}

tab = {'padding':'1%'}
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Navbar([
        # Use row and col to control vertical alignment of logo / brand
        dbc.Row(
            [
                dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                dbc.Col(dbc.NavbarBrand("Vietnam COVID Modelling", className="ml-2",style={'font-size':'20px', 'vertical-align':'center'})),
                dbc.Col(dbc.NavLink("Home", href="/",className='text-light font-weight-bold',style={'font-size':'15px', 'vertical-align':'center'})),
                dbc.Col(dbc.NavLink("About", href="/about",className='text-light font-weight-bold',style={'font-size':'15px', 'vertical-align':'center'}))
            ],
            align="center",
            no_gutters=True,
        ),
    ],color="dark",dark=True,
    style={'text-decoration':'none','color':'white'}),
    html.Div(id='page-content')
])

about_page = html.Div([dcc.Markdown(
                    '''
                    # About us
                    * Tuan Khoi Nguyen - Data engineer, Main website developer
                    * Ngo Hoang Anh - Main model developer, Web developer
                    * Thu Anh Nguyen - Supervisor
                    '''
                )],
                style = {'margin':'5%'})


def generate_inputs():

    num_slider = [html.H3('Number of Stages'),
                  dbc.Tooltip(
                      "Number of main representative stages during the pandemic",
                      target="num", placement='right'
                  ),
                  dcc.Slider(id='num', min=1, max=5, value=4,
                             marks={i: str(i) for i in range(6)})]
    
    text_boxes = [html.H3('Stage Inputs'),
                  html.Div(id='in-r0'),
                  dbc.Tooltip(
                      html.Ul([
                          html.H6("Each stage contains the following:"),
                          html.Li("Starting date"),
                          html.Li("R0 Reduction Rate"),
                          html.Li("Contained proportion")],style={'text-align':'left'}),
                      target="in-r0", placement='right'
                  )
                  ]

    input_list = [num_slider, text_boxes]
    widgets = list()    
    for sublist in input_list:
        sublist.append(html.H1(''))
        for item in sublist:
            widgets.append(item)

    return widgets

#
main_page = html.Div([
    html.Div([

        html.Div(
            [
                dbc.Button(
                    html.H2("Basic Inputs"),
                    id="collapse-button",
                    className="mb-3",
                    color="primary",
                    style={'width':'100%'}
                ),
                dbc.Collapse(
                    [html.Div([html.H3('Population'),
                               dbc.Tooltip(
                                    "Population",
                                    target="div-N", placement='right'
                               ),
                               dcc.Slider(id='slider-N', min=100000, max=100000000, value=11000000, step=100000,
                                          tooltip={'always_visible': True, 'placement':'bottom'},
                                          marks = {i: str(i) for i in [100000, 50000000,100000000]}
                                          )],id='div-N'),

                    html.Div([html.H3('Outbreak Date'),
                               dbc.Tooltip(
                                    "Assumed 1st day of outbreak",
                                    target="div-date", placement='right'
                               ),
                                dcc.DatePickerSingle(
                                    id='date',
                                    min_date_allowed=date(2020, 1, 1),
                                    max_date_allowed=date(2030, 12, 31),
                                    initial_visible_month=date(2021, 4, 15),
                                    date=date(2021, 4, 15),
                                    display_format = 'DD/MM/YYYY'
                                ),
                    ], id = 'div-date'),

                     html.Div([html.H3("Hospital Capacity: "),
                               dbc.Tooltip(
                                    "Hospital Capacity",
                                    target="div-hcap", placement='right'
                               ),
                               dcc.Input(id='hcap', value=100000, type='number')], style={'margin':'4% 0%'},id='div-hcap'),

                     html.Div([html.H3('Initial R0'),
                               dbc.Tooltip(
                                    "Initial R0 at 1st day of outbreak",
                                    target="div-r0", placement='right'
                               ),
                               dcc.Slider(id='slider-r0', min=0, max=20, value=3.9, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-r0'),

                     html.Div(generate_inputs()),
                    

                     ],
                    id="collapse",
                    style = tab
                ),

                dbc.Button(
                    html.H2("Proportion Inputs"),
                    id="collapse-button-p",
                    className="mb-3",
                    color="info",
                    style={'width':'100%'}
                ),
                dbc.Collapse(
                    [
                     html.Div([html.H6('Hospitalisation'),
                               dbc.Tooltip(
                                    "Hospital",
                                    target="div-ph", placement='right'
                               ),
                               dcc.Slider(id='slider-ph', min=0, max=1, value=0.85, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-ph'),

                     html.Div([html.H6('Critical'),
                               dbc.Tooltip(
                                    "Critical",
                                    target="div-pc", placement='right'
                               ),
                               dcc.Slider(id='slider-pc', min=0, max=1, value=0.04, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-pc'),

                     html.Div([html.H6('Deceased'),
                               dbc.Tooltip(
                                    "Deceased",
                                    target="div-pf", placement='right'
                               ),
                               dcc.Slider(id='slider-pf', min=0, max=1, value=0.25, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-pf'),

                     html.Div([html.H6('Media Impact'),
                               dbc.Tooltip(
                                    "Media Impact",
                                    target="div-pj", placement='right'
                               ),
                               dcc.Slider(id='slider-pj', min=0, max=1, value=0.1, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-pj'),

                     html.Div([html.H6('Quarantined'),
                               dbc.Tooltip(
                                    "Qurantined",
                                    target="div-pquar", placement='right'
                               ),
                               dcc.Slider(id='slider-pquar', min=0, max=1, value=0.8, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-pquar'),

                     html.Div([html.H6('Quarantined & Hospitalised'),
                               dbc.Tooltip(
                                    "Quarantined in Hospital",
                                    target="div-pqhsp", placement='right'
                               ),
                               dcc.Slider(id='slider-pqhsp', min=0, max=1, value=0.1, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-pqhsp'),

                     html.Div([html.H6('Cross-Contamination'),
                               dbc.Tooltip(
                                    "Cross Contamination",
                                    target="div-pcross", placement='right'
                               ),
                               dcc.Slider(id='slider-pcross', min=0, max=1, value=0.01, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-pcross'),
                     ],
                    id="collapse-p",
                    style = tab
                ),

                dbc.Button(
                    html.H2("Time Inputs"),
                    id="collapse-button-t",
                    className="mb-3",
                    color="danger",
                    style={'width':'100%'}
                ),
                dbc.Collapse(
                    [html.Div([html.H6('Incubated'),
                               dbc.Tooltip(
                                    "Incubated",
                                    target="div-tinc", placement='right'
                               ),
                               dcc.Slider(id='slider-tinc', min=2.5, max=5, value=3, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-tinc'),

                     html.Div([html.H6('Infectious'),
                               dbc.Tooltip(
                                    "Infectious",
                                    target="div-tinf", placement='right'
                               ),
                               dcc.Slider(id='slider-tinf', min=5.0, max=7, value=6, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-tinf'),

                     html.Div([html.H6('Intensive Care'),
                               dbc.Tooltip(
                                    "ICU",
                                    target="div-ticu", placement='right'
                               ),
                               dcc.Slider(id='slider-ticu', min=10.0, max=14, value=10, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-ticu'),

                     html.Div([html.H6('Hospitalised'),
                               dbc.Tooltip(
                                    "Hospitalised",
                                    target="div-thsp", placement='right'
                               ),
                               dcc.Slider(id='slider-thsp', min=5.0, max=10, value=6, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-thsp'),
                     html.Div([html.H6('Critical'),
                               dbc.Tooltip(
                                    "Critical",
                                    target="div-tcrt", placement='right'
                               ),
                               dcc.Slider(id='slider-tcrt', min=10.0, max=14, value=10, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-tcrt'),

                     html.Div([html.H6('Self-Recovery'),
                               dbc.Tooltip(
                                    "Self-Recover",
                                    target="div-trec", placement='right'
                               ),
                               dcc.Slider(id='slider-trec', min=12.0, max=14, value=13, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-trec'),

                     html.Div([html.H6('Quarantine'),
                               dbc.Tooltip(
                                    "Quarantine",
                                    target="div-tqar", placement='right'
                               ),
                               dcc.Slider(id='slider-tqar', min=4, max=21, value=21, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-tqar'),

                     html.Div([html.H6('Quarantined & Hospitalised'),
                               dbc.Tooltip(
                                    "Quarantined in Hospital",
                                    target="div-tqah", placement='right'
                               ),
                               dcc.Slider(id='slider-tqah', min=0, max=5, value=2, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-tqah'),
                     ],
                    id="collapse-t",
                    style = tab
                ),
            ]
        ,style = {'width':'33%', 'display':'inline-block', 'vertical-align':'top', 'padding':'2%'}),
        # 
        html.Div([
            dcc.Graph(id='my-output'),
            html.Div([
                      dcc.Checklist(
                            options=[
                                {'label': 'Compare Hospital Capacity', 'value': 1},
                                {'label': 'Show by Date', 'value': 2}
                            ],
                            value=[],
                            labelStyle={'display': 'block'},
                            id='mods'
                        )
                    ], style={'padding':'0% 3%','display':'inline-block'}),
            html.Div(
                [
                    html.Button("Download Statistics (.csv)", id="btn_csv", style={'color':'white'}),
                    dcc.Download(id="download-dataframe-csv"),
                    html.Button("Download Summary (.txt)", id="btn_sum", style={'color':'white'}),
                    dcc.Download(id="download-sum"),
                ], style={'padding':'2% 3%','display':'inline-block', 'vertical-align':'bottom'}
            ),        
        ],
        style = {'width':'66%', 'display':'inline-block', 'vertical-align':'top', 'border-style':'outset', 'margin':'1% 0%'}),
        

    ])
])


# 
@app.callback(
    Output('in-r0', 'children'),
    [Input('num', 'value')])
def ins_generate(n):
    return [html.Div([html.H5(f'Stage {i+1}:'),
                    html.Div([html.H6('Starting Date'), dcc.Slider(id={'role':'day', 'index':i}, min=1, max=100, value=10*i+1, step=1, tooltip={'always_visible': False}, marks={1:'1',100:'100'})],
                                style={'width': '33%', 'display': 'inline-block'}),
                    html.Div([html.H6('R0 Reduction'), dcc.Input(id={'role':'r0', 'index':i}, value=1, step=0.1, type='number', style={'width':'100%'})],
                                style={'width': '28%', 'display': 'inline-block', 'margin':'0 5% 0 0'}),
                    html.Div([html.H6('Contained Proportion'), dcc.Slider(id={'role':'pcont', 'index':i}, min=0, max=1, value=0.15*(i+1), step=0.01, tooltip={'always_visible': False}, marks={0:'0',1:'1'})],
                                style={'width': '33%', 'display': 'inline-block'})
                    ], style={'border-style':'outset', 'margin':'1%', 'padding': '1%'}) for i in range(n)]

@app.callback(
    [Output(f"collapse{i}", "is_open") for i in ['','-p','-t']],
    [Input(f"collapse-button{i}", "n_clicks") for i in ['','-p','-t']],
    [State(f"collapse{i}", "is_open") for i in ['','-p','-t']],
)
def toggle_accordion(n1, n2, n3, is_open1, is_open2, is_open3):
    ctx = dash.callback_context

    if not ctx.triggered:
        return False, False, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "collapse-button" and n1:
        return not is_open1, False, False
    elif button_id == "collapse-button-p" and n2:
        return False, not is_open2, False
    elif button_id == "collapse-button-t" and n3:
        return False, False, not is_open3
    return False, False, False

@app.callback(
    Output('my-output', 'figure'),
    Output("download-dataframe-csv", "data"),
    Output("download-sum", "data"),
    Input('slider-N', component_property='value'),
    Input('num', 'value'),
    Input('slider-r0', component_property='value'),
    [Input({'role':'r0', 'index':ALL}, component_property='value')],
    [Input({'role':'pcont', 'index':ALL}, component_property='value')],
    [Input({'role':'day', 'index':ALL}, component_property='value')],
    Input('date', component_property='date'),
    Input('hcap', component_property='value'),
    Input('slider-tinc', component_property='value'),
    Input('slider-tinf', component_property='value'),
    Input('slider-ticu', component_property='value'),
    Input('slider-thsp', component_property='value'),
    Input('slider-tcrt', component_property='value'),
    Input('slider-trec', component_property='value'),
    Input('slider-tqar', component_property='value'),
    Input('slider-tqah', component_property='value'),
    Input('slider-pquar', component_property='value'),
    Input('slider-pcross', component_property='value'),
    Input('slider-pqhsp', component_property='value'),
    Input('slider-pj', component_property='value'),
    Input('slider-ph', component_property='value'),
    Input('slider-pc', component_property='value'),
    Input('slider-pf', component_property='value'),
    Input("btn_csv", "n_clicks"),
    Input("btn_sum", "n_clicks"),
    Input('mods', component_property='value'),
    prevent_initial_call=True,
)

def update_graph(N, n_r0, r0, delta_r0, pcont, day, date, hcap,
                 tinf, tinc, thsp, tcrt,
                 ticu, tqar, tqah, trec,
                 pquar, pcross, pqhsp,
                 pj, ph, pc, pf,
                 ligma,sugma,mod):
    def R0_dynamic(t):
        if not delta_r0 or not pcont or not day:
            return 3.9
        else:
            i = 0
            while t>day[i]:
                if i == len(day)-1:
                    break
                i+=1
            return max(r0*pcont[i]-2*(t-day[i])/day[i] * delta_r0[i],0)

    args = (R0_dynamic,
            tinf, tinc, thsp, tcrt,
            ticu, tqar, tqah, trec,
            ph, pc, pf,
            pj, pquar, pqhsp, pcross)

    n_infected = 1
    initial_state = [(N - n_infected) / N, 0, n_infected / N, 0, 0, 0, 0, 0, 0]

    sol = solve_ivp(SEIQHCDRO_model, [0, 150],
                    initial_state, args=args,
                    t_eval=np.arange(151), method="Radau")
    S, E, I, Q, H, C, D, R, O = sol.y

    x_day = pd.date_range(date, periods=151).tolist()
    x = x_day if 2 in mod else np.linspace(0, 150, 151)
    
    fig = make_subplots(rows=3, cols=3, x_title="Date" if 2 in mod else "Days since outbreak", y_title="Cases")
    
    ift = np.round((I + H + C + D + R + O) * N)
    hsp = np.round((H + C + D + R) * N)
    crt = np.round((C + D) * N)
    ded = np.round(D * N)

    df = pd.DataFrame({"Date": x_day, "Infected": ift, "Hospitalised": hsp, "Critical": crt, "Deaths":ded})

    fig.add_trace(go.Scatter(x=x, y=ift, name='Infected'), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=hsp, name='Hospitalised'), row=1, col=2)
    fig.add_trace(go.Scatter(x=x, y=np.round((H + R) * N), name='Non-critical Hospitalised'), row=1, col=3)
    fig.add_trace(go.Scatter(x=x, y=crt, name='Critical'), row=2, col=1)
    fig.add_trace(go.Scatter(x=x, y=ded, name='Deaths'), row=2, col=2)
    fig.add_trace(go.Scatter(x=x, y=np.round((I + O) * N), name='Undiscovered Cases'), row=2, col=3)
    fig.add_trace(go.Scatter(x=x, y=np.round(Q * N), name='Daily Quarantined'), row=3, col=1)
    fig.add_trace(go.Scatter(x=x, y=np.array([hsp[i + 1] - hsp[i] for i in range(150)]), name='Daily Hospital Incidence'), row=3, col=2)
    fig.add_trace(go.Scatter(x=x, y=np.round((E + Q) * N), name='Daily Exposed'), row=3, col=3)
    if 1 in mod:
        fig.add_trace(go.Scatter(x=x, y=hcap * np.ones(151), name='Hospital Capacity'), row=1, col=2)
        
    fig.update_layout(
        title={
            'text': "Prediction of Different COVID Scenarios in Vietnam",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor = 'rgb(61,61,61)',
        font=dict(color='rgb(174, 211, 210)')
    )

    if 2 in mod:
        fig.update_xaxes(dtick="M2", tickformat="%d/%m/%y")

    ctx = dash.callback_context.triggered
    if ctx:
        current_call = ctx[0]['prop_id'].split('.')[0]
        if current_call=='btn_csv':
            return fig, dcc.send_data_frame(df.to_csv, "daily_data.csv"), None
        elif current_call=='btn_sum':
            text=f'''
Generated by Vietnam COVID Modelling Team

Population: {N} people
The outbreak is assumed to begin on {date}, with R0 = {r0}

The outbreak has {n_r0} stages, starting on days {day}:
_Reduction of R0 through each stage: {delta_r0}
_Containing proportion through each stage: {pcont}

Infectious period: {tinf} days
Incubated period: {tinc} days
Hospitalised Duration: {thsp} days
Critical Status Duration: {tcrt} days
Intensive Care Duration: {ticu} days
Quarantine Duration: {tqar} days
Quarantine in Hospital Duration: {tqah} days
Recovery time: {trec} days

Quarantined proportion: {pquar}
Cross-contamination proportion: {pcross}
Quarantined & Hospitalised proportion {pqhsp}
Journal impact level: {pj*100}%
Hospitalised rate: {ph*100}%
Critical rate: {pc*100}%
Death rate: {pf*100}%

Hospital capacity is {hcap}, which is {'not enough' if hcap<np.max(hsp) else 'sufficient'} for the worst day of the outbreak, with {np.max(hsp)} hospital patients.

On average:
_{np.mean(ift)} positive cases
_{np.mean(hsp)} hospitalised
_{np.mean(crt)} in critical condition
_{np.mean(ded)} died

On the worst days: 
_{np.max(ift)} positive cases
_{np.max(hsp)} hospitalised
_{np.max(crt)} in critical condition
_{np.max(ded)} died

            '''
            return fig, None, dict(content=text, filename="summary.txt")
    return fig, None, None

def SEIQHCDRO_model(t, y, R_0,
                    T_inf, T_inc, T_hsp, T_crt, T_icu, T_quar, T_quar_hosp, T_rec,
                    p_h, p_c, p_f, p_jrnl, p_quar, p_quar_hosp, p_cross_cont):
    """
    t: time step for solve_ivp
    y: solution of previous timestep (or initial solution)
    R_0: basic reproduction number. This can be a constant, or a function with respect to time. These two cases are handled using an if condition of the callability of R_0.
    T_inf: infectious period of an infected agent
    T_inc: incubation time
    T_hsp: duration for an infected agent to check into a health agency
    T_crt: duration for a hospitalised person to turn into a critical case since the initial check-in
    T_icu: duration for a person to stay in the Intensive Care Unit until a clinical outcome has been decided (Recovered or Death)
    T_quar: duration of quarantine, indicated by the government
    T_quar_hosp: duration from the start of quarantine until the patient get tested positive for COVID-19 and hospitalised
    p_h: proportion of hospitalised patients
    p_c: proportion of hospitalised patients who switched to a critical case
    p_f: proportion of critical cases resulting in death
    p_cont: the reduced percentage of contact tracing between individuals in the population due to policy measures. Same as R_0, this can be a constant or a function with respect to time. These two cases are also handled using an if condition.
    p_jrnl: the reduced percentage of contact tracing between individuals in the population due to policy measures. The percentage of p_jrnl are kept constant, since COVID-19 news, policies and activities are updated everyday, regardless whether there is an outbreak.
    p_quar: proportion of exposed individual who are quarantined, either at home or at a facility under the supervision of local authority
    p_quar_hosp: proportion of quarantined individuals who are infected with COVID-19 and hospitalised
    p_cross_cont: cross contamination ratio within quarantined facility under the supervision of local authority
    """

    if callable(R_0):
        def R0_dynamic(t):
            return R_0(t)
    else:
        def R0_dynamic(t):
            return R_0

    S, E, I, Q, H, C, D, R, O = y

    dS_dt = - R0_dynamic(t) * (1 / T_inf + (1 - p_h) / T_rec) * I * S
    dE_dt = R0_dynamic(t) * (1 / T_inf + (1 - p_h) / T_rec) * I * S - 1 / T_inc * E - p_quar * (E) / T_quar
    dI_dt = 1 / T_inc * E - (p_h / T_inf + (1 - p_h) / T_rec) * I
    dQ_dt = p_quar * (E) / T_quar - (p_quar_hosp + p_cross_cont) * Q / T_quar_hosp
    dH_dt = p_h / T_inf * I - (1 - p_c) / T_hsp * H - p_c / T_crt * H - p_h / T_rec * H + (
                p_quar_hosp + p_cross_cont) * Q / T_quar_hosp
    dC_dt = p_c / T_crt * H - C / (T_icu + T_crt)
    dD_dt = p_f / (T_icu + T_crt) * C
    dR_dt = (1 - p_c) / T_hsp * H + (1 - p_f) / (T_icu + T_crt) * C
    dO_dt = (1 - p_h) / T_rec * I + p_h / T_rec * H

    dy_dt = [dS_dt, dE_dt, dI_dt, dQ_dt, dH_dt, dC_dt, dD_dt, dR_dt, dO_dt]
    return dy_dt

# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/about':
        return about_page
    # elif pathname == '/page-2':
    #     return page_2_layout
    else:
        return main_page
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    #app.server.run(port=8000, host='127.0.0.1')
    app.run_server(debug=True)