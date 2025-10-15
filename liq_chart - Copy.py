import pandas as pd
import plotly.express as px

# Load CSV data
file_path = 'liq_chart.csv'  # Replace with the actual file path
df = pd.read_csv(file_path)

# Convert 'timestamp' to datetime for proper plotting
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Map trade types to colors
df['color'] = df['trade'].map({'Short Trade': 'green', 'Long Trade': 'red'})

# Create the interactive scatter plot
fig = px.scatter(
    df,
    x='timestamp',
    y='price',
    color='trade',
    color_discrete_map={'Short Trade': 'green', 'Long Trade': 'red'},
    labels={'timestamp': 'Timestamp', 'price': 'Price', 'trade': 'Trade Type'},
    title='Trade Data Visualization',
    hover_data=['trade', 'price'],  # Show trade and price on hover
)

# Update layout for better readability
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(  # Add range selectors for zooming
            buttons=[
                dict(count=1, label='1h', step='hour', stepmode='backward'),
                dict(count=6, label='6h', step='hour', stepmode='backward'),
                dict(count=1, label='1d', step='day', stepmode='backward'),
                dict(step='all'),
            ]
        ),
        rangeslider=dict(visible=True),  # Enable range slider
        type="date",
    ),
    template='plotly_white',  # Use a clean template
)

# Show the interactive plot
fig.show()