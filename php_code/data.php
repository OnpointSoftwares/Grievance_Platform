<?php

// Your database connection code here
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
// Fetch data from the database (replace this with your actual query)
$query = "SELECT * FROM grievance_details";
$result = mysqli_query($conn, $query);

// Convert the result to an associative array
$data = array();
while ($row = mysqli_fetch_assoc($result)) {
    $data[] = $row;
}

// Close the database connection
mysqli_close($conn);

// Return JSON response
header('Content-Type: application/json');
echo json_encode($data);
?>
