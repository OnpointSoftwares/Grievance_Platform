import pandas as pd
import random

# Function to generate synthetic grievances
def generate_grievances(num_samples):
    grievances = []
    labels = []

    for _ in range(num_samples):
        grievance = " ".join(random.sample(["Classroom", "Exams", "Faculty", "Library", "Facilities", "Other"], k=2))
        grievance += f" {random.choice(['is not', 'are not'])} {random.choice(['satisfactory', 'adequate', 'up to the mark'])}."
        
        grievances.append(grievance)
        labels.append(random.choice([0, 1]))  # 0 for non-urgent, 1 for urgent

    return pd.DataFrame({'text': grievances, 'label': labels})

# Generate a dataset with 100 samples
dataset = generate_grievances(100)

# Display the dataset
print(dataset.head())

# Save the dataset to a CSV file
dataset.to_csv('student_grievances_dataset.csv', index=False)
