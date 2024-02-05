from flask import Flask, render_template, request, jsonify,url_for,redirect
import requests
from requests.exceptions import HTTPError, RequestException
import webbrowser
import joblib
app = Flask(__name__)

# Load the trained model
model = joblib.load('grievance_classifier_model.joblib')

# Load the TF-IDF vectorizer
vectorizer = joblib.load('tfidf_vectorizer.joblib')
@app.route('/add_students')
def add_students():
    return render_template("add_student.html")
@app.route('/form')
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
        php_submit_grievance = 'http://localhost/GrievancePlatform/submit_grievance.php'  # Adjust the URL as needed
        data = {'grievance_text': grievance_text, 'student_name': username,'student_id':student_id,'urgency':urgency}

        try:
            # Use the timeout parameter to avoid hanging indefinitely
            response = requests.post(php_submit_grievance, data=data, timeout=5)

            # Raise an HTTPError for bad responses
            response.raise_for_status()

            # Try to parse the response as JSON
            result = response.json()

            # Check if the expected keys are present in the JSON response
            if 'status' in result and 'message' in result:
                if result['status'] == 'success':
                    # Handle successful login (redirect, set session, etc.)
                     return redirect(url_for('fetch_grievances'))
                else:
                    # Handle failed login (e.g., show error message)
                    return jsonify(result), 401  # Return HTTP status code 401 for unauthorized
            else:
                # Handle unexpected JSON format
                return jsonify({'status': 'error', 'message': 'Unexpected response format'}), 500

        except HTTPError as http_err:
            # Handle HTTP errors (e.g., 404, 500)
            return jsonify({'status': 'error', 'message': f'HTTP Error: {http_err}'})
        except RequestException as req_err:
            # Handle other request-related errors
            return jsonify({'status': 'error', 'message': f'Request Error: {req_err}'})
        except Exception as e:
            # Handle other unexpected errors
            return jsonify({'status': 'error', 'message': f'Unexpected Error: {e}'})
        # Return the result as JSON


@app.route('/')
def index():
    return render_template('login.html')
@app.route('/fetch_grievances')
def fetch_grievances():
    # URL of the PHP file
    php_url = 'http://localhost/GrievancePlatform/data.php'

    # Make a GET request to the PHP file
    response = requests.get(php_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        grievances = response.json()

        # Do something with the fetched data
        # For example, return it as JSON in your Flask route
        return render_template("admin.html",grievances=grievances)
    else:
        # Handle the case when the request was not successful
        return jsonify({'error': 'Failed to fetch grievances'})

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # Get login credentials from the form
        username = request.form['username']
        password = request.form['password']
        role=request.form['role']
        # Send a POST request to the PHP login script
        php_login_url = 'http://localhost/GrievancePlatform/login.php'  # Adjust the URL as needed
        data = {'username': username, 'password': password,'role':role}

        try:
            # Use the timeout parameter to avoid hanging indefinitely
            response = requests.post(php_login_url, data=data, timeout=5)

            # Raise an HTTPError for bad responses
            response.raise_for_status()

            # Try to parse the response as JSON
            result = response.json()

            # Check if the expected keys are present in the JSON response
            if 'status' in result and 'message' in result:
                if result['status'] == 'success':
                    # Handle successful login (redirect, set session, etc.)
                    if result['role']=='admin':
                        return redirect(url_for('fetch_grievances'))
                    else:
                        return render_template("index.html")
                else:
                    # Handle failed login (e.g., show error message)
                    return jsonify(result), 401  # Return HTTP status code 401 for unauthorized
            else:
                # Handle unexpected JSON format
                return jsonify({'status': 'error', 'message': 'Unexpected response format'}), 500

        except HTTPError as http_err:
            # Handle HTTP errors (e.g., 404, 500)
            return jsonify({'status': 'error', 'message': f'HTTP Error: {http_err}'})
        except RequestException as req_err:
            # Handle other request-related errors
            return jsonify({'status': 'error', 'message': f'Request Error: {req_err}'})
        except Exception as e:
            # Handle other unexpected errors
            return jsonify({'status': 'error', 'message': f'Unexpected Error: {e}'})
@app.route('/add_student', methods=['POST'])
def add_student():
    if request.method == 'POST':
        # Get student details from the form
        student_name = request.form['studentName']
        student_id = request.form['studentID']

        # Send a POST request to the PHP file for adding a student
        php_add_student_url = 'http://localhost/GrievancePlatform/add_student.php'  # Adjust the URL as needed
        data = {'studentName': student_name, 'studentID': student_id}

        try:
            response = requests.post(php_add_student_url, data=data, timeout=5)
            response.raise_for_status()
            result = response.json()

            if 'status' in result and 'message' in result:
                if result['status'] == 'success':
                    return jsonify(result), 200
                else:
                    return jsonify(result), 400
            else:
                return jsonify({'status': 'error', 'message': 'Unexpected response format'}), 500

        except requests.exceptions.RequestException as req_err:
            return jsonify({'status': 'error', 'message': f'Request Error: {req_err}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
    webbrowser.open("127.0.0.1:5000")
    
