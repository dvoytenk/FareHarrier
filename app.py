import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from sklearn.externals import joblib
from darksky import get_forecast
import pendulum
import os

app = dash.Dash(__name__)
server = app.server
server.secret_key = os.environ.get('SECRET_KEY', 'my-secret-key')
app.title='FareHarrier'

stops=pd.read_pickle('stations.pkl')
stops=stops[:-2]
lats=stops['stop_lat']
lons=stops['stop_lon']
labels=list(stops['stop_name'])
stopnums=stops['parent_station'].astype('float')

rf = joblib.load('rf23.pkl') 

keys=['day_of_week','weeks','hr','stop_id','heat_index']




def serve_layout():
    return html.Div(
    [
    html.Div([
        html.Div(html.H1('Fare',style={'color':'orange','float':'right'}), className="six columns"),
        html.Div(html.H1('Harrier',style={'color':'black'}),className="row")]),
    
    
    html.Div(id='text-content'),
    
        html.H2('We use machine learning to send NYC taxi drivers to subway stations with long predicted wait times.'),
    html.Div(children='''
        Select a train direction and move the slider to predict wait times over the next 24 hours.
    '''),
        html.Div(children='''
        Hover over the circles to see station names and predicted wait times.
    '''),
        
    html.Br([]),
    html.Label('Train Direction:'),
    dcc.Dropdown(
        id='dirdropdown',
        options=[
            {'label': 'Uptown', 'value': 'uptown'},
            {'label': 'Downtown', 'value': 'downtown'},
        ],
        value='uptown'
    ),
    
    #hrs=[pendulum.now().add(hours=i).hour for i in range(0,24)]
    
      html.Label('Time of day'),
    dcc.Slider(
        id='numslider',
        min=0,
        max=23,
        #marks={i:str(i) for i in range(0,24)},
        marks={i:'' if i%2==1 else pendulum.now(tz='America/New_York').add(hours=i).strftime('%b \n %d \n %H:00') for i in range(0,24)},
        value=0,
        #vertical=True,
        #style={'width':'75%'},
    ),
    
      #html.Div(children='''    
    #'''),
    #html.Div(id='text-content'),
    html.Br([]),
    html.Br([]),
    html.Br([]),
    
    #the displaymodebar disables the save fig and plotly links
    #the undo button is disabled via css
    dcc.Graph(id='map',config={'displayModeBar': False},style={'width': '60%','text-align':'center','padding':'10px'}),
    
    html.Br([]),

    
    html.Div([
    dcc.RadioItems(options=[
        {'label': i, 'value': i} for i in ['Terms', 'About']
    ], value='Terms',
    id='navigation-links'),
    html.Div(id='body',children='''''')
    ])

    
    ], style={'width':'60%','margin':'auto'})
    
    
app.layout=serve_layout    

@app.callback(dash.dependencies.Output('body', 'children'), [dash.dependencies.Input('navigation-links', 'value')])
def display_children(chapter):
    if chapter == 'Terms':
        return [html.Div(children='''We do not store or share any of your information.'''),html.A('Powered by Dark Sky.',href="https://darksky.net/poweredby/"),]
    elif chapter == 'About':
        return [html.Div(children='''Built by Denis Voytenko for the Fall 2017 Insight Data Science Fellowship project.'''),
	    html.Div(children='''Presentation slides are available here:'''),
            html.A('Google Slides',href="https://docs.google.com/presentation/d/e/2PACX-1vT7lohxWn4W9GUVkMLwr4RYHcpotDEO5AEHQSLwtgeIYjxdBQMPAJKHHl_Z2668W7hEAZPZ___Q92qz/pub?start=false&loop=false&delayms=3000"),
            html.Div(children='''Source code for this project available here:'''),
            html.A('GitHub',href="https://github.com/dvoytenk/FareHarrier"),
            ]


@app.callback(
    dash.dependencies.Output('map', 'figure'),[dash.dependencies.Input('numslider', 'value'),dash.dependencies.Input('dirdropdown', 'value')])
def update_graph(slider_value,dropdown_value):  
    S=np.array(stopnums)
    #clean up terminal stations
    termini=[140.,247.,257.,640.,101.,401.,201.,501.,601,301.,138.]
    termini_idx=[ np.where(S==t)[0][0] for t in termini]
    if dropdown_value=='uptown':
        multiplier=1
        #termini=[101.,401.,201.,501.,601]
        #termini_idx=[ np.where(S==t)[0][0] for t in termini]
    if dropdown_value=='downtown':
        multiplier=-1
        #termini=[140.,247.,257.,640.,101.,401.,201.,501.,601,301.]
        #termini_idx=[ np.where(S==t)[0][0] for t in termini]
    #do some model/darksky stuff here
    params=get_forecast()
    vals=params[slider_value]
    
    inputmatrix=np.ones([len(stopnums),len(keys)])
    inp=np.multiply(inputmatrix,vals)
    inp[:,3]=multiplier*stopnums
    wt=rf.predict(inp)
    wt[termini_idx]=0.0
    
    #make terminal indices to account for long times there in specific directions
    
    wtlabels=['%1.d'%round(w) for w in wt]
    scale=4.*wt #we want the first value to be no more than 90, so no point in normalizing it any furhter
    wtc= ['hsl('+str(h)+',50%'+',50%)' for h in scale]
    #wtc= ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, len(wt))]
  
    #timelabels=[labels[i]+', '+wtlabels[i]+' min.' for i in range(len(labels))]
    timelabels=[]
    for i in range(len(labels)):
	if wtlabels[i]=='%1.d'%0.0:
		if 'Cortlandt St'== labels[i]:
			timelabels.append(labels[i]+', '+'closed')
                else:
			timelabels.append(labels[i]+', '+'terminus')
        else:
            timelabels.append(labels[i]+', '+wtlabels[i]+' min.') 

    return {
        'data': [{
            'lat': lats,
            'lon': lons,
            'marker': {
                'size': wt,
                'color':wtc,
            },
            'text':  timelabels,
            #'customdata': labels,
            'type': 'scattermapbox'
        }],
        'layout': {
            'mapbox': {
                'accesstoken': 'YOURMAPBOXTOKENGOESHERE',
                
                'center':dict(lat=40.754,lon=-73.977),
                'zoom':10,
            },
            'hovermode': 'closest',
            #'margin': {'l': 100, 'r':100, 't': 100, 'b':100},
            #'margin':'auto',
            'width':'800',
            'height':'800',
            #'padding':'10px',
                
        }
    }



app.css.append_css({
    #'external_url': 'https://rawgit.com/dvoytenk/skipthetrain/master/bWLwgP.css'
     'external_url':'https://cdn.rawgit.com/dvoytenk/FareHarrier/f655b9e9/bWLwgP.css',
})

if __name__ == '__main__':
    #app.run_server(host='0.0.0.0',port=8000,debug=False)
    app.run_server()
