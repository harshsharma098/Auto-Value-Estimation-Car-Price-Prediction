# Auto Value Estimation

A full-stack application for estimating car prices using machine learning. The system consists of a React/TypeScript frontend and a Flask API backend that serves a trained ML model.

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Setup Instructions](#️-setup-instructions)
- [How to Run](#-how-to-run)
- [API Endpoints](#-api-endpoints)
- [Training the Model](#-training-the-model)
- [Technologies Used](#️-technologies-used)
- [Troubleshooting](#-troubleshooting)

## 🚀 Features

- **ML-Powered Predictions**: Uses XGBoost/LightGBM/RandomForest models for accurate price estimation
- **Modern Frontend**: Built with React, TypeScript, and Tailwind CSS
- **RESTful API**: Flask backend with CORS support for seamless frontend integration
- **Dynamic Form**: Auto-populated dropdowns based on dataset
- **Real-time Predictions**: Instant price calculations via API

## 📁 Project Structure

```
Auto Value Estimation/
├── api_server.py                          # Flask API server (backend)
├── car_price_model_advanced.py           # ML model training script
├── streamlit_app.py                      # Streamlit demo app (optional)
├── model_advanced.joblib                 # Trained ML model (XGBoost/LightGBM)
├── model_advanced_metrics.json           # Model performance metrics
├── car_dataset_india_cleaned.csv         # Training dataset (Indian car data)
├── market_reference_prices.json          # Ex-showroom prices (2024–2025) for market-aligned estimates
├── requirements.txt                      # Python backend dependencies
├── README.md                             # This file
│
└── Auto Value Estimation Frontend/      # React/TypeScript frontend
    ├── src/
    │   ├── components/                   # React components
    │   │   ├── CarBrands.tsx            # Car brands display component
    │   │   ├── CarEstimationForm.tsx    # Main estimation form component
    │   │   ├── HeroSection.tsx          # Hero section component
    │   │   ├── Logo3D.tsx               # 3D logo component
    │   │   ├── Navbar.tsx               # Navigation bar component
    │   │   ├── ThreeCar.tsx             # 3D car visualization
    │   │   ├── ThreeEmbed.tsx           # 3D embed component
    │   │   └── ui/                      # shadcn/ui components
    │   │       └── [40+ UI components]  # Button, Input, Card, etc.
    │   ├── pages/                       # Page components
    │   │   ├── Index.tsx                # Home page (main estimation page)
    │   │   ├── SignIn.tsx               # Sign in page
    │   │   ├── SignUp.tsx               # Sign up page
    │   │   └── NotFound.tsx             # 404 page
    │   ├── hooks/                       # Custom React hooks
    │   │   ├── use-mobile.tsx          # Mobile detection hook
    │   │   └── use-toast.ts            # Toast notification hook
    │   ├── lib/                        # Utility libraries
    │   │   └── utils.ts                # Utility functions
    │   ├── assets/                     # Static assets
    │   │   └── hero-bg.jpg             # Hero background image
    │   ├── App.tsx                     # Main App component
    │   ├── App.css                     # App styles
    │   ├── main.tsx                    # Application entry point
    │   └── index.css                   # Global styles
    ├── public/                         # Public static files
    │   ├── favicon.ico
    │   └── placeholder.svg
    ├── dist/                           # Production build output
    ├── package.json                    # Node.js dependencies
    ├── vite.config.ts                  # Vite configuration
    ├── tailwind.config.ts              # Tailwind CSS configuration
    ├── tsconfig.json                   # TypeScript configuration
    └── components.json                 # shadcn/ui configuration
```

### Key Files Explained

**Backend:**
- `api_server.py` - Flask REST API server that serves predictions
- `car_price_model_advanced.py` - Script to train/retrain the ML model
- `model_advanced.joblib` - Serialized trained model (must exist for API to work)
- `car_dataset_india_cleaned.csv` - Dataset used for training and form options (cleaned: redundant columns removed, only real EVs tagged, seating fixed; run `python fix_dataset_issues.py` to re-apply)
- `market_reference_prices.json` - Real ex-showroom price ranges (India 2024–2025); used as baseline for depreciation and bounds so estimates align with market trends
- `fix_dataset_issues.py` - One-time or periodic cleanup: remove Electric from non-EV models, fix seating, drop redundant columns

**Frontend:**
- `src/pages/Index.tsx` - Main page with car estimation form
- `src/components/CarEstimationForm.tsx` - Form component that connects to API
- `src/components/ui/` - Reusable UI components from shadcn/ui

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** installed
- **Node.js 18+** and **npm** installed
- Ensure you're in the `Auto Value Estimation` directory

### Step-by-Step Setup

1. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies:**
   ```bash
   cd "Auto Value Estimation Frontend"
   npm install
   ```

3. **Start backend server (Terminal 1):**
   ```bash
   # From the root directory (Auto Value Estimation/)
   python api_server.py
   ```
   The server will start on `http://localhost:5000`

4. **Start frontend (Terminal 2):**
   ```bash
   # From the Auto Value Estimation Frontend/ directory
   cd "Auto Value Estimation Frontend"
   npm run dev
   ```
   The frontend will start on `http://localhost:8080` (or another port if 8080 is busy)

5. **Open browser:** Navigate to `http://localhost:8080` to use the application

## 🛠️ Detailed Setup Instructions

### Backend Setup

1. **Navigate to project root:**
   ```bash
   cd "Auto Value Estimation"
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify required files exist:**
   - ✅ `model_advanced.joblib` (trained model) - **Required**
   - ✅ `car_dataset_india_cleaned.csv` (dataset) - **Required**
   - ✅ `model_advanced_metrics.json` (optional, for metrics endpoint)

4. **Start the Flask API server:**
   ```bash
   python api_server.py
   ```
   
   You should see:
   ```
   🚀 Starting Car Price Prediction API Server...
   ✅ Model loaded successfully
   ✅ Dataset loaded successfully
   ✅ Metrics loaded successfully
   📡 Server running on http://localhost:5000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd "Auto Value Estimation Frontend"
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure API URL (optional):**
   
   Create a `.env` file in the `Auto Value Estimation Frontend/` directory:
   ```env
   VITE_API_URL=http://localhost:5000
   ```
   
   If not set, it defaults to `http://localhost:5000`

4. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   You should see:
   ```
   VITE v5.x.x  ready in xxx ms
   ➜  Local:   http://localhost:8080/
   ```

## 🔌 API Endpoints

### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "dataset_loaded": true
}
```

### `GET /api/metrics`
Get model performance metrics.

**Response:**
```json
{
  "MAE": 22211.80,
  "RMSE": 29602.85,
  "R2": 0.9983
}
```

### `GET /api/options`
Get available options for form dropdowns.

**Response:**
```json
{
  "brands": ["Honda", "Toyota", ...],
  "models": ["City", "Civic", ...],
  "fuel_types": ["Petrol", "Diesel", "CNG", "Electric"],
  "transmissions": ["Manual", "Automatic"],
  "year_range": {"min": 2015, "max": 2024},
  "mileage_range": {"min": 10.0, "max": 30.0},
  "engine_range": {"min": 0, "max": 2500},
  "seats_range": {"min": 2, "max": 8},
  "service_range": {"min": 5000, "max": 30000}
}
```

### `GET /api/models?brand=<brand_name>`
Get available models for a specific brand.

**Response:**
```json
{
  "models": ["City", "Civic", "Amaze", ...]
}
```

### `POST /api/predict`
Predict car price.

**Request Body:**
```json
{
  "Brand": "Honda",
  "Model": "City",
  "Year": 2020,
  "Fuel_Type_Clean": "Petrol",
  "Transmission_Clean": "Manual",
  "Mileage_Clean": 18.5,
  "Engine_CC_Clean": 1500,
  "Seating_Capacity_Clean": 5,
  "Service_Cost_Clean": 10000
}
```

**Response:**
```json
{
  "predicted_price": 1608000.0,
  "predicted_price_formatted": "₹ 1,608,000",
  "input_data": { ... }
}
```

## 🔄 Frontend-Backend Connection

The frontend and backend are connected through:

1. **API Configuration**: The frontend uses the `VITE_API_URL` environment variable (defaults to `http://localhost:5000`)

2. **Form Component**: `CarEstimationForm.tsx` makes API calls to:
   - Load dropdown options on mount
   - Fetch models when brand is selected
   - Submit prediction requests

3. **CORS**: The Flask server has CORS enabled to allow requests from the frontend

## 🎯 How to Run the Project

### Method 1: Quick Start (Recommended)

**Terminal 1 - Backend:**
```bash
# Navigate to project root
cd "Auto Value Estimation"

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the API server
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
# Navigate to frontend directory
cd "Auto Value Estimation Frontend"

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

**Then:**
- Open your browser to `http://localhost:8080`
- The frontend will automatically connect to the backend API at `http://localhost:5000`

### Method 2: Step-by-Step

1. **Open Terminal 1** - Start Backend:
   ```bash
   cd "Auto Value Estimation"
   python api_server.py
   ```
   ✅ Wait for: `📡 Server running on http://localhost:5000`

2. **Open Terminal 2** - Start Frontend:
   ```bash
   cd "Auto Value Estimation Frontend"
   npm run dev
   ```
   ✅ Wait for: `➜  Local:   http://localhost:8080/`

3. **Open Browser** - Navigate to `http://localhost:8080`

### Using the Application

1. **Fill out the car estimation form:**
   - **Brand**: Select from dropdown (e.g., Honda, Toyota, Maruti)
   - **Model**: Select from dropdown (auto-populated based on brand)
   - **Year**: Select the manufacturing year (2015-2024)
   - **Fuel Type**: Select Petrol, Diesel, CNG, or Electric
   - **Transmission**: Select Manual or Automatic
   - **Mileage**: Enter kmpl (e.g., 18.5)
   - **Engine CC**: Enter engine capacity in CC (e.g., 1500)
   - **Seating Capacity**: Select number of seats (2-8)
   - **Service Cost**: Enter annual service cost in ₹ (e.g., 10000)

2. **Click "Calculate Car Value"** button

3. **View the estimated price** displayed below the form in Indian Rupees (₹)

## 🧪 Training the Model

After cleaning the dataset (`python fix_dataset_issues.py`), retrain the model so it learns from corrected fuel types and seating; predictions will still be anchored to market reference for realistic used-car valuation.

To train or retrain the model:

```bash
# Basic training
python car_price_model_advanced.py train --data car_dataset_india_cleaned.csv --out model_advanced.joblib --model xgb

# With hyperparameter tuning
python car_price_model_advanced.py train --data car_dataset_india_cleaned.csv --out model_advanced.joblib --model xgb --tune --n-iter 30
```

Available models: `xgb`, `lgb`, `rf`

## 📊 Model Performance

Current model metrics (from `model_advanced_metrics.json`):
- **MAE**: ₹22,211.80
- **RMSE**: ₹29,602.85
- **R² Score**: 0.9983

## 🛠️ Technologies Used

### Backend
- Flask (Web framework)
- Flask-CORS (CORS support)
- scikit-learn (ML pipeline)
- XGBoost/LightGBM (ML models)
- pandas (Data processing)
- joblib (Model serialization)

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- React Router
- TanStack Query

## 🐛 Troubleshooting

### Backend Issues

1. **Model not found:**
   - Ensure `model_advanced.joblib` exists in the project root
   - Train the model if missing (see Training section)

2. **Dataset not found:**
   - Ensure `car_dataset_india_cleaned.csv` exists in the project root

3. **Port already in use:**
   - Change the port in `api_server.py` (line 118): `app.run(..., port=5001)`

### Frontend Issues

1. **Cannot connect to API:**
   - Ensure backend is running on `http://localhost:5000`
   - Check browser console for CORS errors
   - Verify `VITE_API_URL` in `.env` file

2. **Form options not loading:**
   - Check backend is running and accessible
   - Verify `/api/options` endpoint returns data
   - Check browser network tab for failed requests

## 📝 Notes

- The model expects specific field names (e.g., `Fuel_Type_Clean`, `Transmission_Clean`)
- Age is automatically calculated from Year
- All numeric fields should be within the ranges provided by `/api/options`
- The frontend form validates all fields before submission

## 📄 License

This project is for educational/demonstration purposes.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

