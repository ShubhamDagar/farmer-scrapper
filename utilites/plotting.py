import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly
import json
import requests

def get_num(text):
    try:
        if isinstance(text, str):
            # Assumes format like "Rs 1200 / Quintal" -> "1200"
            # Logic from user's previous edit
            return float(text.split('/')[0].split(" ")[1])
        return float(text)
    except:
        return 0.0

def get_max_date(df, commodity):
    df_fil = df.loc[df["commodity"] == commodity, ['commodity', 'state', 'market', 'arrivalDate', 'avgPrice']]
    df_max_date = df_fil.groupby("state")["arrivalDate"].max().reset_index()
    df2 = pd.merge(df_max_date, df_fil, on=['state', 'arrivalDate'], how='inner')
    df2['avgPrice'] = df2['avgPrice'].apply(get_num)
    df3 = df2.groupby(['state', 'arrivalDate'])['avgPrice'].mean().reset_index()
    return df3

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
    # Ensure 'Date' column is in datetime format
    df['arrivalDate'] = pd.to_datetime(df['arrivalDate'])

    # Filter data based on input parameters
    filtered_df = df[
        (df['commodity'] == commodity) &
        (df['state'] == state) &
        (df['market'] == market)
    ]

    if filtered_df.empty:
        print(f"No data found for Commodity: {commodity}, State: {state}, Market: {market}")
        return px.line(title="No Data Available", template="plotly_white")

    # Sort by date and get the latest 7 entries
    latest_7_dates_df = filtered_df.sort_values(by='arrivalDate', ascending=False).head(7)

    # Sort again by date ascending for correct plotting order
    latest_7_dates_df = latest_7_dates_df.sort_values(by='arrivalDate', ascending=True).reset_index(drop=True)

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
    # latest_date = df['arrivalDate_dt'].max()
    # target_commodity = commodity
    # df_filtered = df[(df['arrivalDate_dt'] == latest_date) & (df['commodity'] == target_commodity)]
    # state_prices = df_filtered.groupby('state')['avgPrice_num'].mean().reset_index()
    # state_prices = get_latest_commodity_prices_per_state(df, commodity)
    state_prices = get_max_date(df, commodity)

    # 2. Standardize State Names
    name_corrections = {
        'Uttrakhand': 'Uttarakhand',
        'Orissa': 'Odisha',
        'Pondicherry': 'Puducherry',
        'Andaman and Nicobar': 'Andaman and Nicobar Islands',
        'NCT of Delhi': 'Delhi',
        'Chattisgarh': 'Chhattisgarh'
    }
    state_prices['state'] = state_prices['state'].replace(name_corrections)
    print(state_prices.head())
    # print(state_prices['arrivalDate'].dt.date)
    # 3. Create Master List of All States (The "Grey" Skeleton)
    all_states = [
        "Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", 
        "Bihar", "Chandigarh", "Chhattisgarh", "Dadra and Nagar Haveli and Daman and Diu", 
        "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", 
        "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh", 
        "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", 
        "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", 
        "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
    ]
    df_all_states = pd.DataFrame({'state': all_states})

    # Merge to align data with the master list
    df_merged = pd.merge(df_all_states, state_prices, on='state', how='left')

    # 4. Get India GeoJSON
    geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    # geojson_url = "https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/refs/heads/master/Indian_States"
    # geojson_url = "https://cdn.jsdelivr.net/gh/udit-001/india-maps-data@8d907bc/geojson/india.geojson"
    # geojson_url = "https://raw.githubusercontent.com/civictech-India/INDIA-GEO-JSON-Datasets/refs/heads/main/india_states2.json"
    response = requests.get(geojson_url)
    india_geojson = response.json()
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
    
    fig.add_trace(go.Choropleth(
        geojson=india_geojson,
        featureidkey='properties.ST_NM',
        locations=df_with_data['state'],
        z=df_with_data['avgPrice'],
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

    # print(latest_date)
    map_json = json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    return map_json

def generate_charts(df, commodity, state, market):
    """
    Generates both line chart and map chart for the given parameters.
    """
    line_json = plot_price_history(df, commodity, state, market)
    map_json = generate_clean_india_map(df, commodity)
    
    return {
        "line_chart": line_json,
        "map_chart": map_json,
    }