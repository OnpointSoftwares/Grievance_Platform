<?php
// Assuming you have a MySQL database with the following details
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "grievance_system";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Retrieve grievance details from the POST request
$grievance_text = $_POST['grievance_text'];
$student_name = $_POST['student_name'];
$student_id = $_POST['student_id'];
$urgency = $_POST['urgency'];

// Prepare and execute SQL query to insert data into the database
$sql = "INSERT INTO grievances (grievance_text, student_name, student_id, urgency) VALUES (?, ?, ?, ?)";
$stmt = $conn->prepare($sql);
$stmt->bind_param("ssss", $grievance_text, $student_name, $student_id, $urgency);
$stmt->execute();

// Check if the insertion was successful
if ($stmt->affected_rows > 0) {
    echo json_encode(['result' => 'Grievance saved successfully']);
} else {
    echo json_encode(['result' => 'Failed to save grievance']);
}

// Close the database connection
$stmt->close();
$conn->close();
?>
