import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from pathlib import Path

# --- Define Color Palette (can be used in Plotly figures) ---
# These are for direct use in Python/Plotly, mirroring the CSS variables
PRIMARY_COLOR = '#2c3e50'
SECONDARY_COLOR = '#3498db'
ACCENT_COLOR = '#e74c3c'
LIGHT_BG_COLOR = '#ecf0f1'
TEXT_COLOR = '#34495e'
WHITE_COLOR = '#ffffff'
BORDER_COLOR = '#bdc3c7'

# --- 1. Initialize the Dash App ---
app = dash.Dash(__name__) # Dash will automatically pick up CSS from assets folder
server = app.server

# --- 2. Load and Prepare Data ---
data_file_path = Path("output") / "soul_foods_pink_morsel_sales.csv"
error_message = None
df_original = pd.DataFrame({'Date': pd.to_datetime([]), 'Sales': [], 'Region': []})
regions = ['all']

try:
    df_loaded = pd.read_csv(data_file_path)
    if df_loaded.empty:
        error_message = f"Data file '{data_file_path}' is empty."
    else:
        df_loaded['Date'] = pd.to_datetime(df_loaded['Date'])
        df_loaded.sort_values('Date', inplace=True)
        df_original = df_loaded.copy()
        if 'Region' in df_original.columns and not df_original['Region'].empty:
            regions.extend(sorted(df_original['Region'].unique().tolist()))
        else:
            regions.extend(['north', 'east', 'south', 'west'])
            if 'Region' not in df_original.columns:
                 df_original['Region'] = 'unknown'
except FileNotFoundError:
    error_message = f"ERROR: Data file not found at {data_file_path}. Please generate it first."
except Exception as e:
    error_message = f"An error occurred while loading data: {e}"


# --- 3. Define App Layout ---
app.layout = html.Div([
    html.Div(className="app-header", children=[
        html.H1(children="Soul Foods: Pink Morsel Sales Visualiser")
    ]),

    html.Div(className="app-container", children=[
        html.Div(className="controls-and-graph-container", children=[
            html.Div(className="radio-item-container", children=[
                html.Label("Select Region:", className="radio-items-label"),
                dcc.RadioItems(
                    id='region-radio',
                    options=[{'label': region.capitalize(), 'value': region} for region in regions],
                    value='all',
                    className="custom-radio-items",
                    labelStyle={'display': 'block'}
                )
            ]),

            html.Div(className="graph-container", children=[
                dcc.Graph(id='sales-line-chart', style={'height': '65vh'})
            ])
        ]),
    ]),

    html.Div(className="app-footer", children=[
        html.P("Data reflecting sales for Pink Morsels. Price increase on 2021-01-15.")
    ])
])


# --- 4. Define Callbacks ---
@app.callback(
    Output('sales-line-chart', 'figure'),
    [Input('region-radio', 'value')]
)
def update_line_chart(selected_region):
    if error_message:
        return px.line(title=error_message)

    if df_original.empty:
        return px.line(title="No data available to display.")

    temp_df = df_original.copy()

    if selected_region != 'all':
        temp_df = temp_df[temp_df['Region'].str.lower() == selected_region.lower()]

    if temp_df.empty:
        return px.line(title=f"No sales data found for region: {selected_region.capitalize()}")

    daily_sales_filtered_df = temp_df.groupby('Date')['Sales'].sum().reset_index()

    if daily_sales_filtered_df.empty:
        return px.line(title=f"No aggregated sales data for region: {selected_region.capitalize()}")

    fig = px.line(
        daily_sales_filtered_df,
        x="Date",
        y="Sales",
        title=f"Pink Morsel Sales - Region: {selected_region.capitalize()}",
        labels={"Date": "Date", "Sales": "Total Sales ($)"},
        markers=True
    )

    price_increase_date = pd.to_datetime('2021-01-15')

    y_annotation_position = 0
    if not daily_sales_filtered_df.empty and 'Sales' in daily_sales_filtered_df.columns and not daily_sales_filtered_df['Sales'].dropna().empty:
        y_max_for_annotation = daily_sales_filtered_df['Sales'].max()
        if pd.notna(y_max_for_annotation) and y_max_for_annotation > 0:
            y_annotation_position = daily_sales_filtered_df['Sales'].quantile(0.85)
            if y_annotation_position < y_max_for_annotation * 0.1:
                y_annotation_position = y_max_for_annotation * 0.1
        elif pd.notna(y_max_for_annotation):
            y_annotation_position = 10
    else:
        y_annotation_position = 10

    fig.add_vline(
        x=price_increase_date,
        line_width=2,
        line_dash="dash",
        line_color=ACCENT_COLOR # Using the Python variable defined at the top
    )

    fig.update_layout(
        annotations=[
            dict(
                x=price_increase_date, y=y_annotation_position,
                xref="x", yref="y",
                text="Price Increase", showarrow=True, arrowhead=2,
                ax=20, ay=-30,
                font=dict(size=11, color=ACCENT_COLOR), # Using Python variable
                align="left",
                bordercolor="#aaa", borderwidth=1, borderpad=4,
                bgcolor="rgba(255,255,255,0.85)", opacity=0.9
            )
        ],
        title_font_size=20,
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Total Sales ($)",
        legend_title_text='Sales Trend',
        plot_bgcolor=WHITE_COLOR,      # Using Python variable
        paper_bgcolor=WHITE_COLOR,     # Using Python variable
        font=dict(family="Roboto, Segoe UI, sans-serif", size=12, color=TEXT_COLOR), # Using Python variable
        margin=dict(l=80, r=40, t=80, b=80)
    )
    fig.update_traces(hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Sales</b>: $%{y:,.2f}<extra></extra>")

    return fig

# --- 5. Run the App ---
if __name__ == '__main__':
    app.run(debug=True)