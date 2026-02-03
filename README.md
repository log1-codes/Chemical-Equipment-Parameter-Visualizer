# Chemical Equipment Parameter Visualizer (Hybrid Web + Desktop App)

A professional-grade hybrid application for visualizing and analyzing chemical equipment data. It features a Django backend, a React web frontend, and a PyQt5 desktop application, all sharing a unified modern "Onyx" dark theme.

## 🚀 Overview

This project allows users to upload CSV files containing chemical equipment parameters (Flowrate, Pressure, Temperature). The backend parses the data using Pandas, calculates summary statistics, and manages history. Both Web and Desktop frontends consume the common API to display interactive charts, data tables, and generate PDF reports.

---

## 🛠 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python Django + Django REST Framework |
| **Frontend (Web)** | React.js + Chart.js + Tailwind CSS |
| **Frontend (Desktop)** | PyQt5 + Matplotlib |
| **Data Handling** | Pandas |
| **Reporting** | ReportLab (PDF Generation) |

---

## 📁 Project Structure

```text
Chemical Equipment Parameter Visualizer/
├── backend/            # Django REST API
├── frontend/           # React web application
├── frontend_desktop/   # PyQt5 desktop application
└── sample_equipment_data.csv
```

---

## ⚙️ Installation & Setup

### 1. Backend (Django API)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations api
python manage.py migrate
# Start server
python manage.py runserver
```
*Note: Default admin credentials are `admin` / `admin123`.*

### 2. Frontend Web (React)
```bash
cd frontend
npm install
npm run dev
```

### 3. Frontend Desktop (PyQt5)
```bash
cd frontend_desktop
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## 📊 Usage Guide

1. **Launch the Backend**: Ensure the Django server is running on `http://localhost:8000`.
2. **Web Access**: Open the URL provided by Vite (usually `http://localhost:5173`).
3. **Desktop Access**: Run the `main.py` in the `frontend_desktop` folder.
4. **Upload**: Use the provided `sample_equipment_data.csv` to test the visualization.
5. **Analyze**: View the generated charts, inventory log, and download the PDF reports from the history section.

---

## ✨ Key Features

- **Hybrid Deployment**: Access via browser or standalone desktop app.
- **Premium Onyx Theme**: State-of-the-art dark mode UI for professional use.
- **Real-time Analytics**: Instant calculation of averages and distribution.
- **PDF Export**: Generate professional equipment reports with one click.
- **History Management**: Automatically stores and displays the last 5 successful uploads.
- **Secure Communication**: Integration with Django Basic Authentication.
