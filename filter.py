from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load the trained model
model = joblib.load('grievance_classifier_model.joblib')

# Load the TF-IDF vectorizer
vectorizer = joblib.load('tfidf_vectorizer.joblib')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit_grievance', methods=['POST'])
def submit_grievance():
    if request.method == 'POST':
        # Get the grievance text from the form
        grievance_text = request.form['grievance_text']

        # Vectorize the input text
        grievance_text_vectorized = vectorizer.transform([grievance_text])

        # Make prediction
        urgency = model.predict(grievance_text_vectorized)[0]

        # Return the result as JSON
        return jsonify({'result': f'Predicted Urgency: {urgency}'})

if __name__ == '__main__':
    app.run(debug=True)
