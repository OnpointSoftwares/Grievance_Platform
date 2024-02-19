from flask import Flask, render_template, request, jsonify,url_for,redirect,session
import requests
from requests.exceptions import HTTPError, RequestException
import webbrowser
import joblib
import random
import mysql.connector
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.secret_key = 'onpoint@123'
# Load the trained model
model = joblib.load('grievance_classifier_model.joblib')

# Load the TF-IDF vectorizer
vectorizer = joblib.load('tfidf_vectorizer.joblib')
def save_to_database(grievance_text, student_name, student_username, urgency):
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
        insert_query = "INSERT INTO grievance_details (student_username,grievace_text,urgency) VALUES (%s, %s, %s)"
        # Values to be inserted into the database
        values = (student_username,grievance_text, urgency)
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
        saved_to_database = save_to_database(str(grievance_text), session['username'],session['username'], str(urgency_text))

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
        return render_template("admin.html",grievances=grievances,username=session['username'])
    else:
        # Handle the case when the request was not successful
        return jsonify({'error': 'Failed to fetch grievances'})
@app.route('/fetch_student_grievances')
def fetch_student_grievances():
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
        return render_template("student_grievance.html",grievances=grievances,username=session['username'])
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
                query = "SELECT * FROM student_details WHERE student_email = %s AND password = %s"
                cursor.execute(query, (username, password))
                user1 = cursor.fetchone()
                if user1:
                    session['username'] = username
                    return redirect(url_for('home'))
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
        try:
            # Extract JSON data from the request body
            data = request.get_json()

            # Get student details from the JSON data
            student_name = data.get('studentName')
            student_email = data.get('studentEmail')

            # Validate required fields
            if not student_name or not student_email:
                return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

            # Establish MySQL connection
            connection = mysql.connector.connect(**db_config)

            # Create a cursor object to execute queries
            cursor = connection.cursor()

            # Example INSERT query (replace with your actual query)
            insert_query = "INSERT INTO student_details (student_name, student_email) VALUES (%s, %s)"
            insert_data = (student_name, student_email)

            # Execute the query
            cursor.execute(insert_query, insert_data)

            # Commit the changes
            connection.commit()

            # Close the cursor and connection
            cursor.close()
            connection.close()

            return jsonify({'status': 'success', 'message': 'Student added successfully'}), 200

        except mysql.connector.Error as mysql_err:
            return jsonify({'status': 'error', 'message': f'MySQL Error: {mysql_err}'}), 500

        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Unexpected Error: {e}'}), 500

@app.route('/address_grievance', methods=['POST'])
def address_grievance():
    if request.method == 'POST':
        grievance_id = request.form['grievance_id']
        
        # Update your database logic here
        try:
            # Establish a connection to the MySQL database
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='grievance_system'
            )

            # Create a cursor object to execute SQL queries
            cursor = connection.cursor()

            # Define the SQL query to update the grievance status to addressed
            update_query = "UPDATE grievance_details SET status = 'addressed' WHERE id = %s"
            cursor.execute(update_query, (grievance_id,))

            # Commit the changes to the database
            connection.commit()

            # Close the cursor and connection
            cursor.close()
            connection.close()

            return jsonify({'status': 'success', 'message': 'Grievance addressed successfully'})

        except mysql.connector.Error as e:
            return jsonify({'status': 'error', 'message': f'MySQL Error: {e}'})

        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Unexpected Error: {e}'})
if __name__ == '__main__':
    app.run(debug=True)
    webbrowser.open("127.0.0.1:5000")
    
