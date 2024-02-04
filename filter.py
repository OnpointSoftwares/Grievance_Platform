from flask import Flask, render_template, request, jsonify
import requests
from requests.exceptions import HTTPError, RequestException

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('admin.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # Get login credentials from the form
        username = request.form['username']
        password = request.form['password']

        # Send a POST request to the PHP login script
        php_login_url = 'http://localhost/GrievancePlatform/login.php'  # Adjust the URL as needed
        data = {'username': username, 'password': password}

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
                    return jsonify(result)
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

if __name__ == '__main__':
    app.run(debug=True)
