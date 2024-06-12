# Face-Recognition-attendance-system-
## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Introduction
This project is a Face Recognition Attendance System that utilizes facial recognition technology to mark the attendance of individuals. It captures an image, recognizes faces in the image, and logs attendance automatically.

## Features
- Real-time face recognition
- Attendance logging with timestamps
- User-friendly GUI for capturing images and viewing attendance
- Configurable to add or remove users
- Data storage using SQLite for easy access and management

## Installation

### Prerequisites
- Python 3.7 or higher
- Node.js and npm
- OpenCV
- dlib
- face_recognition
- SQLite

### Steps
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/face-recognition-attendance-system.git
    cd face-recognition-attendance-system
    ```

2. Backend Setup:
    - Install the required Python packages:
      ```bash
      pip install -r requirements.txt
      ```
    - Set up the SQLite database:
      ```bash
      python setup_database.py
      ```

3. Frontend Setup:
    - Navigate to the `frontend` directory and install the required npm packages:
      ```bash
      cd frontend
      npm install
      ```

## Usage

### Running the Application
1. Start the backend:
    ```bash
    python attendanceSystem.py
    ```

2. Start the frontend:
    ```bash
    cd frontend
    npm start
    ```

3. Open your web browser and navigate to `http://localhost:3000` to access the application.

### Adding Users
1. Use the GUI to navigate to the "Add User" section.
2. Capture the user's face and enter their details.
3. Save the user's data to the database.

### Viewing Attendance
1. Use the GUI to navigate to the "View Attendance" section.
2. Select the date to view the attendance records.

## Configuration
You can configure the settings for the face recognition system in the `config.py` file. This includes parameters like the threshold for face matching, the database path, and the directories for storing images.


