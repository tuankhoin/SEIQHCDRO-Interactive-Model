import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np
import math
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_squared_log_error

# List những cái css m sẽ dùng ở đây vô 1 array
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Này k biết để lm gì, chắc custom css
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# Tất cả mọi thứ sẽ nằm trong app.layout, tất cả sub-component của 1 component thì gói vào 1 array. Tên thì cứ như html cơ bản thôi
app.layout = html.Div([
    html.Div([

        html.Div(
            [
                dbc.Button(
                    "Basic Inputs",
                    id="collapse-button",
                    className="mb-3",
                    color="primary",
                ),
                dbc.Collapse(
                    [html.Div([html.H6('Population'),
                            dcc.Slider(id='slider-N', min = 100000, max = 100000000, value = 11000000, step = 100000, tooltip = {'always_visible': True}
                            )]),  

                    html.Div([html.H6('R0'),
                            dcc.Slider(id='slider-r0',min = 0, max = 20, value = 3.9, step = 0.1, tooltip = {'always_visible': True}
                            )]),  

                    html.Div(["Hospital Capacity: ",
                            dcc.Input(id='hcap', value=1000000, type='number')])
                    ],
                id="collapse",
                ),

                dbc.Button(
                    "Proportion Inputs",
                    id="collapse-button-p",
                    className="mb-3",
                    color="primary",
                ),
                dbc.Collapse(
                    [html.Div([html.H6('Contained'),
                            dcc.Slider(id='slider-pcont',min = 0, max = 1, value = 0.1, step = 0.05, tooltip = {'always_visible': True}
                            )]),

                    html.Div([html.H6('Quarantined'),
                            dcc.Slider(id='slider-pquar',min = 0, max = 1, value = 0.7, step = 0.05, tooltip = {'always_visible': True}
                            )]),  

                    html.Div([html.H6('Cross-Contamination'),
                            dcc.Slider(id='slider-pcross',min = 0, max = 1, value = 0.01, step = 0.01, tooltip = {'always_visible': True}
                            )]),  

                    html.Div([html.H6('Quarantined & Hospitalised'),
                            dcc.Slider(id='slider-pqhsp',min = 0, max = 1, value = 0.01, step = 0.01, tooltip = {'always_visible': True}
                            )]),  

                    html.Div([html.H6('Media Impact'),
                            dcc.Slider(id='slider-pj',min = 0, max = 1, value = 0.1, step = 0.05, tooltip = {'always_visible': True}
                            )]),  

                    html.Div([html.H6('Hospitalisation'),
                            dcc.Slider(id='slider-ph',min = 0, max = 1, value = 0.5, step = 0.05, tooltip = {'always_visible': True}
                            )]),  

                    html.Div([html.H6('Critical'),
                            dcc.Slider(id='slider-pc',min = 0, max = 1, value = 0.75, step = 0.05, tooltip = {'always_visible': True}
                            )]),  

                    html.Div([html.H6('Deceased'),
                            dcc.Slider(id='slider-pf',min = 0, max = 1, value = 0.5, step = 0.05, tooltip = {'always_visible': True}
                            )]),  
                    ],
                id="collapse-p",
                ),

                dbc.Button(
                    "Time Inputs",
                    id="collapse-button-t",
                    className="mb-3",
                    color="primary",
                ),
                dbc.Collapse(
                    [html.Div([html.H6('Incubated'),
                            dcc.Slider(id='slider-tinc',min = 2.5, max = 5, value = 3, step = 0.1, tooltip = {'always_visible': True}
                            )]),

                    html.Div([html.H6('Infectious'),
                            dcc.Slider(id='slider-tinf',min = 5.0, max = 7, value = 6, step = 0.1, tooltip = {'always_visible': True}
                            )]),  

                    html.Div([html.H6('Intensive Care'),
                            dcc.Slider(id='slider-ticu',min = 10.0, max = 14, value = 10, step = 0.1, tooltip = {'always_visible': True}
                            )]),  

                    html.Div([html.H6('Hospitalised'),
                            dcc.Slider(id='slider-thsp',min = 5.0, max = 10, value = 6, step = 0.1, tooltip = {'always_visible': True}
                            )]),  
                    html.Div([html.H6('Critical'),
                            dcc.Slider(id='slider-tcrt',min = 10.0, max = 14, value = 10, step = 0.1, tooltip = {'always_visible': True}
                            )]),  

                    html.Div([html.H6('Self-Recovery'),
                            dcc.Slider(id='slider-trec',min = 12.0, max = 14, value = 13, step = 0.1, tooltip = {'always_visible': True}
                            )]),  

                    html.Div([html.H6('Quarantine'),
                            dcc.Slider(id='slider-tqar',min = 4, max = 21, value = 21, step = 0.1, tooltip = {'always_visible': True}
                            )]),  

                    html.Div([html.H6('Quarantined & Hospitalised'),
                            dcc.Slider(id='slider-tqah',min = 0, max = 5, value = 2, step = 0.1, tooltip = {'always_visible': True}
                            )]),  
                    ],
                id="collapse-t",
                ),
            ]
        ),
        # Cái output plot nhé
        dcc.Graph(id='my-output'),
        html.Div(id='my-output2'),

    ])
])

