# SEIQHCDRO COVID-19 INTERACTIVE MODELLING TOOL
![Heroku](https://pyheroku-badge.herokuapp.com/?app=vn-covid-modelling&style=flat)
![ver](https://img.shields.io/badge/version-2.0-blue)

 Interactive website that takes different scenarios to predict COVID outcomes in Vietnam
- [SEIQHCDRO COVID-19 INTERACTIVE MODELLING TOOL](#seiqhcdro-covid-19-interactive-modelling-tool)
  - [Introduction](#introduction)
  - [Deployment Instructions](#deployment-instructions)
  - [Technical Specifications](#technical-specifications)
  - [Formation of the model](#formation-of-the-model)
    - [Model Flowchart](#model-flowchart)
  - [Formula](#formula)
  - [Formulation of the basic reproduction number `R_0`](#formulation-of-the-basic-reproduction-number-r_0)
  - [Tool features](#tool-features)
    - [Modelling features](#modelling-features)
    - [Cross-checking and testing features](#cross-checking-and-testing-features)
  - [Mentions](#mentions)
  - [Citation](#citation)
  - [About the authors](#about-the-authors)
  - [Acknowledgement](#acknowledgement)
  - [License](#license)
  - [Authorship & Contribution](#authorship--contribution)
  - [Website legal disclaimer](#website-legal-disclaimer)

## Introduction

In the past outbreaks, Vietnam has successfully controlled the COVID-19 pandemic by simultaneously applying numerous strategies, including aggressive contact tracing, mandatory quarantine, routine testing, etc. Taken inspiration from our own hometown, to quantify the effectiveness of social governance measures, we have developed a multi-compartment model that integrates all of these practices to estimate impacts of possible mitigation scenarios on the COVID-19 outbreak for any given location, using the SEIQHCDRO model, a multi-variable data modelling/machine learning model. 

In order to turn our research into an open-source web-app that everyone can access and use with ease, as well as creating a tool for policy makers/public health specialists to facilitate their policy advocate/policy making process, this modelling tool is created as a result. **Through this website, anyone can predict their own COVID outcome within any region, only through adjusting common social inputs.**

## Deployment Instructions

Requirements:
* Python 3 (work best with Python 3.6)
  
Steps:
1. Clone the repo: `git clone https://github.com/tuankhoin/SEIQHCDRO-Interactive-Model`
2. Install all dependencies: `pip install requirements.txt`
3. Run `app.py`

## Technical Specifications

This tool is built on Python 3.6, using the following tools:
* **Dash/Flask**: Framework
* **Plotly**: Plotting and framework
* **Heroku**: CI & Deployment platform

For all installed Python libraries, refer to `requirements.txt`.

## Formation of the model 

### Model Flowchart

As an multi-compartment epidemiological model, there must exist specific relations between each and every single compartment. Such relations are expressed though the model flowchart below

![Flowchart](https://drive.google.com/uc?export=view&id=1nb9DFzmOBdlbp8eSaMUsKA45owrYauf_)                  

## Formula

<details>
<summary>Expand!</summary>

From this, we develop a system of differential equations to simulate the relationship between these compartments. The system reads:

![Formula](https://quicklatex.com/cache3/2e/ql_5948b14b283613968f0b24fb80533a2e_l3.png)

with two main types of hyper-parameters
* Proportion-related hyper-parameters `p`;
* Time interval related hyperparameters `T`.

To obtain the result, this system of ordinary differential equations (ODEs) will be solved using the `solve_ivp` command within the `SciPy` package in Python. To prevent any stiffness of the system, the `Radau` method, i.e the implicit Runge-Kutta method of the Radau IIA family of order 5.

## Formulation of the basic reproduction number `R_0`

One of the most important aspects of this model is the ability to capture different levels of social distancing/lockdown to the spread of the disease. As such, we have integrated these impacts onto the function representing the effective reproduction number `R_t` (i.e the basic reproduction number `R_0` with respect to time).

![r0_formula](https://quicklatex.com/cache3/f7/ql_580fe4eb71ceadb277d725dd86ca49f7_l3.png)

Assume that there exists two consecutive time intervals separated by a policy scheme change at time `T`. Before time `T`, the population inherits a scheme with change of the basic reproduction number `delta R_0`, contact rate reduction `p_cont` and contact rate reduction due to journalism `p_jrnl`. After time `T`, the population now inherits a new scheme with a new set of parameters, `delta R'_0`, `p'_cont` and `p'_jrnl`, respectively.

There are two cases that would happen:

* When `p'_cont >= p_cont` (i.e. the social distancing/lockdown measure tightens), the new function is:
  
    ![case1](https://quicklatex.com/cache3/9e/ql_11ac62405647900135857d3b2d429b9e_l3.png)

* When `p'_cont < p_cont` (i.e. the social distancing/lockdown measure loosens), the function now becomes:

    ![case2](https://quicklatex.com/cache3/84/ql_1a46c5cd376b5ef2c5fa51f23f675484_l3.png)
</details>

## Tool features

<details>
<summary>Expand!</summary>

### Modelling features

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

### Cross-checking and testing features

To facilitate the validation and cross-checking of models between users, we provide the following additional features:
* Samples .json files of the previous outbreaks in Vietnam, including the outbreaks in 
    - Danang (07-08/2020);
    - Hai Duong (01-03/2021); and 
    - Bac Giang (05-07/2021).
* Import (Upload) a .json file that includes all information of the previously calibrated model to continue further moedification 
    without having to restart the whole process from the beginning;
* Upload a csv file of the actual situation and illustrate it alongside with the prediction model. The uploaded csv file can include 
    up to 5 following fields:   
    - Number of new (incidence) cases per day (`daily_infected`);
    - Total (cumulative) number of cases (`cumulative_infected`);
    - Number of active critical cases (`active_critical`);
    - Total (cumulative) number of deaths (`cumulative_deaths`);
    - Number of active quarantined individuals (`active_quarantined`).
</details>

## Mentions

Up until now, our research project has been featured at two major conferences in lung health, public health and epidemiology, including:
- [The 52nd World Union Conference on Lung Health](https://theunion.org/our-work/conferences/52nd-union-world-conference-on-lung-health?fbclid=IwAR3DAw1R3eA8L0Jv0cr0aUtoqFJwESIHNvdGCyBKzkPF5KFbsUcXTOOK-ZM);
- [8th Vietnam Lung Association (VILA) Scientific Conference 2021](https://drive.google.com/file/d/10uBQJATgEIVgIAbQdp9n4oWGGYqOiKf-/view?fbclid=IwAR3bNTaz_4UKZxa2TaN5ge6FSJL88vURX7xzFURjkE0J-B4hxuKT_3ZZ3vQ).

Besides, our research has also been featured on a lot of renowned newspapers in Vietnam, including Tuoi tre, VNExpress, Soha, Viet Nam News, etc. as a major tool for our policy advocates to fight against the COVID-19 pandemic in Vietnam.

## Citation

If SEIQHCDRO multi-compartment model in general or the interactive modelling website has been useful for your research and policy advocacy, and you would like to cite it in an scientific publication, please refer to our presentation at the **52nd Union World Conference on Lung Health** as follows:

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
## About the authors

* [**Tuan-Khoi Nguyen**](https://tkhoinguyen.netlify.app/) is the data engineer and tool developer of this project. He is graduating from The University of Melbourne with a Bachelor of Science in Mechatronics, and about to continue his Masters within the same field. His research interest focuses on Machine Learning and its autonomous applications in Robotics and real life problems.
* [**Hoang Anh NGO**](https://orcid.org/0000-0002-7583-753X) is the main author of the SEIQHCDRO model. He is about to graduate from École Polytechnique with a double major in Mathematics and Economics, minor in Computational Economics. He is also currently a Research Contractor at Woolcock Institute of Medical Research
Vietnam. His research interests focus on Epidemiology, (Online) Machine Learning and its applications in Medicine.
* Dr [**Nguyen Thu Anh**](https://www.researchgate.net/profile/Nguyen-Anh-50) is the epidemiological supervisor of this project. She is an epidemiologist and a social scientist by training, with more than 20 years of experience. She holds an honorary position as Senior Clinical Lecturer at University of Sydney, and the head of the Woolcock Institute of Medical Research in Vietnam.

## Acknowledgement

We would like to send our sincerest gratitude towards all team members of [5F Team](https://5fteam.com/) for contributing valuable insights and data to help us complete out model:

* BPharm. Duyen T. Duong, Woolcock Institute of Medical Research Vietnam
* MS. Thao Huong Nguyen, Independent Social Researcher
* Kim Anh Le, MD PhD, Hanoi University of Public Health
* Cuong Quoc Nguyen, MD PhD, Independent Epidemiologist
* Phuc Phan, MD PhD, Vietnam National Hospital of Pediatrics 
* Nguyen Huyen Nguyen, MD, National Hospital of Tropical Diseases (NHTD)

Moreover, we also want to send our warmest thanks to our fellow colleagues and readers for their thoughtful and scholarly evaluation of the model. All comments are hugely appreciated.

## License 
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

SEIQHCDRO COVID-19 Interactive Modelling Tool is a free and open-source web application/software licensed under the [3-clause BSD license](https://github.com/tuankhoin/SEIQHCDRO-Interactive-Model/blob/main/LICENSE).

## Authorship & Contribution
- Based on the license, this is a free software/web application released by the authors. There is no relation between the application and authors' affiliations.
- For support, please write an issue.
- For contribution, please fork and make a pull request.

## Website legal disclaimer
The information contained in this website is for convenience or reference only. The content cannot be considered to be medical advice and is not intended to be a substitute for professional medical counselling, diagnosis or treatment. For any concern please consult a trusted specialist in the field.

Whilst we endeavor to keep the information up to date and correct, we make no representations or warranties of any kind, express or implied, about the completeness, accuracy, timeliness, reliability, suitability or availability with respect to the website or the information, products, services, or related graphics, images, text and all other materials contained on the website for any purpose. It is not meant to be applicable to any specific individual’s medical condition and any reliance you place on such information is therefore strictly at your own risk.

In no event will we be liable for any loss or damage including without limitation, indirect or consequential loss or damage, or any loss or damage whatsoever arising from loss of data or profits arising out of, or in connection with, the use of this website.
                        
                 
                 