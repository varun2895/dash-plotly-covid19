import pandas as pd
import plotly.express as px

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
app = dash.Dash(__name__)
server = app.server

#---------------------------------------------------------------

india_states = json.load(open("states_india.geojson", "r"))
state_id_map = {}
for feature in india_states["features"]:
    feature["id"] = feature["properties"]["state_code"]
    state_id_map[feature["properties"]["st_nm"]] = feature["id"]


#Taken from kaggle
df = pd.read_csv("covid_19_india.csv")

df['Date'] = pd.to_datetime(df['Date']).dt.date
dff = df[df.groupby('State/UnionTerritory')['Date'].transform('max') == df['Date']]
dff["id"] = dff["State/UnionTerritory"].apply(lambda x: state_id_map[x])
dff = dff[['Date','id','State/UnionTerritory','Cured','Deaths','Confirmed']].sort_values('State/UnionTerritory')

#---------------------------------------------------------------
app.layout = html.Div([

    html.Div([
            html.H1(children='COVID-19 Dashboard',
                    style = {'textAlign' : 'center'}
            )],
            className='col-8',
            style = {'padding-top' : '1%'}
        ),

    html.Div([
        dash_table.DataTable(
            id='datatable_id',
            data=dff.to_dict('records'),
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": False} for i in dff.columns
            ],
            editable=False,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            row_deletable=False,
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 6,
            # page_action='none',
            # style_cell={
            # 'whiteSpace': 'normal'
            # },
            # fixed_rows={ 'headers': True, 'data': 0 },
            # virtualization=False,
            style_cell_conditional=[
                {'if': {'column_id': 'State/UnionTerritory'},
                 'width': '30%', 'textAlign': 'left'},
                {'if': {'column_id': 'Cured'},
                 'width': '20%', 'textAlign': 'left'},
                {'if': {'column_id': 'Deaths'},
                 'width': '20%', 'textAlign': 'left'},
                {'if': {'column_id': 'Confirmed'},
                 'width': '20%', 'textAlign': 'left'},
            ],
        ),
    ],className='row')
    ,

    # html.Div([
    #     html.Div([
    #         dcc.Dropdown(id='linedropdown',
    #             options=[
    #                      {'label': 'Deaths', 'value': 'Deaths'},
    #                      {'label': 'Cured', 'value': 'Cured'},
    #                       {'label': 'Confirmed', 'value': 'Confirmed'}
                        
    #             ],
    #             value='Deaths',
    #             multi=False,
    #             clearable=False
    #         ),
    #     ],className='six columns'),
    # ],className='row'),

    #     html.Div([
    #     dcc.Dropdown(id='piedropdown',
    #         options=[
    #                      {'label': 'Deaths', 'value': 'Deaths'},
    #                      {'label': 'Cured', 'value': 'Cured'},
    #                       {'label': 'Confirmed', 'value': 'Confirmed'}
    #         ],
    #         value='Deaths',
    #         multi=False,
    #         clearable=False
    #     ),
    #     ],className='six columns'),

    # ],className='row'),

    html.Div([
        html.Div([
            dcc.Dropdown(id='linedropdown',
                options=[
                         {'label': 'Deaths', 'value': 'Deaths'},
                         {'label': 'Cured', 'value': 'Cured'},
                          {'label': 'Confirmed', 'value': 'Confirmed'}],
                value='Deaths',
                multi=False,
                clearable=False
            ),
        ],className='six columns'),
        html.Div([
            dcc.Graph(id='linechart'),
        ],className='six columns'),
        html.Div([
        dcc.Dropdown(id='piedropdown',
            options=[
                         {'label': 'Deaths', 'value': 'Deaths'},
                         {'label': 'Cured', 'value': 'Cured'},
                        {'label': 'Confirmed', 'value': 'Confirmed'}
            ],
            value='Deaths',
            multi=False,
            clearable=False
        ),
        ],className='six columns'),
        html.Div([
            dcc.Graph(id='piechart'),
        ],className='six columns'),

    ],className='row'),

    dcc.Graph(id='my_bee_map', figure={})
])

#------------------------------------------------------------------
@app.callback(
    [Output(component_id='piechart',component_property='figure'),
     Output(component_id='linechart',component_property='figure'),
     Output(component_id='my_bee_map', component_property='figure')
     ],
    [Input('datatable_id', 'selected_rows'),
     Input('piedropdown', 'value'),
     Input('linedropdown', 'value')
     ]
)

# call back function
def update_data(chosen_rows,piedropval,linedropval):
    if len(chosen_rows)==0:
        df_filterd = dff[dff['State/UnionTerritory'].isin(['Delhi','Gujarat','Maharashtra','Uttar Pradesh','Karnataka'])]
    else:
        print(chosen_rows)
        df_filterd = dff[dff.index.isin(chosen_rows)]

    pie_chart=px.pie(
            data_frame=df_filterd,
            names='State/UnionTerritory',
            values=piedropval,
            hole=.3,
            labels={'State/UnionTerritory':'State/UnionTerritory'},
            title="COVID-19 cases (Top 5 states)"   
            )


    #extract list of chosen countries
    list_chosen_countries=df_filterd['State/UnionTerritory'].tolist()

    #filter original df according to chosen countries
    #because original df has all the complete dates
    df_line = df[df['State/UnionTerritory'].isin(list_chosen_countries)]

    line_chart = px.line(
            data_frame=df_line,
            x='Date',
            y=linedropval,
            color='State/UnionTerritory',
            labels={'State/UnionTerritory':'State/UnionTerritory', 'Date':'Date'},
            title="COVID-19 cases"   
            )
    line_chart.update_layout(uirevision='foo')

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        # locationmode='USA-states',
        locations='id',
        # scope="usa",
        # color='Pct of Colonies Impacted',
        # hover_data=['Death'],
        # color_continuous_scale=px.colors.sequential.YlOrRd,
        # # labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
        # template='plotly_dark'
        geojson=india_states,
        color="Deaths",
        hover_name="State/UnionTerritory",
        hover_data=["Deaths"],
        title="COVID-19 Deaths",
        center={"lat": 24, "lon": 78},
        color_continuous_scale=px.colors.sequential.YlOrRd
        )
    fig.update_geos(fitbounds="locations", visible=False)    
    return (pie_chart,line_chart, fig)

#------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
