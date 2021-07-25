"""
Main application script.
"""

# Local Library
import sample

# 3rd-party
import json
import base64
import io
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

# Header
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets, 
                title='COVID-19 Modelling with SEIQHCDRO',
                suppress_callback_exceptions = True)
server = app.server

# Some frequently used CSS across different HTML elements
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

# Overall page layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Navbar([
        # Use row and col to control vertical alignment of logo / brand
        dbc.Row(
            [
                dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                dbc.Col(dbc.NavbarBrand("COVID-19 modelling with SEIQHCDRO", className="ml-2",style={'font-size':'20px', 'vertical-align':'center'})),
                dbc.Col(dbc.NavLink("Home", href="/",className='text-light font-weight-bold',style={'font-size':'15px', 'vertical-align':'center'})),
                dbc.Col(dbc.NavLink("About", href="/about",className='text-light font-weight-bold',style={'font-size':'15px', 'vertical-align':'center'}))
            ],
            align="center",
            no_gutters=True,
        ),
    ],color="dark",dark=True,
    style={'text-decoration':'none','color':'white'}),
    html.Div(id='page-content'),
    html.Footer([
                u'Copyright \u00a92021 SEIQHCDRO COVID-19 Interactive Modelling Tool by Hoang Anh NGO, Tuan-Khoi NGUYEN and Thu-Anh NGUYEN',
                html.Div(['Visitors: ',html.Img(src="https://counter2.stat.ovh/private/freecounterstat.php?c=xj7lgw2xsbsyk917b5wrbr45ldmx56u6", style={'width':'12%'})], style={'width': '100%','text-align': 'center','margin':'1% 0 0 0'}),
                ],style={'width':'100%', 
                       'text-align':'center',
                       #'border-style':'outset',
                       'background-color':'#343a40',
                       'padding':'2%'})
])

