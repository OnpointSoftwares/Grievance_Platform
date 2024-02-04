<?php
// Check if the form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Your database connection code here

    $servername = "localhost";
    $username = "root";
    $password = "";
    $dbname = "hospital";

    // Create connection
    $conn = new mysqli($servername, $username, $password, $dbname);

    // Check connection
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    // Get user input
    $username = $_POST["username"];
    $password = $_POST["password"];

    // SQL query to check if the username and password match
    $sql = "SELECT * FROM users WHERE Username = '$username' AND password = '$password'";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        // User is authenticated
        $response = array("status" => "success", "message" => "Login successful");
        echo json_encode($response);
    } else {
        // User authentication failed
        $response = array("status" => "error", "message" => "Invalid username or password");
        echo json_encode($response);
    }

    $conn->close();
}
?>
