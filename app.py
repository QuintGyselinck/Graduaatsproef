from flask import Flask, Response, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
import json
import openai
import os

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

    fig = px.pie(category_totals, values='amount', names='category', title='Uitgaven per categorie')

    svg_bytes = pio.to_image(fig, format="svg")

    svg_string = svg_bytes.decode()

    return Response(svg_string, mimetype='image/svg+xml')

@app.route('/get_bar', methods=['GET'])
def get_bar_chart_for_month(year = 2023, month = 6):
    df = load_data()

    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%y')
    
    df = df[(df['date'].dt.year == year) & (df['date'].dt.month == month)]
    
    df['day'] = df['date'].dt.day

    day_totals = df.groupby('day')['amount'].sum().reset_index()

    fig = px.bar(day_totals, x='day', y='amount', title='Totale uitgaven per dag in de maand juni', labels={"day": "Dag", "amount": "Bedrag"})

    svg_bytes = pio.to_image(fig, format="svg")

    svg_string = svg_bytes.decode()

    return Response(svg_string, mimetype='image/svg+xml')

@app.route('/answer_question', methods=['POST'])
def answer_question():
    question = request.get_json().get('question')

    df = load_data()

    data = df.to_dict('records')

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=f"De data toont dit aan {data}. De vraag is: {question}\n Antwoord in het nederlands en vermeld enkel het antwoord",
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.1,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )

    answer = response.choices[0].text.strip() # type: ignore

    return {'answer': answer}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True) 