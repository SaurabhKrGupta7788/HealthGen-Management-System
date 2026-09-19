# Next-gen Health Management System (NHMS)

A modular, multi-modal Django-based platform delivering end-to-end healthcare support. The system processes patient data and medical imaging to provide AI-powered diagnostics, home remedy suggestions, organ donation tracking, and interactive mapping/routing to healthcare facilities.

## Features

| # | Feature | Method / Tooling |
|---|---|---|
| 1 | AI Diagnostics | PyTorch models for ECG arrhythmia, cataracts, tuberculosis, tumor segmentation |
| 2 | Home Remedies | Symptom-to-remedy lookup and natural treatment suggestions |
| 3 | Organ Search | Donor registration and proximity-based lookup (blood type matching) |
| 4 | Facility Mapping | Shortest driving route calculation using OSMnx and NetworkX |
| 5 | Authentication | Secure Role-based access (Patient, Clinic, Hospital) |

## Architecture Overview

\\\
Web Interface (User/Clinic/Hospital)
    │
    ▼
┌──────────────────────────┐
│  Django Request Router   │  ← Handles authentication and role verification
└──────────┬───────────────┘
           │
    ┌──────┼───────────────┬────────────────┐
    ▼      ▼               ▼                ▼
┌───────┐ ┌────────────┐ ┌─────────────┐ ┌─────────────┐
│ AI    │ │ Home       │ │ Organ       │ │ Facility    │
│ Diags │ │ Remedies   │ │ Management  │ │ Routing     │
└───┬───┘ └──────┬─────┘ └──────┬──────┘ └──────┬──────┘
    │            │              │               │
    ▼            ▼              ▼               ▼
┌───────┐ ┌────────────┐ ┌─────────────┐ ┌─────────────┐
│PyTorch│ │ SQLite DB  │ │ Geo-Spatial │ │ OSMnx /     │
│Models │ │ Query      │ │ Filtering   │ │ NetworkX    │
└───┬───┘ └──────┬─────┘ └──────┬──────┘ └──────┬──────┘
    │            │              │               │
    ▼            ▼              ▼               ▼
┌──────────────────────────────────────────────────────┐
│                  Consolidated Results                │
└──────────────────────────────────────────────────────┘
\\\

## System Output

The system outputs varying results depending on the module. For AI Diagnostics:

| Modality | Patient/Upload | Prediction Result | Confidence/Status |
|---|---|---|---|
| ECG | patient_102.png | Arrhythmia Detected | 89.4% |
| Chest X-Ray | patient_205.jpg | Tuberculosis - Negative | 95.1% |

For Facility Mapping, the system outputs an interactive map (map_paths.html) with the shortest driving route from the user to the nearest hospital.

## Directory Structure

\\\
├── medcare/                 # Core Django project and apps
│   ├── diseaseprediction/   # AI inference endpoints & forms
│   ├── homeremedies/        # Symptom → remedy lookup logic
│   ├── organavailability/   # Donor registration & search
│   ├── mapthings/           # OSMnx & NetworkX routing scripts
│   ├── landingpage/         # Auth & landing pages
│   ├── templates/           # Shared HTML templates
│   ├── static/              # CSS, JS, images
│   ├── media/               # Uploaded files for prediction
│   ├── manage.py            # Django CLI entrypoint
│   └── requirements.txt     # Python dependencies
├── Pipfile                  # Pipenv configuration
└── map_paths.html           # Generated map output example
\\\

## How to Run

### 1. Prerequisites
- Python 3.8+
- pip (or Pipenv)

### 2. Install Dependencies

\\\ash
# Create and activate virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Navigate to inner directory and install dependencies
cd medcare
pip install -r requirements.txt
\\\

### 3. Run the Application

\\\ash
# Apply database migrations
python manage.py migrate

# Run development server
python manage.py runserver
\\\

### 4. Usage
1. Open the URL shown in terminal (default: \http://127.0.0.1:8000\)
2. Sign up as a Patient or Clinic.
3. Access modules from the dashboard:
   - **Disease Prediction**: Upload an image (X-ray, ECG) for immediate AI inference.
   - **Home Remedies**: Input symptoms to get recommendations.
   - **Organ Availability**: Search for donors by organ and blood type.
   - **Maps**: View nearest hospitals and calculate driving routes.

## Key Design Decisions

1. **Modular Django Architecture**: Splitting the system into independent apps (\diseaseprediction\, \homeremedies\, \mapthings\) allows independent scaling and development.
2. **On-the-fly Geo-Routing**: Instead of static maps, the system uses \OSMnx\ and \NetworkX\ to compute exact, drivable routes based on real road networks dynamically.
3. **Integrated PyTorch Inference**: AI models are directly loaded into Django views for synchronous inference, eliminating the overhead of a separate microservice for diagnostics while maintaining fast response times.