# About page
about_page = html.Div([
                    dcc.Markdown(
                        u'''
                        #### SEIQHCDRO COVID-19 <br> INTERACTIVE MODELLING TOOL
                        
                        # Introduction
                        
                        In the past outbreaks, Vietnam has successfully controlled the COVID-19 pandemic by simultaneously applying numerous strategies,
                        including aggressive contact tracing, mandatory quarantine, routine testing, etc. To quantify the effectiveness of these measures,
                        we developed a multi-compartment model that integrates all of these practices to estimate impacts of possible mitigation scenarios
                        on the COVID-19 outbreak. To do that, we extended the traditional SEIR model into a 9-compartment model SEIQHCDRO with 
                        S (Susceptible), E (Exposed), I (Infected), Q (Quarantined), H (Hospitalized), C (Critical), D (Death), R (Recovered) 
                        and O (Other - Recovered). 
                        
                        Moreover, in order to turn our research 
                        into an open-source project so that everyone can have access to, while creating a tool so that policy makers/public health specialists have a
                        tool to facilitate their policy advocate/policy making process, we decided to create this tool, alongside with publicizing all associated
                        source code.
                        
                        # Formation of the model 
                        
                        ## Model Flowchart
                        
                        As an multi-compartment epidemiological model, there must exist specific relations between each and every single compartment. 
                        Such relations are expressed though the model flowchart below
                        
                        
                        '''
                    ,dangerously_allow_html=True),
                    html.Div([html.Img(src="https://drive.google.com/uc?export=view&id=1nb9DFzmOBdlbp8eSaMUsKA45owrYauf_", style={'width': '50%', 'fill':'#000'})], style={'width': '100%','text-align': 'center'}),
            dcc.Markdown(
                        '''
                        ## Formula
    
                        From this, we develop a system of differential equations to simulate the relationship between these compartments. The system reads:
                        '''
            ),
             html.Div([html.Img(src="https://quicklatex.com/cache3/2e/ql_5948b14b283613968f0b24fb80533a2e_l3.png",
                                style={'width': '40%', 'fill': '#000'})],
                      style={'width': '100%', 'text-align': 'center'}),
             dcc.Markdown(
                 '''
                 with two main types of hyper-parameters
                 * Proportion-related hyper-parameters `p`;
                 * Time interval related hyperparameters `T`.

                 To obtain the result, this system of ordinary differential equations (ODEs) will be solved using the `solve_ivp` command within the `SciPy` package
                 in Python. To prevent any stiffness of the system, the `Radau` method, i.e the implicit Runge-Kutta method of the Radau IIA family of order 5.

                 ## Formulation of the basic reproduction number `R_0`

                 One of the most important aspects of this model is the ability to capture different levels of social distancing/lockdown to the spread
                 of the disease. As such, we have integrated these impacts onto the function representing the effective reproduction number `R_t` (i.e the basic reproduction
                 number `R_0` with respect to time).
                 '''
             ),
             html.Div([html.Img(src="https://quicklatex.com/cache3/f7/ql_580fe4eb71ceadb277d725dd86ca49f7_l3.png",
                                style={'width': '15%', 'fill': '#000'})],
                      style={'width': '100%', 'text-align': 'center'}),
             dcc.Markdown(
                 '''
                 Assume that there exists two consecutive time intervals separated by a policy scheme change at time `T`. Before time `T`, the population
                 inherits a scheme with change of the basic reproduction number `delta R_0`, contact rate reduction `p_cont` and contact rate reduction due
                 to journalism `p_jrnl`. After time `T`, the population now inherits a new scheme with a new set of parameters, `delta R'_0`, `p'_cont` and 
                 `p'_jrnl`, respectively.

                 There are two cases that would happen:

                 * When `p'_cont >= p_cont` (i.e. the social distancing/lockdown measure tightens), the new function is:
                 '''
             ),
             html.Div([html.Img(src="https://quicklatex.com/cache3/9e/ql_11ac62405647900135857d3b2d429b9e_l3.png",
                                style={'width': '40%', 'fill': '#000'})],
                      style={'width': '100%', 'text-align': 'center'}),
             dcc.Markdown(
                 '''
                 * When `p'_cont < p_cont` (i.e. the social distancing/lockdown measure loosens), the function now becomes:
                 '''
             ),
             html.Div([html.Img(src="https://quicklatex.com/cache3/84/ql_1a46c5cd376b5ef2c5fa51f23f675484_l3.png",
                                style={'width': '40%', 'fill': '#000'})],
                      style={'width': '100%', 'text-align': 'center'}),
             dcc.Markdown(
                 '''
                        # Tool features
                        
                        ## Modelling features
                        
                        In order to create the most interactive and convenient tool possible for COVID-19 modelling, we have decided to opt for 
                        a number of features that makes it more comfortable for users to interact with this web application, including
                        * The ability to capture 10 different policy schemes in place, corresponding to 10 consecutive time intervals. This would
                        be helpful for policy advocates to simulate effects of different policy making processes.
                        * 3 pairs of plots representing different aspect of the outbreak with built-in gadgets of `Plotly` for generated plots, including:
                            - **Overall trend of infection**: Incidence and cumulative number of hospitalized/infected COVID-19 cases,
                            - **Critical and fatal cases**: Number of active critical cases daily and cumulative number of deceased cases,
                            - **Spread and containment**: Effective reproduction number (Basic reproduction number by day) and total number of quarantined individuals.  
                        * Ability to export all statistical data of a newly calibrated model in a personalized file name, including
                            - Information summary of the model (in either a .txt file or a .json file for further uploading and re-calibration); 
                            - Total hospitalized/infected/critical/fatal cases in a single CSV file.
                        * Comparision with the current capacity for the number of quarantined/hospitalized cases
                        
                        ## Cross-checking and testing features
                        
                        To facilitate the validation and cross-checking of models between users, we provide the following additional features:
                        * Samples .json files of the previous outbreaks in Vietnam, including the outbreaks in 
                            - Danang (07-08/2020);
                            - Hai Duong (01-03/2021); 
                            - Bac Giang (05-07/2021); and 
                            - Ho Chi Minh (05/2021 onwards) with 3 scenarios: best, moderate and worst.
                        * Import (Upload) a .json file that includes all information of the previously calibrated model to continue further moedification 
                            without having to restart the whole process from the beginning;
                        * Upload a csv file of the actual situation and illustrate it alongside with the prediction model. The uploaded csv file can include 
                            up to 5 following fields:   
                            - Number of new (incidence) cases per day (`daily_infected`);
                            - Total (cumulative) number of cases (`cumulative_infected`);
                            - Number of active critical cases (`active_critical`);
                            - Total (cumulative) number of deaths (`cumulative_deaths`);
                            - Number of active quarantined individuals (`active_quarantined`). 
                            
                        '''
                    ),
                    dcc.Markdown(
                    '''
                    # Mentions
                    
                    Up until now, our research project has been featured at two major conferences in lung health, public health and epidemiology, including:
                    - [The 52nd World Union Conference on Lung Health](https://theunion.org/our-work/conferences/52nd-union-world-conference-on-lung-health?fbclid=IwAR3DAw1R3eA8L0Jv0cr0aUtoqFJwESIHNvdGCyBKzkPF5KFbsUcXTOOK-ZM);
                    - [8th Vietnam Lung Association (VILA) Scientific Conference 2021](https://drive.google.com/file/d/10uBQJATgEIVgIAbQdp9n4oWGGYqOiKf-/view?fbclid=IwAR3bNTaz_4UKZxa2TaN5ge6FSJL88vURX7xzFURjkE0J-B4hxuKT_3ZZ3vQ).
                    
                    Moreover, we also have a Markdown version ready for submission to Journal of Open Source Software. This can be found at the associated 
                    [paper.md](https://github.com/tuankhoin/SEIQHCDRO-Interactive-Model/blob/main/paper.md) file within this repository.
                    
                    Besides, our research has also been featured on a lot of renowned newspapers in Vietnam, including Tuoi tre, VNExpress, Soha, Viet Nam News, etc. as a major tool 
                    for our policy advocates to fight against the COVID-19 pandemic in Vietnam.
                    
                    # Citation

                    If SEIQHCDRO multi-compartment model in general or the interactive modelling website has been useful for your research and policy advocacy, and you would like to cite it in an scientific publication, please refer to our presentation at the **52nd Union World Conference on Lung Health** as follows:
                    '''
                    ),
                    dcc.Markdown(
                    '''
                    ```json
                    @misc{
                        author = {Hoang Anh NGO and Tuan-Khoi NGUYEN and Thu-Anh NGUYEN},
                        title = {A novel compartment model for analyzing and predicting COVID-19 outbreaks in Vietnam},
                        howpublished = {Oral presentation at the 52nd Union World Conference on Lung Health}
                        year = {2021},
                        month = {October},
                        date = {19--22}
                    }
                    ```
                    '''
                ,
                ),
                    dcc.Markdown(
                        '''
                        # About the authors
                
                        * [**Hoang Anh NGO**](https://orcid.org/0000-0002-7583-753X) is the main author and model developer of the project. He is about to graduate from École Polytechnique
                        with a double major in Mathematics and Economics, minor in Computational Economics. He is also currently a Research Contractor at Woolcock Institute of Medical Research
                        Vietnam. His research interests focus on Epidemiology, (Online) Machine Learning and its applications in Medicine.
                        * [**Tuan-Khoi Nguyen**](https://tkhoinguyen.netlify.app/) is the data engineer and main web developer of this project. He is graduating from The University of
                        Melbourne with a Bachelor of Science in Mechatronics, and about to continue his Masters within the same field. His research
                        interest focuses on Machine Learning and its applications in Robotics.
                        * Dr [**Nguyen Thu Anh**](https://www.researchgate.net/profile/Nguyen-Anh-50) is an epidemiologist and a social scientist by training, with more than 20 years of experience. 
                        She holds an honorary position as Senior Clinical Lecturer at University of Sydney, and the head of the 
                        Woolcock Institute of Medical Research in Vietnam.
                
                        '''
                    ),
                    dcc.Markdown(
                        '''
                        # Acknowledgement
                        
                        We would like to send our sincerest gratitude towards all team members of [5F Team](https://5fteam.com/) for contributing 
                        valuable insights and data to help us complete out model:
                        
                        * BPharm. Duyen T. Duong, Woolcock Institute of Medical Research Vietnam
                        * MS. Thao Huong Nguyen, Independent Social Researcher
                        * Kim Anh Le, MD PhD, Hanoi University of Public Health
                        * Cuong Quoc Nguyen, MD PhD, Independent Epidemiologist
                        * Phuc Phan, MD PhD, Vietnam National Hospital of Pediatrics 
                        * Nguyen Huyen Nguyen, MD, National Hospital of Tropical Diseases (NHTD)
                        
                        Moreover, we also want to send our warmest thanks to our fellow 
                        colleagues and readers for their thoughtful and scholarly evaluation of the model. 
                        All comments are hugely appreciated.
                        
                        '''
                    ),
                    dcc.Markdown(
                        '''
                        # License 
                        SEIQHCDRO COVID-19 Interactive Modelling Tool is a free and open-source web application/software licensed under the 
                        [3-clause BSD license](https://github.com/tuankhoin/SEIQHCDRO-Interactive-Model/blob/main/LICENSE).
                        
                        ## Authorship & Contribution
                            - Based on the license, this is a free software/web application released by the authors. There is no relation between the application and authors' affiliations.
                            - For support, please write an issue in the [issue tracker of this project](https://github.com/tuankhoin/SEIQHCDRO-Interactive-Model/issues).
                            - For contribution, please fork and make a pull request.
                        
                        # Website legal disclaimer
                        The information contained in this website is for convenience or reference only. The content cannot be considered to be medical advice and is not intended 
                        to be a substitute for professional medical counselling, diagnosis or treatment. For any concern please consult a trusted specialist in the field.

                        Whilst we endeavor to keep the information up to date and correct, we make no representations or warranties of any kind, express or implied, 
                        about the completeness, accuracy, timeliness, reliability, suitability or availability with respect to the website or the information, 
                        products, services, or related graphics, images, text and all other materials contained on the website for any purpose. 
                        It is not meant to be applicable to any specific individual’s medical condition and any reliance you place on such information is therefore 
                        strictly at your own risk.

                        In no event will we be liable for any loss or damage including without limitation, indirect or consequential loss or damage, or any loss or damage whatsoever 
                        arising from loss of data or profits arising out of, or in connection with, the use of this website.
                        '''
                    )
                ],
                style = {'margin':'5%'})


