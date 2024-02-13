from flask import Flask, render_template, request, jsonify,url_for,redirect
import requests
from requests.exceptions import HTTPError, RequestException
import webbrowser
import joblib
import random
import mysql.connector
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# Load the trained model
model = joblib.load('grievance_classifier_model.joblib')

# Load the TF-IDF vectorizer
vectorizer = joblib.load('tfidf_vectorizer.joblib')
def save_to_database(grievance_text, student_name, student_id, urgency):
    try:
        # Establish a MySQL connection
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='grievance_system'
        )
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Define the SQL query to insert data into the database
        insert_query = "INSERT INTO grievance_details (student_id,grievace_text,urgency) VALUES (%s, %s, %s)"
        # Values to be inserted into the database
        values = (student_id,grievance_text, urgency)
        print(values)
        # Execute the query
        cursor.execute(insert_query, values)

        # Commit the changes to the database
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return True  # Return True if data is successfully saved to the database

    except Exception as e:
        print(f"Error: {e}")
        return False  # Return False if an error occurs

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
        if(urgency==0):
            urgency_text="not urgent"
        elif(urgency==1):
            urgency_text="urgent"
        php_submit_grievance = 'http://localhost/GrievancePlatform/submit_grievance.php'  # Adjust the URL as needed
        data = {'grievance_text': grievance_text, 'student_name': "username",'student_id':"student_id",'urgency':str(urgency_text)}
        saved_to_database = save_to_database(str(grievance_text), "username",int(2), str(urgency_text))

    if saved_to_database:
        print("Data successfully saved to the database")
    else:
        print("Failed to save data to the database")
    return jsonify(data)


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

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'grievance_system',
}

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # Get login credentials from the form
        username = request.form['username']
        password = request.form['password']

        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        try:
            # Execute a query to check the login credentials
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                # Handle successful login (redirect, set session, etc.)
                role = user[3]  # Assuming the role is in the third column of the users table
                if role == 'admin':
                    return redirect(url_for('fetch_grievances'))
                else:
                    return render_template("index.html")
            else:
                # Handle failed login (e.g., show error message)
                return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401  # Unauthorized

        except Exception as e:
            # Handle unexpected errors
            return jsonify({'status': 'error', 'message': f'Unexpected Error: {e}'}), 500

        finally:
            # Close the database connection
            cursor.close()
            connection.close()
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
    