# Mỗi cái callback sẽ lấy 1 số input và show 1 số output. Cái function ngay dưới sẽ đc gọi khi Input có thay đổi
# Này là call back của cái collapsible, lấy trên mạng
@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-p", "is_open"),
    [Input("collapse-button-p", "n_clicks")],
    [State("collapse-p", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-t", "is_open"),
    [Input("collapse-button-t", "n_clicks")],
    [State("collapse-t", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# Mỗi cái callback sẽ lấy 1 số input và show 1 số output. Cái function ngay dưới sẽ đc gọi khi Input có thay đổi
# Ví dụ như callback này lấy 3 cái input và show 1 cái graph
# Đặt tên function argument t cũng chả biết ntn, mà có vẻ như là lấy theo thứ tự Input.
@app.callback(
    # Argument 1 là id của component, Argument 2 là type
    Output('my-output', 'figure'),
    Input('slider-N', component_property='value'),
    Input('slider-r0', component_property='value'),
    Input('hcap', component_property='value'),

    Input('slider-tinc', component_property='value'),
    Input('slider-tinf', component_property='value'),
    Input('slider-ticu', component_property='value'),
    Input('slider-thsp', component_property='value'),
    Input('slider-tcrt', component_property='value'),
    Input('slider-trec', component_property='value'),
    Input('slider-tqar', component_property='value'),
    Input('slider-tqah', component_property='value'),

    Input('slider-pcont', component_property='value'),
    Input('slider-pquar', component_property='value'),
    Input('slider-pcross', component_property='value'),
    Input('slider-pqhsp', component_property='value'),
    Input('slider-pj', component_property='value'),
    Input('slider-ph', component_property='value'),
    Input('slider-pc', component_property='value'),
    Input('slider-pf', component_property='value'),
    
    )
# Function này để m muốn làm gì input để nó ra output thì ghi vô. Nãy type là 'figure' thì m phải trả 1 cái Figure object
def update_graph(N,r0,hcap, 
            tinf, tinc, thsp, tcrt, 
            ticu, tqar, tqah, trec, 
            pcont, pquar, pcross, pqhsp,  
            pj, ph, pc, pf):

    args = (r0, 
            tinf, tinc, thsp, tcrt, 
            ticu, tqar, tqah, trec, 
            pj, pquar, pqhsp, pcross, 
            ph, pc, pf, pcont)

    n_infected=1
    initial_state = [(N - n_infected)/ N, 0, n_infected/N, 0, 0, 0, 0, 0, 0]

    sol = solve_ivp(SEIQHCDRO_model, [0, 150], \
                        initial_state, args=args, \
                        t_eval=np.arange(151), method = "Radau")
    S, E, I, Q, H, C, D, R, O = sol.y
    # SEIQHCDRO_plot(sol_blind, 'SEIQHCDRO, nationwide, intervention 80 % on day 20, R0 = 4.6')

    x = np.linspace(0,150,151)
    fig = make_subplots(rows=3, cols=3)#go.Figure()
    # Add nhiều plot vô 1 fig thì fig.add_trace(), argument 'name' là để bỏ tên vô legend
    fig.add_trace(go.Scatter(x=x,y=hcap*np.ones(151), name = 'Hospital Capacity'),row=1, col=2)
    # fig.add_trace(go.Scatter(x=x,y=n/r0*np.ones(100), name = 'n/r0'),row=1, col=1)
    # fig.add_trace(go.Scatter(x=x,y=np.array([math.exp(-pq*t) for t in x]), name = 'e^{-p_quar*t}'),row=1, col=2)
    hsp = np.round((H + C + D + R) * N)
    fig.add_trace(go.Scatter(x=x,y=np.round((I + H + C + D + R + O) * N), name = 'Infected'),row=1, col=1)
    fig.add_trace(go.Scatter(x=x,y=hsp, name = 'Hospitalised'),row=1, col=2)
    fig.add_trace(go.Scatter(x=x,y=np.round((H + R) * N), name = 'Non-critical Hospitalised'),row=1, col=3)
    fig.add_trace(go.Scatter(x=x,y=np.round((C + D) * N), name = 'Critical'),row=2, col=1)
    fig.add_trace(go.Scatter(x=x,y=np.round(D * N), name = 'Deaths'),row=2, col=2)
    fig.add_trace(go.Scatter(x=x,y=np.round((I + O) * N), name = 'Undiscovered Cases'),row=2, col=3)
    fig.add_trace(go.Scatter(x=x,y=np.round(Q*N), name = 'Daily Quarantined'),row=3, col=1)
    fig.add_trace(go.Scatter(x=x,y=np.array([hsp[i+1]-hsp[i] for i in range(150)]), name = 'Daily Hospital Incidence'),row=3, col=2)
    fig.add_trace(go.Scatter(x=x,y=np.round((E+Q)*N), name = 'Daily Exposed'),row=3, col=3)
    fig.update_layout(
        title={
            'text': "Prediction of Different COVID Scenarios in Vietnam",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
    )
    return fig

@app.callback(
    Output('my-output2', 'children'),
    Input('slider-pquar', component_property='value'),
    Input('slider-pcross', component_property='value'),
    Input('slider-pqhsp', component_property='value'),
    Input('slider-pj', component_property='value'),
    Input('slider-ph', component_property='value'),
    Input('slider-pc', component_property='value'),
    Input('slider-pf', component_property='value'),
)
def update_output_div(pquar,pcross,pqhsp,pj,ph,pc,pf):
    return f'Output: {pj}, {ph}, {pc}, {pf}'

def SEIQHCDRO_model(t, y, R_0, T_inf, T_inc, T_hsp, T_crt, T_icu, T_quar, T_quar_hosp, T_rec, p_h, p_c, p_f, p_cont, p_jrnl, p_quar, p_quar_hosp, p_cross_cont):
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

    # if condition in case R_0 is a callable function wrt time
    
    """
    def R0_dynamic(t):
        if t <= 22:
            return 4.3 * 0.8   
        elif 22 < t <= 34:
            return 4.3 * (1 - 0.5) * (1 - 1/16) - 1/31 * t * 0.5 
            # 4.4*0.6 - t/31
        elif 34 < t <= 41:
            return 4.3 * (1 - 0.5) * (1 - 1/16) - 1/31 * t * 0.5
            # 4.4 * 0.4 - t/31
        else:
            return max(4.3 * (1 - 0.8) * (1 - 1/16) - 1/31 * t * 0.8, 0)
            # max(4.4*0.3 - t/31,0) 
    """
    
    if callable(R_0):
        def R0_dynamic(t): return R_0(t)
    else:
        def R0_dynamic(t): return R_0

    S, E, I, Q, H, C, D, R, O = y

    dS_dt = - R0_dynamic(t) * (1 / T_inf + (1 - p_h) / T_rec) * I * S
    dE_dt = R0_dynamic(t) * (1 / T_inf + (1 - p_h) / T_rec) * I * S - 1 / T_inc * E - p_quar * (E) / T_quar
    dI_dt = 1 / T_inc * E - (p_h / T_inf + (1 - p_h) / T_rec) * I
    dQ_dt = p_quar * (E) / T_quar - (p_quar_hosp + p_cross_cont) * Q / T_quar_hosp
    dH_dt = p_h / T_inf * I - (1 - p_c) / T_hsp * H - p_c / T_crt * H - p_h / T_rec * H + (p_quar_hosp + p_cross_cont) * Q / T_quar_hosp
    dC_dt = p_c / T_crt * H - C / (T_icu + T_crt)
    dD_dt = p_f / (T_icu + T_crt) * C
    dR_dt = (1 - p_c) / T_hsp * H + (1 - p_f) / (T_icu + T_crt) * C 
    dO_dt = (1 - p_h) / T_rec * I + p_h / T_rec * H
    
    dy_dt = [dS_dt, dE_dt, dI_dt, dQ_dt, dH_dt, dC_dt, dD_dt, dR_dt, dO_dt]
    return dy_dt

# Cái này để chạy sv thôi, k cần sửa gì
if __name__ == '__main__':
    app.run_server(debug=True)