def generate_inputs():
    r"""
    Generate the basic input slots and stages for the main page.

    Returns
    -------
    widgets : :class:`list`
        A list of HTML Elements for the basic stage inputs.
    """
    num_slider = [
                    html.Div([html.H3('Number of Stages:'),
                            dbc.Tooltip(
                                "Number of main representative stages during the pandemic",
                                target="div-num", placement='right'
                            ),
                            dcc.Input(id='num', min=0, max=30, value=3, step=1,
                                    type='number'#tooltip={'always_visible': True}
                                    )],id='div-num')
                  ]
    
    text_boxes = [html.H3('Stage Inputs'),
                  html.Div(id='in-r0'),
                  dbc.Tooltip(
                      html.Ul([
                          html.H6("Excluding the default first stage with zero reduction, each stage contains the following:"),
                          html.Li("Starting date"),
                          html.Li("Assumed reduction rate within 15 days when 100% containment scheme is in place "),
                          html.Li("Contained proportion due to new policy scheme")],style={'text-align':'left'}),
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

# Main page
main_page = html.Div([
    html.Div([
        html.Div([html.H1("COVID-19 Multi-compartment Modelling Result".upper())],style={'width':'100%','text-align':'center','padding':'1%'}),

        # Inputs
        html.Div(
            [
                # Basic inputs
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
                                    "Population taken into account",
                                    target="div-N", placement='right'
                               ),
                               dcc.Slider(id='slider-N', min=100000, max=100000000, value=11000000, step=1000,
                                          tooltip={'always_visible': True, 'placement':'top'},
                                          marks = {i: str(i) for i in [100000, 50000000,100000000]}
                                          )],id='div-N'),

                    html.Div([html.H3('Outbreak Date'),
                               dbc.Tooltip(
                                    "Assumed first day of outbreak",
                                    target="div-date", placement='right'
                               ),
                                dcc.DatePickerSingle(
                                    id='date',
                                    min_date_allowed=date(2020, 1, 1),
                                    max_date_allowed=date(2030, 12, 31),
                                    initial_visible_month=date(2021, 5, 1),
                                    date=date(2021, 5, 1),
                                    display_format = 'DD/MM/YYYY'
                                ),
                    ], id = 'div-date'),

                    html.Div([html.H3('Number of Days'),
                               dbc.Tooltip(
                                    "Length of outbreak",
                                    target="div-ndate", placement='right'
                               ),
                                dcc.Input(id='ndate', value=300, min=10, max=1000, type='number')
                    ], id = 'div-ndate'),

                     html.Div([html.H3("Hospital Capacity: "),
                               dbc.Tooltip(
                                    "Hospital Capacity",
                                    target="div-hcap", placement='right'
                               ),
                               dcc.Input(id='hcap', value=100000, type='number')], style={'margin':'4% 0%'},id='div-hcap'),

                     html.Div([html.H3("Quarantine Capacity: "),
                               dbc.Tooltip(
                                    "Quarantine Capacity",
                                    target="div-qar", placement='right'
                               ),
                               dcc.Input(id='hqar', value=10000, type='number')], style={'margin':'4% 0%'},id='div-qar'),

                     html.Div([html.H3('Initial basic reproduction number (R0):'),
                               dbc.Tooltip(
                                    "Initial basic reproduction number at first day of outbreak",
                                    target="div-r0", placement='right'
                               ),
                               dcc.Input(id='slider-r0', min=0, max=20, value=4.1, step=0.001,
                                          type='number'#tooltip={'always_visible': True}
                                          )],id='div-r0'),

                     html.Div(generate_inputs()),
                    

                     ],
                    id="collapse",
                    style = tab
                ),

                # Proportional inputs
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
                                    "Proportion of infected people getting hospitalized (For example, if 100 positive cases exist in the community, this proportion of them would be directly sent to a hospital).",
                                    target="div-ph", placement='right'
                               ),
                               dcc.Slider(id='slider-ph', min=0, max=1, value=0.85, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-ph'),

                     html.Div([html.H6('Critical'),
                               dbc.Tooltip(
                                    "Proportion of COVID-19 positive hospitalized patients turning critical.",
                                    target="div-pc", placement='right'
                               ),
                               dcc.Slider(id='slider-pc', min=0, max=1, value=0.04, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-pc'),

                     html.Div([html.H6('Deceased'),
                               dbc.Tooltip(
                                    "Proportion of COVID-19 positive critical patients deceased.",
                                    target="div-pf", placement='right'
                               ),
                               dcc.Slider(id='slider-pf', min=0, max=1, value=0.25, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-pf'),

                     html.Div([html.H6('Media Impact'),
                               dbc.Tooltip(
                                    "Media Impact as a contact reduction rate on the reproduction number.",
                                    target="div-pj", placement='right'
                               ),
                               dcc.Slider(id='slider-pj', min=0, max=1, value=0.12, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-pj'),

                     html.Div([html.H6('Quarantined'),
                               dbc.Tooltip(
                                    "Proportion of contact cases who requires quarantined actually get quarantined upon contact tracing (For example, if 100 contact cases need quarantine, this proportion of them would get quarantined immediately).",
                                    target="div-pquar", placement='right'
                               ),
                               dcc.Slider(id='slider-pquar', min=0, max=1, value=0.8, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-pquar'),

                     html.Div([html.H6('Quarantined, then Hospitalised'),
                               dbc.Tooltip(
                                    "Proportion of individuals quarantined for a long duration of time before getting positive result and hospitalized.",
                                    target="div-pqhsp", placement='right'
                               ),
                               dcc.Slider(id='slider-pqhsp', min=0, max=1, value=0.1, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-pqhsp'),

                     html.Div([html.H6('Cross-Contamination'),
                               dbc.Tooltip(
                                    "Cross-contamination rate in quarantine facilities.",
                                    target="div-pcross", placement='right'
                               ),
                               dcc.Slider(id='slider-pcross', min=0, max=1, value=0.01, step=0.01,
                                          tooltip={'always_visible': True}
                                          )],id='div-pcross'),
                     ],
                    id="collapse-p",
                    style = tab
                ),

                # Timing inputs
                dbc.Button(
                    html.H2("Time Inputs"),
                    id="collapse-button-t",
                    className="mb-3",
                    color="danger",
                    style={'width':'100%'}
                ),
                dbc.Collapse(
                    [html.Div([html.H6('Incubation'),
                               dbc.Tooltip(
                                    "Incubation period.",
                                    target="div-tinc", placement='right'
                               ),
                               dcc.Slider(id='slider-tinc', min=2.5, max=7, value=4.5, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-tinc'),

                     html.Div([html.H6('Infectious'),
                               dbc.Tooltip(
                                    "Infectious period.",
                                    target="div-tinf", placement='right'
                               ),
                               dcc.Slider(id='slider-tinf', min=1.0, max=7, value=2.9, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-tinf'),

                     html.Div([html.H6('Intensive Care'),
                               dbc.Tooltip(
                                    "Time spent within the ICU.",
                                    target="div-ticu", placement='right'
                               ),
                               dcc.Slider(id='slider-ticu', min=10.0, max=14, value=11, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-ticu'),

                     html.Div([html.H6('Hospitalised'),
                               dbc.Tooltip(
                                    "Time spent hospitalised for non-critical patients.",
                                    target="div-thsp", placement='right'
                               ),
                               dcc.Slider(id='slider-thsp', min=7, max=21, value=21, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-thsp'),
                     html.Div([html.H6('Critical'),
                               dbc.Tooltip(
                                    "Time spent hospitalized before turning critical.",
                                    target="div-tcrt", placement='right'
                               ),
                               dcc.Slider(id='slider-tcrt', min=1, max=14, value=7, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-tcrt'),

                     html.Div([html.H6('Self-Recovery'),
                               dbc.Tooltip(
                                    "Self-Recovery time for non-disclosed cases.",
                                    target="div-trec", placement='right'
                               ),
                               dcc.Slider(id='slider-trec', min=7, max=21, value=21, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-trec'),

                     html.Div([html.H6('Quarantine'),
                               dbc.Tooltip(
                                    "Quarantine time under regulation.",
                                    target="div-tqar", placement='right'
                               ),
                               dcc.Slider(id='slider-tqar', min=4, max=21, value=21, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-tqar'),

                     html.Div([html.H6('Quarantined, then Hospitalised'),
                               dbc.Tooltip(
                                    "Time interval between the last COVID-19 positive result until getting hospitalized.",
                                    target="div-tqah", placement='right'
                               ),
                               dcc.Slider(id='slider-tqah', min=0, max=5, value=2, step=0.1,
                                          tooltip={'always_visible': True}
                                          )],id='div-tqah'),
                     ],
                    id="collapse-t",
                    style = tab
                ),

            # Input uploader
            html.Div([
                dcc.Upload(html.Button([u'\f Upload custom .json input file'], style={'color':'white','margin':'2% 0', 'width':'100%'}),
                        id='up', style={'padding':'2% 0', 'font-style':'bold'}),
                dbc.Tooltip(
                        "You can import your json file that you have exported previously, rather than having to readjust inputs all over again",
                        target="div-up", placement='right'
                    ),
            ],id='div-up'),
            html.Div([
                dcc.Upload(html.Button([u'\f Upload .csv stats for comparing'], style={'color':'white','margin':'2% 0', 'width':'100%'}),
                        id='up_stat', style={'padding':'0% 0', 'font-style':'bold'}),
                dbc.Tooltip(
                        html.Ul([
                            html.H6("You can upload a csv file of real statistics to compare. The device will find any matching columns and add them to the plot for comparison (assuming 1st row is 1st day of outbreak). The following column names can be selected:"),
                            html.Li("infected"),
                            html.Li("daily_infected"),
                            html.Li("active_critical"),
                            html.Li("active_quarantined"),
                            html.Li("deaths"),
                            ],style={'text-align':'left'}),
                        target="div-up-stat", placement='right'
                    ),
                html.P(id='err', style={'color': 'red'}),
            ],id='div-up-stat')
            ]
        ,style = {'width':'33%', 'display':'inline-block', 'vertical-align':'top', 'padding':'2%'}),
        
        # Output
        html.Div([
            # Modes and sample picker
            html.Div([
                      dcc.Checklist(
                            options=[
                                {'label': 'Show Hospital Capacity', 'value': 1},
                                {'label': 'Show Quarantine Capacity', 'value': 3},
                                {'label': 'Show by Date', 'value': 2}
                            ],
                            value=[],
                            labelStyle={'display': 'block'},
                            id='mods'
                        )
                    ], style={'padding':'0% 3%','display':'inline-block','width':'35%'}),
            html.Div([
                      dcc.Dropdown(
                            options=[
                                {'label': sample.name[n], 'value': n} for n in sample.name.keys()
                            ],
                            placeholder='Select an example region',
                            id='init'
                        )
                    ], style={'padding':'0% 3%','display':'inline-block','width':'55%'}),
            
            # Plots
            html.Div([dcc.Graph(id='overall-plot'),], style={'vertical-align':'top', 'border-style':'outset', 'margin':'1% 0%'}),
            html.Div([dcc.Graph(id='fatal-plot'),], style={'vertical-align':'top', 'border-style':'outset', 'margin':'1% 0%'}),
            html.Div([dcc.Graph(id='r0-plot'),], style={'vertical-align':'top', 'border-style':'outset', 'margin':'1% 0%'}),
            
            # File downloader
            html.Div([html.Div(
                            [
                                html.H2("Download Statistics"),
                                dcc.Input(id='file', value='',
                                          type='text', placeholder='Specify exported file name (default: ''exported_stats'')',
                                          style = {'width':'100%'}),
                                html.Button("Statistics Data (.csv)", id="btn_csv", style={'color':'white','margin':'2%'}),
                                dcc.Download(id="download-dataframe-csv"),
                                html.Button("Information Summary (.txt)", id="btn_sum", style={'color':'white','margin':'2%'}),
                                dcc.Download(id="download-sum"),
                                html.Button("Export Inputs (.json)", id="btn_ipt", style={'color':'white','margin':'2%'}),
                                dcc.Download(id="download-ipt"),
                            ], style={'padding':'2% 3%','display':'inline-block', 'vertical-align':'bottom','text-align':'center', 'width':'100%'}
                        ),    
            ], style={'vertical-align':'top', 'border-style':'outset', 'margin':'1% 0%'}),
                
        ],
        style = {'width':'66%', 'display':'inline-block', 'vertical-align':'top', 'margin':'1% 0%'}),
        

    ])
])


# Dynamically creating stage inputs 
@app.callback(
    Output('in-r0', 'children'),
    Input('init', 'value'),
    [Input('num', 'value')],
    [Input('up', 'contents')],
    State('up', 'filename'),
    )
def ins_generate(init,n,content,file):
    r"""
    Generate dynamic stage inputs based on number of stages, either from file or from input.
    Triggered when there is change in at least 1 variable.

    Parameters
    ----------
    init : `str`
        Chosen sample region.
    n : `int`
        Number of stages.
    content : `base64`
        File content, encoded to base64.
    file : `str`
        File name.

    Returns
    -------
    stages : :class:`list`
        A list of HTML Elements with pre-defined values for the stage inputs.
    """
    # Check which input is changing
    ctx = dash.callback_context.triggered
    current_call = [] if not ctx else ctx[0]['prop_id'].split('.')[0]

    # If it's only changing in irrelevant variables, set to default
    if (not file or 'up' not in current_call) and 'init' not in current_call:
        # Default values for up to 30 stages
        d = [6,20,30,49,55,60,69,70,80,85,90,95,100,105,110,115,120,125,130,135,140,145,145,145,145,145,145,145,145,145]
        dr = [1.5,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        pco = [0.1, 0.4, 0.6, 0.8,0.8,0.85,0.9, 0.9, 0.95, 1, 0.9, 0.9, 0.95, 1, 0.9, 0.9, 0.95, 1, 0.9, 0.9, 0.95, 1, 0.9, 0.9, 0.95, 1, 0.9, 0.9, 0.95, 1]
        return [html.Div([html.H5(f'Stage {i+1}:'),
                        html.Div([html.H6('Starting Date'), dcc.Input(id={'role':'day', 'index':i}, min=1, max=1000, value=d[i], step=1, type='number', style={'width':'80%'})],
                                    style={'width': '33%', 'display': 'inline-block'}),
                        html.Div([html.H6('R0 Reduction'), dcc.Input(id={'role':'r0', 'index':i}, value=dr[i], step=0.1, type='number', style={'width':'100%'})],
                                    style={'width': '28%', 'display': 'inline-block', 'margin':'0 5% 0 0'}),
                        html.Div([html.H6('Contained Proportion'), dcc.Slider(id={'role':'pcont', 'index':i}, min=0, max=1, value=pco[i], step=0.01, tooltip={'always_visible': False}, marks={0:'0',1:'1'})],
                                    style={'width': '33%', 'display': 'inline-block'})
                        ], style={'border-style':'outset', 'margin':'1%', 'padding': '1%'}) for i in range(n)]

    # Choosing which to change the stage inputs, by finding out the triggered component
    json_stage = ['delta_r0', 'pcont', 'day', 'n_r0']
    # If it's sample that is looked for, use the inputs from sample file
    if current_call=='init':
        jf = json.loads(sample.loc[init])
    # If it's a file, use the inputs from it
    else:
        _, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        jf = json.loads(decoded)

        # Handling wrong formatting cases

        # Irrelevant attributes
        for i in json_stage:
            if i not in jf:
                return dash.no_update
        # Inconsistent number of stage variables
        if len(jf['day']) != len(jf['delta_r0']) or len(jf['day']) != len(jf['pcont']):
            return dash.no_update

    return [html.Div([html.H5(f'Stage {i+1}:'),
                        html.Div([html.H6('Starting Date'), dcc.Input(id={'role':'day', 'index':i}, min=1, max=1000, value=jf['day'][i], step=1, type='number', style={'width':'80%'})],
                                    style={'width': '33%', 'display': 'inline-block'}),
                        html.Div([html.H6('R0 Reduction'), dcc.Input(id={'role':'r0', 'index':i}, value=jf['delta_r0'][i], step=0.1, type='number', style={'width':'100%'})],
                                    style={'width': '28%', 'display': 'inline-block', 'margin':'0 5% 0 0'}),
                        html.Div([html.H6('Contained Proportion'), dcc.Slider(id={'role':'pcont', 'index':i}, min=0, max=1, value=jf['pcont'][i], step=0.01, tooltip={'always_visible': False}, marks={0:'0',1:'1'})],
                                    style={'width': '33%', 'display': 'inline-block'})
                        ], style={'border-style':'outset', 'margin':'1%', 'padding': '1%'}) for i in range(jf['n_r0'])]

@app.callback(
    [Output(f"collapse{i}", "is_open") for i in ['','-p','-t']],
    [Input(f"collapse-button{i}", "n_clicks") for i in ['','-p','-t']],
    [State(f"collapse{i}", "is_open") for i in ['','-p','-t']],
)
def toggle_accordion(n1, n2, n3, is_open1, is_open2, is_open3):
    r"""
    Toggle Open/Close of input groups.

    Parameters
    ----------
    n1, n2, n3 : `int`
        Number of clicks made on a specified button.
    is_open1, is_open2, is_open3 : `bool`
        Boolean indicating ff collapsible in any group is open.

    Returns
    -------
    stage1, stage2, stage3 : :class:`bool`
        Corresponding responsive open state for each collapsible group.
    """
    ctx = dash.callback_context

    # Check if any group is being clicked on first, by detecting change in number of clicks
    if not ctx.triggered:
        return False, False, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # When a group is clicked, toggle its stage and close the others
    if button_id == "collapse-button" and n1:
        return not is_open1, False, False
    elif button_id == "collapse-button-p" and n2:
        return False, not is_open2, False
    elif button_id == "collapse-button-t" and n3:
        return False, False, not is_open3
    return False, False, False

@app.callback(
    Output('overall-plot', 'figure'),
    Output('fatal-plot', 'figure'),
    Output('r0-plot', 'figure'),
    Output("download-dataframe-csv", "data"),
    Output("download-sum", "data"),
    Output("download-ipt", "data"),
    Input('slider-N', component_property='value'),
    Input('num', 'value'),
    Input('slider-r0', component_property='value'),
    [Input({'role':'r0', 'index':ALL}, component_property='value')],
    [Input({'role':'pcont', 'index':ALL}, component_property='value')],
    [Input({'role':'day', 'index':ALL}, component_property='value')],
    Input('date', component_property='date'),
    Input('ndate', 'value'),
    Input('hcap', component_property='value'),
    Input('hqar', component_property='value'),
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
    Input("btn_ipt", "n_clicks"),
    Input('mods', component_property='value'),
    Input('file', component_property='value'),
    Input('up_stat', 'contents'),
    State('up_stat', 'filename'),
    prevent_initial_call=True,
)
def update_graph(N, n_r0, r0, delta_r0, pcont, day, date, ndate,
                 hcap, hqar,
                 tinc, tinf, ticu, thsp, tcrt,
                 trec, tqar, tqah, 
                 pquar, pcross, pqhsp,
                 pj, ph, pc, pf,
                 ligma,sugma,sigma_duck,mod,file,contents,filename):
    r"""
    Produce/change output plot. Triggered on open, or when any variable changes.

    Parameters
    ----------
    **kwargs : `numbers`
        Inputs that are shown on the website.

    Returns
    -------
    plot1, plot2, plot3 : `plotly.graph_objects.Figure`
        Output plots to be demonstrated.

    download1, download2, download3: `file`
        Exported file for download, if requested
    """
    def R0_dynamic(t):
        r"""
        Get R0 based on day and stage inputs.

        Parameters
        ----------
        t : `int`
            Number of days passed since initial outbreak.

        Returns
        -------
        r0 : `float`
            Corresponding reproductive number.
        """
        # Default stage when created initially
        if not delta_r0 or not pcont or not day:
            return 4.1
        # No change yet: Keep to default
        elif t < day[0]:
            return r0
        else:
            i = 0
            # Check which stage t is in
            while t >= day[i]:
                if (i == len(day) - 1) or (t < day[i + 1]):
                    break
                i += 1
            # Initial stage
            if i == 0:
                return r0 * (1 - pcont[0]) - 2 * delta_r0[0] / 30 * (t - (day[0] - 1)) * pcont[0]
            else:
                # Recursively call the function, as R0 works in a similar fashion to Hidden Markov Model
                # If there is increase in proportion contamination (See formula for details)
                if pcont[i] >= pcont[i - 1]:
                    return max(
                        min(R0_dynamic(day[i] - 1), r0 * (1 - pcont[i])) - 2 * delta_r0[i] / 30 * (t - (day[i] - 1)) *
                        pcont[i], 0)
                # If there is decrease in proportion contamination (See formula for details)
                else:
                    if min(R0_dynamic(day[i] - 1), r0 * (1 - pcont[i])) > 0:
                        return min(R0_dynamic(day[i] - 1), r0 * (1 - pcont[i])) + 2 * delta_r0[i] / 30 * (
                                t - (day[i] - 1)) * (1 - pcont[i])
                    else:
                        return 0.0

    # Open up comparison csv file, if there is one
    compare = False
    if contents:
        _, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                df_compare = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))
                compare = True
        except Exception as e:
            print(e)

    # Solve for output variables
    args = (R0_dynamic,
            tinf, tinc, thsp, tcrt,
            ticu, tqar, tqah, trec,
            ph, pc, pf,
            pj, pquar, pqhsp, pcross)

    n_infected = 1
    initial_state = [(N - n_infected) / N, 0, n_infected / N, 0, 0, 0, 0, 0, 0]

    sol = solve_ivp(SEIQHCDRO_model, [0, ndate],
                    initial_state, args=args,
                    t_eval=np.arange(ndate+1), method="Radau")
    S, E, I, Q, H, C, D, R, O = sol.y

    # Show by days passed pr date?
    x_day = pd.date_range(date, periods=ndate+1).tolist()
    x = x_day if 2 in mod else np.linspace(0, ndate, ndate+1)
    
    # Infected, Hospitalised
    ift = np.round((I + H + C + D + R + O) * N)
    hsp = np.round((H + C + D + R) * N)
    hsp_in = np.append([0],[hsp[i + 1] - hsp[i] if hsp[i+1]>hsp[i] else 0 for i in range(ndate)])
    ift_in = np.append([0],[ift[i + 1] - ift[i] if ift[i+1]>ift[i] else 0 for i in range(ndate)])
    for i in range(ndate):
        hsp[i+1]=hsp[i]+hsp_in[i]
        ift[i+1]=ift[i]+ift_in[i]

    # Critical, Dead
    crt = np.round((C + D) * N)
    ded = np.round(D * N)
    crt_in = np.append([0],[crt[i + 1] - crt[i] if crt[i+1]>crt[i] else 0 for i in range(ndate)])
    ded_in = np.append([0],[ded[i + 1] - ded[i] if ded[i+1]>ded[i] else 0 for i in range(ndate)])

    # Quarantine
    qar = np.round((E+I+Q+H+C+D)*N)

    # R0
    r0_trend = np.array([R0_dynamic(t) for t in np.linspace(0, ndate, ndate+1)])

    df = pd.DataFrame({"Date": x_day, 
                       "Infected": ift, 
                       "Daily Infected": ift_in, 
                       "Hospitalised": hsp,
                       "Daily Hospitalised": hsp_in,  
                       "Active ICU": crt-ded,
                       "Deaths":ded})
    
    # Plotting
    fig = make_subplots(rows=1, cols=2, x_title="Date" if 2 in mod else "Days since the beginning of outbreak", y_title="Cases")

    fig.add_trace(go.Scatter(x=x, y=ift, name='Total Infected'), row=1, col=2)
    fig.add_trace(go.Scatter(x=x, y=hsp, name='Total Hospitalised'), row=1, col=2)
    fig.add_trace(go.Scatter(x=x, y=hsp_in, name='Daily Hospital Incidence'), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=ift_in, name='Daily Infected Incidence'), row=1, col=1)
    if 1 in mod:
        fig.add_trace(go.Scatter(x=x, y=hcap * np.ones(ndate+1), name='Hospital Capacity'), row=1, col=2)
        
    fig.update_layout(
        title={
            'text': "OVERALL TREND OF INFECTION",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        title_font_size=20,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor = 'rgb(61,61,61)',
        font=dict(color='rgb(174, 211, 210)')
    )
    fig.update_xaxes(zerolinecolor='rgb(110,110,110)', gridwidth=1, gridcolor='rgb(100,100,100)')
    fig.update_yaxes(zerolinecolor='rgb(110,110,110)', gridwidth=1, gridcolor='rgb(100,100,100)')

    fig1 = make_subplots(rows=1, cols=2, x_title="Date" if 2 in mod else "Days since the beginning of outbreak", y_title="Cases")
    
    fig1.add_trace(go.Scatter(x=x, y=crt-ded, name='Active ICU'), row=1, col=1)
    fig1.add_trace(go.Scatter(x=x, y=ded, name='Deaths'), row=1, col=2)

    fig1.update_layout(
        title={
            'text': "CRITICAL AND FATAL CASES",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        title_font_size=20,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor = 'rgb(61,61,61)',
        font=dict(color='rgb(174, 211, 210)')
    )
    fig1.update_xaxes(zerolinecolor='rgb(110,110,110)', gridwidth=1, gridcolor='rgb(100,100,100)')
    fig1.update_yaxes(zerolinecolor='rgb(110,110,110)', gridwidth=1, gridcolor='rgb(100,100,100)')

    fig2 = make_subplots(rows=1, cols=2, x_title="Date" if 2 in mod else "Days since the beginning of outbreak", y_title="Cases")

    fig2.add_trace(go.Scatter(x=x, y=r0_trend, name='Effective Reproduction Number'), row=1, col=1)
    fig2.add_trace(go.Scatter(x=x, y=qar, name='Total quarantined'), row=1, col=2)
    if 3 in mod:
        fig2.add_trace(go.Scatter(x=x, y=hqar * np.ones(ndate+1), name='Quarantine Capacity'), row=1, col=2)

    fig2.update_layout(
        title={
            'text': "SPREAD AND CONTAINMENT",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        title_font_size=20,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor = 'rgb(61,61,61)',
        font=dict(color='rgb(174, 211, 210)')
    )
    fig2.update_xaxes(zerolinecolor='rgb(110,110,110)', gridwidth=1, gridcolor='rgb(100,100,100)')
    fig2.update_yaxes(zerolinecolor='rgb(110,110,110)', gridwidth=1, gridcolor='rgb(100,100,100)')

    if 2 in mod:
        fig.update_xaxes(dtick="M1", tickformat="%d/%m/%y")
        fig1.update_xaxes(dtick="M1", tickformat="%d/%m/%y")
        fig2.update_xaxes(dtick="M1", tickformat="%d/%m/%y")

    # Add comparison lines if there is any
    if compare:
        if 'infected' in df_compare.columns:
            fig.add_trace(go.Scatter(x=x, y=df_compare['infected'], name='Actual Infected'), row=1, col=2)
        if 'daily_infected' in df_compare.columns:
            fig.add_trace(go.Scatter(x=x, y=df_compare['daily_infected'], name='Actual Daily Infected'), row=1, col=1)
        if 'active_critical' in df_compare.columns:
            fig1.add_trace(go.Scatter(x=x, y=df_compare['active_critical'], name='Actual ICU'), row=1, col=1)
        if 'active_quarantined' in df_compare.columns:
            fig2.add_trace(go.Scatter(x=x, y=df_compare['active_quarantined'], name='Actual On Quarantine'), row=1, col=2)
        if 'deaths' in df_compare.columns:
            fig1.add_trace(go.Scatter(x=x, y=df_compare['deaths'], name='Actual Deaths'), row=1, col=2)

    # Check if there is any download triggered. If there is, send a file, depending on the specified format
    ctx = dash.callback_context.triggered
    if ctx:
        name = 'exported_stats' if not file else file
        current_call = ctx[0]['prop_id'].split('.')[0]
        if current_call=='btn_csv':
            return fig,fig1,fig2, dcc.send_data_frame(df.to_csv, name+".csv"), None, None
        elif current_call=='btn_ipt':
            json_out = json.dumps(
                {"N":N, "n_r0":n_r0, "r0":r0, "delta_r0":delta_r0, 
                 "pcont":pcont, "day":day, "date":date, "ndate": ndate,
                 "hcap":hcap, "hqar":hqar,
                 "tinc":tinc, "tinf":tinf, "ticu":ticu, "thsp":thsp, "tcrt":tcrt,
                 "trec":trec, "tqar":tqar, "tqah":tqah, 
                 "pquar":pquar, "pcross":pcross, "pqhsp":pqhsp,
                 "pj":pj, "ph":ph, "pc":pc, "pf":pf},
                indent=4
            )
            return fig,fig1,fig2, None, None, dict(content=json_out, filename=name+".json")
        elif current_call=='btn_sum':
            text=f'''
Generated by SEIQHCDRO COVID-19 Modelling Team for Vietnam: Hoang-Anh NGO, Tuan Khoi NGUYEN and Thu-Anh NGUYEN

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
Hospital capacity is {hqar}, which is {'not enough' if hqar<np.max(qar) else 'sufficient'} for the worst day of the outbreak, with {np.max(qar)} hospital patients.

The final outcome of the outbreak is
_{np.max(ift)} COVID-19 positive cases
_{np.max(qar)} quarantined individuals 
_{np.max(hsp)} hospitalised patients
_{np.max(crt)} in critical condition
_{np.max(ded)} deceased

            '''
            return fig,fig1,fig2, None, dict(content=text, filename=name+".txt"),None
    return fig,fig1,fig2, None, None, None

# Change input from uploaded files or sample files
@app.callback(
    Output('slider-N', component_property='value'),
    Output('num', 'value'),
    Output('slider-r0', component_property='value'),
    Output('date', component_property='date'),
    Output('ndate', component_property='value'),
    Output('hcap', component_property='value'),
    Output('hqar', component_property='value'),
    Output('slider-tinc', component_property='value'),
    Output('slider-tinf', component_property='value'),
    Output('slider-ticu', component_property='value'),
    Output('slider-thsp', component_property='value'),
    Output('slider-tcrt', component_property='value'),
    Output('slider-trec', component_property='value'),
    Output('slider-tqar', component_property='value'),
    Output('slider-tqah', component_property='value'),
    Output('slider-pquar', component_property='value'),
    Output('slider-pcross', component_property='value'),
    Output('slider-pqhsp', component_property='value'),
    Output('slider-pj', component_property='value'),
    Output('slider-ph', component_property='value'),
    Output('slider-pc', component_property='value'),
    Output('slider-pf', component_property='value'),
    Output('err', 'children'),
    Input('init', 'value'),
    Input('up', 'contents'),
    State('up', 'filename'),
    prevent_initial_call=True
)
def load_to_input(init,content,file):
    r"""
    Load json file content to inputs.

    Parameters
    ----------
    init : `str`
        Sample file to be used.

    content : `base64`
        File content, base64 encoded.

    file : `str`
        File name.

    Returns
    -------
    output : `(Any | List)`
        The modified outputs and upload status, for informing or debugging
    """
    components = [  'slider-N',
                    'n_r0',
                    'slider-r0',
                    'date',
                    'ndate',
                    'hcap',
                    'hqar',
                    'slider-tinc',
                    'slider-tinf',
                    'slider-ticu',
                    'slider-thsp',
                    'slider-tcrt',
                    'slider-trec',
                    'slider-tqar',
                    'slider-tqah',
                    'slider-pquar',
                    'slider-pcross',
                    'slider-pqhsp',
                    'slider-pj',
                    'slider-ph',
                    'slider-pc',
                    'slider-pf',]

    json_attrib = [w.replace('slider-','') if 'slider-' in w else w for w in components]
    json_stage = ['delta_r0', 'pcont', 'day']
    
    # Check which file to be used from
    ctx = dash.callback_context.triggered
    if ctx:
        current_call = ctx[0]['prop_id'].split('.')[0]
        # Sample file to be used
        if current_call=='init':
            jf = json.loads(sample.loc[init])
            updated_name = sample.name[init]
        # Uploaded file to be used
        else:
            if not file:
                return [dash.no_update for i in components] + ['Error: File not found!']
            _, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            jf = json.loads(decoded)
            # Irrelevant attribute handling
            for i in json_attrib+json_stage:
                if i not in jf:
                    return [dash.no_update for i in components] + [f'Error: Input "{i}" not found!']
            # Inconsistent input handling
            if len(jf['day']) != len(jf['delta_r0']) or len(jf['day']) != len(jf['pcont']):
                return[dash.no_update for i in components] + [f'Error: Number of stage inputs not consistent!']
            updated_name = file

    return [jf[i] for i in json_attrib] + [html.P(f'Updated inputs from {updated_name}!',style={'color':'chartreuse'})]


def SEIQHCDRO_model(t, y, R_0,
                    T_inf, T_inc, T_hsp, T_crt, T_icu, T_quar, T_quar_hosp, T_rec,
                    p_h, p_c, p_f, p_jrnl, p_quar, p_quar_hosp, p_cross_cont):
    """
    Main function of SEIQHCDRO model.

    Parameters:
    ---
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

    Returns
    ---
    dy_dt: `list`
        List of numerical derivatives calculated.
    """

    # Check if R is constant or not
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
    r"""
    Routing the content to display.

    Parameters
    ----------
    pathname : `str`
        Picked route.

    Returns
    ---
    content : `dash_html_components.Div`
        A Div of HTML Elements for the specified route.
    """
    if pathname == '/about':
        return about_page
    else:
        return main_page


if __name__ == '__main__':
    # If Mac, uncomment the next line, comment out the 2nd line
    #app.server.run(port=8000, host='127.0.0.1')
    app.run_server(debug=True)
