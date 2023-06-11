from flask import Flask, Response, request
import pandas as pd
import plotly.express as px
import plotly.io as pio
import json
import openai

app = Flask(__name__)

def load_data():
    with open('transactions.json') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    return df

openai.api_key = "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"

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

@app.route('/answer_question', methods=['POST'])
def answer_question():
    question = request.get_json().get('question')

    df = load_data()

    # Convert the dataframe to a list of dictionaries
    data = df.to_dict('records')

    # Use the OpenAI API to generate an answer
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=f"De data toont dit aan {data}. De vraag is: {question}\n Antwoord in het nederlands en vermeld enkel het antwoord",
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )

    answer = response.choices[0].text.strip() # type: ignore

    return {'answer': answer}

if __name__ == '__main__':
    app.run(port=int("3000"), debug=True)