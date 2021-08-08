---
title: 'SEIQHCDRO COVID-19 Interactive Modelling Tool'
authors:
- affiliation: '1'
  name: Hoang Anh NGO
  orcid: 0000-0002-7583-753X
- affiliation: '2'
  name: Khoi T. Nguyen
  orcid: 0000-0001-8556-5876
- affiliation: '1,3'
  name: Thu-Anh Nguyen
  orcid: 0000-0002-2089-2902

date: "24 July 2021"
bibliography: paper.bib
tags:
- COVID-19
- SEIR
- open-source
- dash
- COVID-19
- compartment model
affiliations:
- index: '1'
  name: The Woolcock Institute of Medical Research, Hanoi, Vietnam
- index: '2'
  name: The Melbourne School of Engineering, The University of Melbourne, Victoria, Australia
- index: '3'
  name: The Faculty of Medicine and Health, The University of Sydney, Sydney, NSW, Australia
---

# Summary

COVID-19 SEIQHCDRO Modelling is a web application that lets users model the COVID-19 outcome of an area, using a system of multiple inputs. Using the extended SEIQHCDRO model, this website provides prediction results on positive case counts, deaths, intensive cares, and where applicable, quarantine. The website will automate the process of running the model, letting users without statistics knowledge to easily define customised inputs, and extend the usage to policy-making or social governance. Source code is stored as open source on [GitHub](https://github.com/tuankhoin/SEIQHCDRO-Interactive-Model) and [Zenodo](https://doi.org/10.5281/zenodo.5136441).

# Statement of need

The onset of a novel global pandemic, COVID-19, in late 2019 - beginning 2020 has put a huge pressure on health system of various countries. However, there has been a certain number of countries who arised as "role models" in containing and minimizing the impact of this pandemic, including Singapore [@covid19-sngapore:2021], New Zealand [@covid19-nz:2021], Taiwan [@covid19-taiwan:2020] or Vietnam [@covid19-vietnam:2021]. Particularly, in the past outbreaks, Vietnam has successfully controlled the COVID-19 pandemic by simultaneously applying numerous strategies, including aggressive contact tracing, mandatory quarantine, routine testing, etc [@covid19-vietnam:2020, @covid19-vietnam:2021]. 

Taken inspiration from this successful case study, to quantify the effectiveness of social governance measures, we have developed a multi-compartment model that integrates all of these practices to estimate impacts of possible mitigation scenarios on the COVID-19 outbreak for any given location, using the SEIQHCDRO model, an extended multi-compartment epidemiological model. The research has been accepted as a presentation at The 52nd World Union Conference on Lung Health [@seiqhcdro-union:2021].

In order to turn the research into an open-source web-app that everyone can access and use with ease, as well as creating a tool for policy makers/public health specialists to facilitate their policy advocate/policy making process, this modelling tool is created as a result. Through this website, anyone can predict their own COVID outcome within any region, only through adjusting common social inputs.

The web application of this interactive modelling tool can be found at [http://covid19-modelling.com](http://covid19-modelling.com). The local installation instructions can be found within the next section.

# Deployment Instructions

Requirements:

* Python 3
  
Steps:

1. Clone the repo: `git clone https://github.com/tuankhoin/SEIQHCDRO-Interactive-Model`
2. Install all dependencies: `pip install requirements.txt`
3. Run `app.py`

# Technical Specifications

This tool is built on Python 3.6, using the following tools:

* **Dash/Flask**: Framework
* **Plotly**: Plotting and framework
* **Heroku**: CI & Deployment platform

For all installed Python libraries, please refer to the requirements at `requirements.txt`.

# Formation of the model 

## Model Flowchart

As an multi-compartment epidemiological model, there must exist specific relations between each and every single compartment. Such relations are expressed though the model flowchart below

![Flowchart](https://drive.google.com/uc?export=view&id=1nb9DFzmOBdlbp8eSaMUsKA45owrYauf_)                  

## Formula

From this, we develop a system of differential equations to simulate the relationship between these compartments. The system reads:

\begin{align*}
    \frac{dS}{dt} & =  - f(R_0, \Delta R_0, p_{cont}, p_{jrnl}, t) \left[ \frac{1}{T_{inf}} + \frac{1 - p_h}{T_{rec}} \right] I(t) S(t) \\
    \frac{dE}{dt} & =  f(R_0, \Delta R_0, p_{cont}, p_{jrnl}, t) \left[ \frac{1}{T_{inf}} + \frac{1 - p_h}{T_{rec}} \right] I(t) S(t) - \frac{1}{T_{inc}} E(t) \\
    \frac{dI}{dt} & = \frac{1}{T_{inc}} E(t) - \left[ \frac{p_h}{T_{inf}} + \frac{1 - p_h}{T_{rec}}\right] I(t) \\
    \frac{dQ}{dt} & = p_{quar} \frac{E}{T_{quar}} - (p_{quar\_hosp} + p_{cross\_cont}) * \frac{Q}{T_{quar\_hosp}} \\
    \frac{dH}{dt} & = p_h \frac{I(t)}{T_{inf}} - (1 - p_c) \frac{H(t)}{T_{hsp}} - p_c \frac{H(t)}{T_{crt}} - \frac{p_h}{T_{rec}} H(t) + \\ & (p_{quar\_hosp} + p_{cross\_cont}) \frac{Q}{T_{quar\_hosp}} \\
    \frac{dC}{dt} & = \frac{p_c}{T_{crt}} H(t) - \frac{C(t)}{T_{icu} + T_{crt}} \\
    \frac{dD}{dt} & = \frac{p_f C(t)}{T_{icu} + T_{crt}} \\
    \frac{dR}{dt} & = (1 - p_c) \frac{H(t)}{T_{hsp}} + (1 - p_f) \frac{C(t)}{T_{icu}} \\
    \frac{dO}{dt} & =  \frac{1 - p_h}{T_{rec}} I(t) + \frac{p_h}{T_{rec}} H(t)
\end{align*}

with two main types of hyper-parameters

* Proportion-related hyper-parameters $p$;
* Time interval related hyperparameters $T$.

To obtain the result, this system of ordinary differential equations (ODEs) will be solved using the `solve_ivp` command within the `SciPy` package in Python. To prevent any stiffness of the system, the `Radau` method, i.e the implicit Runge-Kutta method of the Radau IIA family of order 5.

## Formulation of the basic reproduction number $R_0$

One of the most important aspects of this model is the ability to capture different levels of social distancing/lockdown to the spread of the disease. As such, we have integrated these impacts onto the function representing the effective reproduction number $R_t$ (i.e the basic reproduction number $R_0$ with respect to time).

$$
f(R_0, \Delta R_0, p_{cont}, p_{jrnl}, t)
$$

Assume that there exists two consecutive time intervals separated by a policy scheme change at time $T$. Before time $T$, the population inherits a scheme with change of the basic reproduction number $\Delta R_0$, contact rate reduction $p_{cont}$ and contact rate reduction due to journalism $p_{jrnl}$. After time `T`, the population now inherits a new scheme with a new set of parameters, $\Delta R'_0$, $p'_{cont}$ and $p'_{jrnl}$, respectively.

There are two cases that would happen:

* When $p'_{cont} \geq p_{cont}$ (i.e. the social distancing/lockdown measure tightens), the new function is:

    \begin{align*}
        f(R_0, \Delta R'_0, p'_{cont}, p'_{jrnl}, t) & = \min(R0 \times (1 - p'_{cont}), f(R_0, \Delta R_0, p_{cont}, p_{jrnl}, T-1)) \\
        & - \Delta R'_0 / 15 \times (1 - p'_{cont}) \times (1 - p'_{jrnl}) \times (t - (T-1))
    \end{align*}
    

* When $p'_{cont} < p_{cont}$ (i.e. the social distancing/lockdown measure loosens), the function now becomes:
 
    \begin{align*}
        f(R_0, \Delta R'_0, p'_{cont}, p'_{jrnl}, t) & = \min(R0 \times (1 - p'_{cont}), f(R_0, \Delta R_0, p_{cont}, p_{jrnl}, T-1)) \\
        & + \Delta R'_0 / 15 \times p'_{cont} \times (1 - p'_{jrnl}) \times (t - (T-1))
    \end{align*}

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

* Samples scenarios of the previous outbreaks in Vietnam, including the outbreaks in 
  
    - Danang (07-08/2020);
    - Hai Duong (01-03/2021); 
    - Bac Giang (05-07/2021); and 
    - Ho Chi Minh (05/2021 onwards) with 3 scenarios: best, moderate and worst.
* Import (Upload) a `.json` file that includes all information of the previously calibrated model to continue further moedification 
    without having to restart the whole process from the beginning;
* Upload a csv file of the actual situation and illustrate it alongside with the prediction model. The uploaded csv file can include 
    up to 5 following fields:
  
    - Number of new (incidence) cases per day (`daily_infected`);
    - Total (cumulative) number of cases (`cumulative_infected`);
    - Number of active critical cases (`active_critical`);
    - Total (cumulative) number of deaths (`cumulative_deaths`);
    - Number of active quarantined individuals (`active_quarantined`).


# Acknowledgement

We would like to send our sincerest gratitude towards all team members of [5F Team](https://5fteam.com/) for contributing valuable insights and data to help us complete out model:

* BPharm. Duyen T. Duong, Woolcock Institute of Medical Research Vietnam
* MS. Thao Huong Nguyen, Independent Social Researcher
* Kim Anh Le, MD PhD, Hanoi University of Public Health
* Cuong Quoc Nguyen, MD PhD, Independent Epidemiologist
* Phuc Phan, MD PhD, Vietnam National Hospital of Pediatrics 
* Nguyen Huyen Nguyen, MD, National Hospital of Tropical Diseases (NHTD)

Moreover, we also want to send our warmest thanks to our fellow colleagues and readers for their thoughtful and scholarly evaluation of the model. All comments are hugely appreciated.

# References
