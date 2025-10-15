import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objects as go

# Path to the CSV files
btc_csv_file = "btc_current_price.csv"  # Current price history file
orderbook_csv_file = "current_order_book.csv"  # Order book history file
liquidation_csv_file = "current_liquidation_order.csv"  # Liquidation order file


# Initialize Dash app
app = Dash(__name__)

# Initialize a variable to store the last processed timestamp
last_processed_timestamp = None

# Layout of the app
app.layout = html.Div(
    [
        html.H1("Bid, Ask, and Liquidation Prices Over Time", style={"textAlign": "center", "marginBottom": "20px"}),
        dcc.Graph(
            id='live-chart',
            config={'responsive': True},
            style={'height': '90vh', 'width': '100%'},
            figure=go.Figure(
                data=[
                    go.Scatter(x=[], y=[], mode='markers', name='Current Price', marker=dict(color='blue')),
                    go.Scatter(x=[], y=[], mode='markers', name='Bids', marker=dict(color='green')),
                    go.Scatter(x=[], y=[], mode='markers', name='Asks', marker=dict(color='red')),
                    go.Scatter(x=[], y=[], mode='markers', name='Liquidations', marker=dict(color='orange'))
                ],
                layout=go.Layout(
                    yaxis=dict(
                        tickformat='.0f',  # Display full numbers
                        dtick=200,        # Set tick difference to 200
                        title='Price'     # Add a label to the y-axis for clarity
                    )
                )
            )
        ),
        dcc.Interval(
            id='interval-component',
            interval=1000,  # Refresh every 1 second
            n_intervals=0
        )
    ],
    style={"margin": "0", "padding": "0", "height": "100vh", "width": "100vw"}
)

# Callback to update the chart dynamically
@app.callback(
    Output('live-chart', 'extendData'),
    Input('interval-component', 'n_intervals')
)
def update_chart(n):
    global last_processed_timestamp

    # Load the current price data from btc_price_history.csv
    df_btc = pd.read_csv(btc_csv_file)
    # Load the order book data from order_book_history.csv
    df_orderbook = pd.read_csv(orderbook_csv_file)
    # Load the liquidation data from current_liquidation_order.csv
    try:
        df_liquidation = pd.read_csv(liquidation_csv_file)
        df_liquidation['Event Time (IST)'] = pd.to_datetime(df_liquidation['Event Time (IST)'])
    except Exception as e:
        df_liquidation = pd.DataFrame()

    # Ensure the Datetime column is in the correct format
    df_btc['Datetime'] = pd.to_datetime(df_btc['Datetime'], format="%Y-%m-%d %H:%M:%S")
    df_orderbook['Datetime'] = pd.to_datetime(df_orderbook['Datetime'], format="%Y-%m-%d %H:%M:%S")

    # Get the current time and calculate the 5-minute time window
    current_time = pd.Timestamp.now()
    time_5_min_ago = current_time - pd.Timedelta(minutes=5)

    # Filter df_btc and df_orderbook to include only data from the last 5 minutes
    df_btc_recent = df_btc[df_btc['Datetime'] >= time_5_min_ago]
    df_orderbook_recent = df_orderbook[df_orderbook['Datetime'] >= time_5_min_ago]

    # Only get data newer than the last processed timestamp
    if last_processed_timestamp is not None:
        df_btc_recent = df_btc_recent[df_btc_recent['Datetime'] > last_processed_timestamp]
        df_orderbook_recent = df_orderbook_recent[df_orderbook_recent['Datetime'] > last_processed_timestamp]

    # If there is no new data, return None to avoid updating the plot
    if df_btc_recent.empty and df_orderbook_recent.empty and df_liquidation.empty:
        return None

    # Extract the current price (last price) from the recent btc data
    current_price = df_btc_recent['Price'].iloc[-1] if not df_btc_recent.empty else None
    current_timestamp = df_btc_recent['Datetime'].iloc[-1] if not df_btc_recent.empty else None

    # Update the last processed timestamp
    if current_timestamp is not None:
        last_processed_timestamp = current_timestamp

    # Define the price range filter (±1000)
    price_range = 2000
    quantity_threshold = 45  # Quantity filter (> 10)

    # Filter bids and asks based on the current price ±1000 range and quantity > 10
    bids = df_orderbook_recent[df_orderbook_recent['Type'] == 'Bid']
    asks = df_orderbook_recent[df_orderbook_recent['Type'] == 'Ask']
    
    # Apply filters: Price range and Quantity > 10
    bids = bids[(bids['Price'] >= current_price - price_range) & 
                (bids['Price'] <= current_price + price_range) & 
                (bids['Quantity'] > quantity_threshold)]
    
    asks = asks[(asks['Price'] >= current_price - price_range) & 
                (asks['Price'] <= current_price + price_range) & 
                (asks['Quantity'] > quantity_threshold)]

    # Prepare data to extend the plot
    data = {
        'x': [
            df_btc_recent['Datetime'].tolist(),
            bids['Datetime'].tolist(),
            asks['Datetime'].tolist(),
            df_liquidation['Event Time (IST)'].tolist() if not df_liquidation.empty else []
        ],
        'y': [
            df_btc_recent['Price'].tolist(),
            bids['Price'].tolist(),
            asks['Price'].tolist(),
            df_liquidation['Price'].tolist() if not df_liquidation.empty else []
        ]
    }

    trace_indices = [0, 1, 2, 3]  # Current price, bids, asks, liquidations

    return data, trace_indices, [len(data['x'][0]), len(data['x'][1]), len(data['x'][2]), len(data['x'][3])]

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
