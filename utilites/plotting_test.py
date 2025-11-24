import pandas as pd
import plotly.express as px
import json
import requests
import glob
import os
import plotly.graph_objs as go
import plotly

list_of_files = glob.glob('../data/*.csv')


latest_file = max(list_of_files, key=os.path.getctime)
df = pd.read_csv(latest_file)


def plot_price_history(df, commodity, state, market):

    df['arrivalDate'] = pd.to_datetime(df['arrivalDate'])

    filtered_df = df[
        (df['commodity'] == commodity) &
        (df['state'] == state) &
        (df['market_id'] == market)
    ]

    latest_7_dates_df = filtered_df.sort_values(by='arrivalDate', ascending=False).head(7)
    latest_7_dates_df = latest_7_dates_df.sort_values(by='arrivalDate', ascending=True).reset_index(drop=True)
    latest_7_dates_df['avgPrice'] = latest_7_dates_df['avgPrice'].apply(get_num)

    fig = px.line(
        latest_7_dates_df,
        x='arrivalDate',
        y='avgPrice',
        title=f'Price History for {commodity} in {market}, {state} (Latest 7 Dates)',
        markers=True,
        labels={'arrivalDate': 'Date', 'avgPrice': 'Price (INR/Quintal)'},
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_traces(
        mode='lines+markers',
        marker=dict(size=8, symbol='circle', line=dict(width=1, color='DarkSlateGrey')),
        line=dict(width=3, color='royalblue')
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor='black',
        linewidth=1,
        mirror=True,
        title_text='Date'
    )
    fig.update_yaxes(
        showgrid=False,
        linecolor='black',
        linewidth=1,
        mirror=True,
    )

    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=40)
    )
    line_json = json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    return line_json


def generate_clean_india_map(df, commodity): 

    state_prices = get_max_date(df, commodity)

    name_corrections = {
        'Uttrakhand': 'Uttarakhand',
        'Orissa': 'Odisha',
        'Pondicherry': 'Puducherry',
        'Andaman and Nicobar': 'Andaman & Nicobar',
        'NCT of Delhi': 'Delhi',
        'Chattisgarh': 'Chhattisgarh',
        'Jammu and Kashmir': 'Jammu & Kashmir'
    }
    state_prices['state'] = state_prices['state'].replace(name_corrections)
    
    all_states = [
        "Andaman & Nicobar", "Andhra Pradesh", "Arunachal Pradesh", "Assam", 
        "Bihar", "Chandigarh", "Chhattisgarh", "Dadra and Nagar Haveli and Daman and Diu", 
        "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu & Kashmir", 
        "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh", 
        "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", 
        "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", 
        "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
    ]

    df_all_states = pd.DataFrame({'state': all_states})

    df_merged = pd.merge(df_all_states, state_prices, on='state', how='left')
    
    with open('./utilites/india.geojson', 'r') as f:
        india_geojson = json.load(f)
        geojson_states = [f['properties']['ST_NM'] for f in india_geojson['features']]
        data_states = set(df_merged['state'])
        geo_states = set(geojson_states)
            

    fig = go.Figure()

    fig.add_trace(go.Choropleth(
        geojson=india_geojson,
        featureidkey='properties.ST_NM',
        locations=df_merged['state'],
        z=[1] * len(df_merged),
        colorscale=[[0, 'lightgrey'], [1, 'lightgrey']],
        showscale=False,
        marker_line_color='white',
        marker_line_width=0.5,
        hoverinfo='skip'
    ))

    df_with_data = df_merged.dropna(subset=['avgPrice'])
    
    fig.add_trace(go.Choropleth(
        geojson=india_geojson,
        featureidkey='properties.ST_NM',
        locations=df_with_data['state'],
        z=df_with_data['avgPrice'].tolist(),
        colorscale='YlOrRd',
        marker_line_color='white',
        marker_line_width=0.5,
        name='Price',
        colorbar_title='Price (Rs/Quintal)'
    ))

    fig.update_geos(
        visible=False,
        fitbounds="locations"
    )

    fig.update_layout(
        margin={"r":0,"t":50,"l":0,"b":0},
        height=700
    )
    
    map_json = json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    return map_json


def get_max_date(df, commodity):
    df_fil = df.loc[df["commodity"] == commodity, ['commodity', 'state', 'market', 'arrivalDate', 'avgPrice']]
    df_max_date = df_fil.groupby("state")["arrivalDate"].max().reset_index()
    df2 = pd.merge(df_max_date, df_fil, on=['state', 'arrivalDate'], how='inner')
    df2['avgPrice'] = df2['avgPrice'].apply(get_num)
    df3 = df2.groupby(['state', 'arrivalDate'])['avgPrice'].mean().reset_index()
    return df3


def get_num(text):
    num = float(text.split('/')[0].split(" ")[1])
    return num


def plotting(commodity, state, market):
    indianMap = generate_clean_india_map(df, commodity)
    lineGraph = plot_price_history(df, commodity, state, market)
    return {
        "indianMap": indianMap,
        "priceLineGraph": lineGraph
    }