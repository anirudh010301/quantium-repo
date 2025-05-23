import dash
from dash import dcc # Dash Core Components
from dash import html # Dash HTML Components
import plotly.express as px
import pandas as pd
from pathlib import Path

# --- 1. Initialize the Dash App ---
app = dash.Dash(__name__)
server = app.server # Expose server for deployment platforms

# --- 2. Load and Prepare Data ---
data_file_path = Path("output") / "soul_foods_pink_morsel_sales.csv"
error_message = None # Initialize error message
daily_sales_df = pd.DataFrame({'Date': pd.to_datetime([]), 'Sales': []}) # Initialize with correct dtypes

try:
    df = pd.read_csv(data_file_path)
    if df.empty:
        error_message = f"Data file '{data_file_path}' is empty."
    else:
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values('Date', inplace=True)
        daily_sales_df = df.groupby('Date')['Sales'].sum().reset_index()
        if daily_sales_df.empty : # If groupby results in empty (e.g. no 'Sales' column)
            error_message = "Could not aggregate daily sales. Check 'Sales' column in data."
            daily_sales_df = pd.DataFrame({'Date': pd.to_datetime([]), 'Sales': []})


except FileNotFoundError:
    error_message = f"ERROR: Data file not found at {data_file_path}. Please generate it first."
except Exception as e:
    error_message = f"An error occurred: {e}"


# --- 3. Create the Line Chart ---
if error_message:
    fig = px.line(title=error_message) # Display error on the chart itself
else:
    fig = px.line(
        daily_sales_df,
        x="Date",
        y="Sales",
        title="Pink Morsel Sales Over Time",
        labels={
            "Date": "Date of Sale",
            "Sales": "Total Sales ($)"
        },
        markers=True
    )

    price_increase_date_str = '2021-01-15'
    price_increase_date_dt = pd.to_datetime(price_increase_date_str)

    # Add a vertical line for the price increase date
    # We will add the annotation separately to avoid triggering the internal _mean error
    fig.add_vline(
        x=price_increase_date_dt,
        line_width=2,
        line_dash="dash",
        line_color="red"
    )

    # Determine a y-position for the annotation
    y_annotation_position = 0
    if not daily_sales_df.empty and 'Sales' in daily_sales_df.columns and not daily_sales_df['Sales'].dropna().empty:
        y_max_for_annotation = daily_sales_df['Sales'].max()
        if pd.notna(y_max_for_annotation):
            y_annotation_position = y_max_for_annotation * 0.85 # Position at 85% of max sales
        else: # if sales column is all NaN
            y_annotation_position = 10
    else: # if dataframe is empty or no sales
        y_annotation_position = 10


    # Add the annotation explicitly to the layout
    # Ensure 'x' for annotation is also a valid datetime recognized by Plotly
    fig.update_layout(
        annotations=[
            dict(
                x=price_increase_date_dt, # Use the datetime object
                y=y_annotation_position,
                xref="x",
                yref="y",
                text="Price Increase",
                showarrow=True,
                arrowhead=2,
                ax=20,   # Arrow x-offset from text
                ay=-30,  # Arrow y-offset from text (points down from text)
                font=dict(
                    size=10,
                    color="red"
                ),
                align="left", # Align text to the left of its x-coordinate
                bordercolor="#c7c7c7", # Optional: add a border to the annotation
                borderwidth=1,
                borderpad=4,
                bgcolor="rgba(255,255,255,0.8)", # Semi-transparent white background
                opacity=0.8
            )
        ],
        xaxis_title="Date of Sale",
        yaxis_title="Total Sales ($)",
        legend_title_text='Sales Trend'
    )

# --- 4. Define the App Layout ---
app.layout = html.Div(children=[
    html.Header(
        html.H1(children="Soul Foods: Pink Morsel Sales Visualiser"),
        style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f0f0f0', 'color': '#333'}
    ),

    html.Div(children=[
        dcc.Graph(
            id='sales-line-chart',
            figure=fig,
            style={'height': '60vh'}
        )
    ], style={'padding': '20px'})
])

# --- 5. Run the App ---
if __name__ == '__main__':
    # Use app.run (the new way) instead of app.run_server
    app.run(debug=True)