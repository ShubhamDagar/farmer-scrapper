import pandas as pd
import plotly.express as px
import json
import requests
import glob
import os
import plotly.graph_objs as go
import plotly

list_of_files = glob.glob('./data/*.csv')

# Find the latest file based on creation time
if list_of_files:
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Using latest file: {latest_file}")
    df = pd.read_csv(latest_file)
else:
    print("No CSV files found in data/")
    df = pd.DataFrame()

def plot_price_history(df, commodity, state, market):
    """
    Generates a Plotly line chart showing the price history for the latest 7
    available dates for a given commodity, state, and market with enhanced aesthetics.

    Args:
        df (pd.DataFrame): The DataFrame containing price data.
                           Expected columns: 'Commodity', 'State', 'Market', 'Date', 'Price'.
        commodity (str): The commodity to filter by.
        state (str): The state to filter by.
        market (str): The market to filter by.

    Returns:
        plotly.graph_objects.Figure: A Plotly line chart.
    """
    if df.empty:
         return px.line(title="No Data Available", template="plotly_white")

    # Ensure 'Date' column is in datetime format
    df['arrivalDate'] = pd.to_datetime(df['arrivalDate'])

    # Filter data based on input parameters
    filtered_df = df[
        (df['commodity'] == commodity) &
        (df['state'] == state) &
        (df['market_id'] == market)
    ]
    pct = 0

    if filtered_df.empty:
        print(f"No data found for Commodity: {commodity}, State: {state}, Market: {market}")
        fig = px.line(title="No Data Available", template="plotly_white")
        return json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

    # Sort by date and get the latest 7 entries
    latest_7_dates_df = filtered_df.sort_values(by='arrivalDate', ascending=False).head(7)

    # Sort again by date ascending for correct plotting order
    latest_7_dates_df = latest_7_dates_df.sort_values(by='arrivalDate', ascending=True).reset_index(drop=True)
    latest_7_dates_df['avgPrice'] = latest_7_dates_df['avgPrice'].apply(get_num)

    # Create the Plotly line chart with a clean template
    fig = px.line(
        latest_7_dates_df,
        x='arrivalDate',  # Use the actual date for x-axis
        y='avgPrice',
        title=f'Price History for {commodity} in {market}, {state} (Latest 7 Dates)',
        markers=True,
        labels={'arrivalDate': 'Date', 'avgPrice': 'Price (INR/Quintal)'},
        template='plotly_white'  # Use a clean white template
    )

    # Enhance line and marker appearance
    fig.update_traces(
        mode='lines+markers',
        marker=dict(size=8, symbol='circle', line=dict(width=1, color='DarkSlateGrey')),
        line=dict(width=3, color='royalblue')
    )

    # Update axes for a cleaner look, remove grids, and ensure consistent tick spacing
    fig.update_xaxes(
        showgrid=False,  # Remove x-axis grid lines
        linecolor='black',  # Add axis line color
        linewidth=1,
        mirror=True,
        title_text='Date' # Explicitly set x-axis title
    )
    fig.update_yaxes(
        showgrid=False,  # Remove y-axis grid lines
        linecolor='black',  # Add axis line color
        linewidth=1,
        mirror=True,
    )

    # Update layout for hover and background color
    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
        paper_bgcolor='rgba(0,0,0,0)', # Transparent paper background
        margin=dict(l=40, r=40, t=80, b=40) # Adjust margins
    )
    line_json = json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    return line_json


def generate_clean_india_map(df, commodity):    
    if df.empty:
        print(list_of_files)
        return {}

    # state_prices = get_latest_commodity_prices_per_state(df, commodity)
    state_prices = get_max_date(df, commodity)

    # 2. Standardize State Names
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
    print(state_prices.head())
    
    # 3. Create Master List of All States (The "Grey" Skeleton)
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

    # Merge to align data with the master list
    df_merged = pd.merge(df_all_states, state_prices, on='state', how='left')
    
    print("DEBUG: Unique states in df_merged:")
    print(df_merged['state'].unique())
    print("DEBUG: Sample of df_merged with avgPrice:")
    print(df_merged[['state', 'avgPrice']].head(10))

    # 4. Get India GeoJSON
    try:
        with open('./utilites/india.geojson', 'r') as f:
            india_geojson = json.load(f)
            print("DEBUG: GeoJSON loaded. First feature property keys:")
            print(india_geojson['features'][0]['properties'].keys())
            geojson_states = [f['properties']['ST_NM'] for f in india_geojson['features']]
            print("DEBUG: First 5 GeoJSON states:", geojson_states[:5])
            
            # Check for mismatches
            data_states = set(df_merged['state'])
            geo_states = set(geojson_states)
            print("DEBUG: States in Data but NOT in GeoJSON:", data_states - geo_states)
            print("DEBUG: States in GeoJSON but NOT in Data:", geo_states - data_states)
            
    except FileNotFoundError:
        print("india.geojson not found")
        return {}

    # 5. Build the Map with Two Layers
    fig = go.Figure()

    # Layer 1: The "Background" (All States -> Grey)
    # We plot every state in the list with a fixed grey color
    fig.add_trace(go.Choropleth(
        geojson=india_geojson,
        featureidkey='properties.ST_NM',
        locations=df_merged['state'],
        z=[1] * len(df_merged), # Dummy value for plotting
        colorscale=[[0, 'lightgrey'], [1, 'lightgrey']], # Force all to grey
        showscale=False,        # Hide the legend for this layer
        marker_line_color='white', # White borders between states
        marker_line_width=0.5,
        hoverinfo='skip'        # Don't show hover info for the background
    ))

    # Layer 2: The "Heatmap" (Valid Data -> Colors)
    # We only plot states that actually have a price value
    df_with_data = df_merged.dropna(subset=['avgPrice'])
    print(f"DEBUG: df_with_data shape: {df_with_data.shape}")
    print(f"DEBUG: df_with_data columns: {df_with_data.columns}")
    print(f"Shubham: df_with_data['avgPrice'] head: {df_with_data['avgPrice'].head()}")
    print(f"DEBUG: df_with_data['state'] head: {df_with_data['state'].head()}")
    
    fig.add_trace(go.Choropleth(
        geojson=india_geojson,
        featureidkey='properties.ST_NM',
        locations=df_with_data['state'],
        z=df_with_data['avgPrice'].tolist(),
        colorscale='YlOrRd',    # Your desired heat map scale
        marker_line_color='white',
        marker_line_width=0.5,
        name='Price',
        colorbar_title='Price (Rs/Quintal)'
    ))

    # 6. Configure Layout to "Show Only India"
    fig.update_geos(
        visible=False,        # Hides the world map, countries, oceans (sets them to blank)
        fitbounds="locations" # Automatically zooms to show only the drawn Indian states
    )

    fig.update_layout(
        # title=f"Mean {target_commodity} Price by State (Latest Date: {latest_date.date()})",
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
    if isinstance(text, (int, float)):
        return float(text)
    try:
        num = float(text.split('/')[0].split(" ")[1])
        return num
    except (IndexError, ValueError, AttributeError):
        return 0.0

def plotting(commodity, state, market):
    pct=0
    indianMap = generate_clean_india_map(df, commodity)
    lineGraph = plot_price_history(df, commodity, state, market)
    return {
        "indianMap": indianMap,
        "priceLineGraph": lineGraph
    }