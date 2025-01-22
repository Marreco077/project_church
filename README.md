# Tithe Manager

This is a tithe management system, developed in Python using the Tkinter library for the graphical interface and SQLite for the database.

## Features

- **Login Screen:** Users can log in using a username and password registered in the database.
- **Dashboard:** After a successful login, the user is redirected to the dashboard where they can manage tithe data.
- **Tithe Management:** The system stores information about the tithe payers, including name, tithe amount, donation date, birthday, phone number, and overdue status.

## Technologies Used

- Python 3.x
- Tkinter (for graphical interface)
- SQLite (for database)

## Project Structure

- **database.py:** Contains the function to create the database and necessary tables.
- **login_screen.py:** Graphical interface for the login, where the user enters their credentials.
- **dashboard.py:** Graphical interface for the dashboard (not included in the example, but you can add functionalities like viewing and managing tithe payers).

## How to Run the Project

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/tithe-manager.git
    cd tithe-manager
    ```

2. Install dependencies (if necessary):

    ```bash
    pip install tkinter sqlite3
    ```

3. Run the `login_screen.py` script to start the application:

    ```bash
    python login_screen.py
    ```

4. The first time you run the project, the database will be automatically created with a default user (`teste` / `123`).

