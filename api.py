from flask import Flask, Response
import pandas as pd
import plotly.express as px
import plotly.io as pio
import json

app = Flask(__name__)

def load_data():
    with open('transactions.json') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    return df

@app.route('/get_pie', methods=['GET'])
def get_pie_chart():

    df = load_data()

    category_totals = df.groupby('category')['amount'].sum().reset_index()

    fig = px.pie(category_totals, values='amount', names='category', title='Spending by Category')

    svg_bytes = pio.to_image(fig, format="svg")

    svg_string = svg_bytes.decode()

    return Response(svg_string, mimetype='image/svg+xml')

@app.route('/get_bar', methods=['GET'])
def get_bar_chart():
    df = load_data()

    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%y')
    df['month'] = df['date'].dt.month

    month_totals = df.groupby('month')['amount'].sum().reset_index()

    fig = px.bar(month_totals, x='month', y='amount', title='Total uitgaven per maand')

    svg_bytes = pio.to_image(fig, format="svg")

    svg_string = svg_bytes.decode()

    return Response(svg_string, mimetype='image/svg+xml')

if __name__ == '__main__':
    app.run(debug=True)