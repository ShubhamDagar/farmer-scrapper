import pandas as pd
import plotly.express as px
import json

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
