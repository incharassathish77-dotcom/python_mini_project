# Government Scheme Awareness App

A Flask-based web application with an SQLite database designed to raise awareness about various government schemes. It includes search functionality, an eligibility checker, and an admin dashboard for managing schemes.

## Features

- **Home Page**: Lists all available government schemes.
- **Search**: Search for schemes by name or category.
- **Eligibility Checker**: Fill in age, gender, and income to see eligible schemes.
- **Scheme Details**: View detailed benefits, required documents, application procedures, and official websites.
- **Admin Panel**: Add, edit, and delete schemes (Default credentials: `admin` / `admin123`).
- **Ngrok Integration**: Run the app publicly with `run_public.py`.

## Getting Started

### Prerequisites

- Python 3.x
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/incharassathish77-dotcom/python_mini_project.git
   cd python_mini_project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

To run the application locally:
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

To run the application and make it publicly accessible via ngrok:
```bash
python run_public.py
```
*(Optional: Open `run_public.py` and set your `NGROK_AUTHTOKEN` to remove the 2-hour session limit.)*
