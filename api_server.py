"""
Flask API Server for Car Price Prediction
Connects the ML model to the frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import json
import os
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Paths
MODEL_PATH = "./model_advanced.joblib"
DATA_PATH = "./car_dataset_india_cleaned.csv"
METRICS_PATH = "./model_advanced_metrics.json"
MARKET_REFERENCE_PATH = "./market_reference_prices.json"

# Load model and data on startup
model = None
dataset = None
metrics = None
market_reference = None  # dict: (Brand, Model, Fuel_Type_Clean) -> {price_new_min, price_new_max}

def load_model():
    """Load the trained model"""
    global model
    if Path(MODEL_PATH).exists():
        model = joblib.load(MODEL_PATH)
        print("✅ Model loaded successfully")
    else:
        print("⚠️  Model file not found!")

def load_dataset():
    """Load dataset for getting available options"""
    global dataset
    if Path(DATA_PATH).exists():
        dataset = pd.read_csv(DATA_PATH)
        print("✅ Dataset loaded successfully")
    else:
        print("⚠️  Dataset file not found!")

def load_metrics():
    """Load model metrics"""
    global metrics
    if Path(METRICS_PATH).exists():
        with open(METRICS_PATH, 'r') as f:
            metrics = json.load(f)
        print("✅ Metrics loaded successfully")
    else:
        print("⚠️  Metrics file not found!")

def load_market_reference():
    """Load market reference prices (ex-showroom 2024-2025) for baseline and bounds"""
    global market_reference
    market_reference = {}
    if Path(MARKET_REFERENCE_PATH).exists():
        with open(MARKET_REFERENCE_PATH, 'r') as f:
            data = json.load(f)
        for entry in data.get("entries", []):
            key = (entry["Brand"], entry["Model"], entry["Fuel_Type_Clean"])
            market_reference[key] = {
                "price_new_min": entry["price_new_min"],
                "price_new_max": entry["price_new_max"],
                "price_new_avg": (entry["price_new_min"] + entry["price_new_max"]) / 2,
            }
        print("✅ Market reference prices loaded (%d entries)" % len(market_reference))
    else:
        print("⚠️  Market reference file not found; using dataset-only pricing")

def get_market_baseline(brand, model, fuel_type):
    """Return (price_new_avg, price_new_min, price_new_max) in rupees or None"""
    if market_reference is None:
        return None
    key = (brand, model, fuel_type)
    return market_reference.get(key)

def calculate_charge_level_from_gravity(sg):
    """
    Calculate battery charge level from specific gravity (interpolated)
    Specific gravity ranges:
    - Fully charged: 1.265 - 1.285 (100%)
    - 75% charged: ~1.225 (75%)
    - 50% charged: ~1.190 (50%)
    - 25% charged: ~1.155 (25%)
    - Discharged: 1.120 or less (0%)
    """
    if sg >= 1.285:
        return 100.0
    if sg <= 1.120:
        return 0.0
    
    # Interpolate between ranges
    if 1.265 <= sg < 1.285:
        # Between 100% (1.265) and 100% (1.285) - fully charged range
        return 100.0
    elif 1.225 <= sg < 1.265:
        # Between 75% (1.225) and 100% (1.265)
        ratio = (sg - 1.225) / (1.265 - 1.225)
        return 75.0 + (ratio * 25.0)  # Interpolate from 75% to 100%
    elif 1.190 <= sg < 1.225:
        # Between 50% (1.190) and 75% (1.225)
        ratio = (sg - 1.190) / (1.225 - 1.190)
        return 50.0 + (ratio * 25.0)  # Interpolate from 50% to 75%
    elif 1.155 <= sg < 1.190:
        # Between 25% (1.155) and 50% (1.190)
        ratio = (sg - 1.155) / (1.190 - 1.155)
        return 25.0 + (ratio * 25.0)  # Interpolate from 25% to 50%
    elif 1.120 <= sg < 1.155:
        # Between 0% (1.120) and 25% (1.155)
        ratio = (sg - 1.120) / (1.155 - 1.120)
        return 0.0 + (ratio * 25.0)  # Interpolate from 0% to 25%
    
    return 0.0  # Default fallback

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "dataset_loaded": dataset is not None
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get model performance metrics"""
    if metrics:
        return jsonify(metrics)
    return jsonify({"error": "Metrics not available"}), 404

@app.route('/api/options', methods=['GET'])
def get_options():
    """Get available options for dropdowns"""
    if dataset is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    
    try:
        # Get unique values for each field
        brands = sorted(dataset['Brand'].unique().tolist())
        models = sorted(dataset['Model'].unique().tolist())
        fuel_types = sorted(dataset['Fuel_Type_Clean'].unique().tolist())
        transmissions = sorted(dataset['Transmission_Clean'].unique().tolist())
        
        # Get min/max for numeric fields
        year_min = int(dataset['Year'].min())
        year_max = int(dataset['Year'].max())
        mileage_min = float(dataset['Mileage_Clean'].min())
        mileage_max = float(dataset['Mileage_Clean'].max())
        engine_min = int(dataset['Engine_CC_Clean'].min())
        engine_max = int(dataset['Engine_CC_Clean'].max())
        seats_min = int(dataset['Seating_Capacity_Clean'].min())
        seats_max = int(dataset['Seating_Capacity_Clean'].max())
        service_min = float(dataset['Service_Cost_Clean'].min())
        service_max = float(dataset['Service_Cost_Clean'].max())
        
        # EV range in km (driving range per charge); petrol/diesel use mileage_range in kmpl
        ev_range = {"min": 200, "max": 600}
        return jsonify({
            "brands": brands,
            "models": models,
            "fuel_types": fuel_types,
            "transmissions": transmissions,
            "year_range": {"min": year_min, "max": year_max},
            "mileage_range": {"min": mileage_min, "max": mileage_max},
            "ev_range": ev_range,
            "engine_range": {"min": engine_min, "max": engine_max},
            "seats_range": {"min": seats_min, "max": seats_max},
            "service_range": {"min": service_min, "max": service_max}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models_by_brand():
    """Get available models for a specific brand"""
    brand = request.args.get('brand')
    if not brand:
        return jsonify({"error": "Brand parameter required"}), 400
    
    if dataset is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    
    try:
        brand_models = sorted(dataset[dataset['Brand'] == brand]['Model'].unique().tolist())
        return jsonify({"models": brand_models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/fuel-types', methods=['GET'])
def get_fuel_types_by_model():
    """Get available fuel types for a specific brand and model"""
    brand = request.args.get('brand')
    model = request.args.get('model')
    
    if not brand or not model:
        return jsonify({"error": "Brand and Model parameters required"}), 400
    
    if dataset is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    
    try:
        # Get fuel types available for this specific brand and model
        model_data = dataset[(dataset['Brand'] == brand) & (dataset['Model'] == model)]
        if len(model_data) == 0:
            return jsonify({"fuel_types": []})
        
        fuel_types = sorted(model_data['Fuel_Type_Clean'].unique().tolist())
        
        # Filter out Electric if it's not a real EV model
        # Check if this model actually has Electric entries with proper data
        electric_data = model_data[model_data['Fuel_Type_Clean'] == 'Electric']
        if len(electric_data) > 0:
            # Check if these are real EVs (Engine_CC should be 0 for real EVs)
            real_evs = electric_data[electric_data['Engine_CC_Clean'] == 0]
            if len(real_evs) == 0:
                # These are fake EVs, remove Electric from list
                fuel_types = [ft for ft in fuel_types if ft != 'Electric']
        
        # Additional check: Remove Electric if this is a known non-EV model
        known_non_evs = [
            ("Hyundai", "i10"), ("Hyundai", "i20"), ("Hyundai", "Creta"), ("Hyundai", "Venue"), ("Hyundai", "Verna"),
            ("Maruti Suzuki", "Baleno"), ("Maruti Suzuki", "Swift"), ("Maruti Suzuki", "Dzire"), ("Maruti Suzuki", "WagonR"),
            ("Honda", "Amaze"), ("Honda", "City"), ("Honda", "Jazz"), ("Honda", "Civic"),
            ("Toyota", "Innova"), ("Toyota", "Glanza"), ("Toyota", "Fortuner"),
            ("Kia", "Sonet"), ("Kia", "Seltos"), ("Kia", "Carnival"), ("Kia", "Carens"),
            ("Tata Motors", "Punch"), ("Tata Motors", "Altroz"), ("Tata Motors", "Tiago"), ("Tata Motors", "Harrier"),
            ("Mahindra", "Scorpio"), ("Mahindra", "XUV700"), ("Mahindra", "Thar"), ("Mahindra", "XUV300")
        ]
        
        if (brand, model) in known_non_evs and 'Electric' in fuel_types:
            fuel_types = [ft for ft in fuel_types if ft != 'Electric']
        
        return jsonify({"fuel_types": fuel_types})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/model-specs', methods=['GET'])
def get_model_specs():
    """Get default specifications (Engine CC, Seating Capacity) for a specific brand, model, and fuel type"""
    brand = request.args.get('brand')
    model = request.args.get('model')
    fuel_type = request.args.get('fuel_type')
    
    if not brand or not model or not fuel_type:
        return jsonify({"error": "Brand, Model, and Fuel_Type parameters required"}), 400
    
    if dataset is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    
    try:
        # Get specs for this specific combination
        model_data = dataset[
            (dataset['Brand'] == brand) & 
            (dataset['Model'] == model) & 
            (dataset['Fuel_Type_Clean'] == fuel_type)
        ]
        
        if len(model_data) == 0:
            return jsonify({
                "engine_cc": None,
                "seating_capacity": None,
                "avg_mileage": None,
                "avg_service_cost": None
            })
        
        # Get most common values (mode) for fixed specs - these are fixed for each model
        # Engine CC is fixed for each model+fuel_type combination
        engine_cc_mode = model_data['Engine_CC_Clean'].mode()
        if len(engine_cc_mode) > 0:
            engine_cc = int(engine_cc_mode.iloc[0])
        else:
            # If no mode, use median (should be rare as Engine CC is usually fixed)
            engine_cc = int(model_data['Engine_CC_Clean'].median())
        
        # Seating Capacity is also fixed for each model
        # Use mode (most common) to get the correct seating capacity
        seats_mode = model_data['Seating_Capacity_Clean'].mode()
        if len(seats_mode) > 0:
            seating_capacity = int(seats_mode.iloc[0])
        else:
            seating_capacity = int(model_data['Seating_Capacity_Clean'].median())
        
        # Validate seating capacity against known car specs
        # Known seating capacities for common models
        known_seating = {
            ("Hyundai", "i10"): 5,
            ("Hyundai", "i20"): 5,
            ("Hyundai", "Creta"): 5,
            ("Hyundai", "Venue"): 5,
            ("Hyundai", "Verna"): 5,
            ("Maruti Suzuki", "Baleno"): 5,
            ("Maruti Suzuki", "Swift"): 5,
            ("Maruti Suzuki", "Dzire"): 5,
            ("Maruti Suzuki", "WagonR"): 5,
            ("Maruti Suzuki", "Ertiga"): 7,
            ("Honda", "Amaze"): 5,
            ("Honda", "City"): 5,
            ("Honda", "Jazz"): 5,
            ("Honda", "Civic"): 5,
            ("Toyota", "Innova"): 7,
            ("Toyota", "Glanza"): 5,
            ("Toyota", "Fortuner"): 7,
            ("Kia", "Sonet"): 5,
            ("Kia", "Seltos"): 5,
            ("Kia", "Carens"): 7,
            ("Kia", "Carnival"): 7,
            ("Tata Motors", "Punch"): 5,
            ("Tata Motors", "Altroz"): 5,
            ("Tata Motors", "Tiago"): 5,
            ("Tata Motors", "Harrier"): 5,
            ("Tata Motors", "Nexon"): 5,  # Regular Nexon (not EV)
            ("Mahindra", "Thar"): 4,
            ("Mahindra", "Scorpio"): 7,
            ("Mahindra", "XUV700"): 7,
            ("Mahindra", "XUV300"): 5,
        }
        
        # Override with known correct value if available
        if (brand, model) in known_seating:
            seating_capacity = known_seating[(brand, model)]
        
        # Get average for variable specs
        avg_mileage = float(model_data['Mileage_Clean'].mean())
        avg_service_cost = float(model_data['Service_Cost_Clean'].mean())
        
        return jsonify({
            "engine_cc": engine_cc,
            "seating_capacity": seating_capacity,
            "avg_mileage": round(avg_mileage, 1),
            "avg_service_cost": round(avg_service_cost, 0)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/price-range', methods=['GET'])
def get_price_range():
    """Get price range for a specific brand, model, and fuel type"""
    brand = request.args.get('brand')
    model = request.args.get('model')
    fuel_type = request.args.get('fuel_type')
    
    if not brand or not model or not fuel_type:
        return jsonify({"error": "Brand, Model, and Fuel_Type parameters required"}), 400
    
    if dataset is None:
        return jsonify({"error": "Dataset not loaded"}), 500
    
    try:
        # Get price range for this specific combination
        filtered_data = dataset[
            (dataset['Brand'] == brand) & 
            (dataset['Model'] == model) & 
            (dataset['Fuel_Type_Clean'] == fuel_type)
        ]
        
        if len(filtered_data) == 0:
            return jsonify({
                "min_price": None,
                "max_price": None,
                "avg_price": None,
                "count": 0
            })
        
        prices = filtered_data['Price_Clean']
        return jsonify({
            "min_price": float(prices.min()),
            "max_price": float(prices.max()),
            "avg_price": float(prices.mean()),
            "median_price": float(prices.median()),
            "count": len(filtered_data)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict car price"""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            "Brand", "Model", "Year", "Fuel_Type_Clean", "Transmission_Clean",
            "Mileage_Clean", "Engine_CC_Clean", "Seating_Capacity_Clean",
            "Service_Cost_Clean"
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Calculate Age from Year
        current_year = datetime.now().year
        age = current_year - int(data['Year'])
        
        # Handle Battery Charge Level for electric cars (Specific Gravity or % directly)
        # Lower specific gravity = lower battery health = lower price
        battery_charge_level = 0  # Default for non-electric
        if data.get("Fuel_Type_Clean") == "Electric":
            if "Battery_Specific_Gravity" in data and data["Battery_Specific_Gravity"] is not None and str(data["Battery_Specific_Gravity"]).strip() != "":
                # Prefer Specific Gravity: lower SG = lower charge % = lower price
                sg = float(data["Battery_Specific_Gravity"])
                battery_charge_level = calculate_charge_level_from_gravity(sg)
            elif "Battery_Charge_Level" in data and data["Battery_Charge_Level"] is not None and str(data["Battery_Charge_Level"]).strip() != "":
                battery_charge_level = float(data["Battery_Charge_Level"])
            else:
                # Default to 75% for electric cars if not provided
                battery_charge_level = 75
        
        # Prepare input data
        input_data = {
            "Brand": data["Brand"],
            "Model": data["Model"],
            "Year": int(data["Year"]),
            "Fuel_Type_Clean": data["Fuel_Type_Clean"],
            "Transmission_Clean": data["Transmission_Clean"],
            "Mileage_Clean": float(data["Mileage_Clean"]),
            "Engine_CC_Clean": int(data["Engine_CC_Clean"]),
            "Seating_Capacity_Clean": int(data["Seating_Capacity_Clean"]),
            "Service_Cost_Clean": float(data["Service_Cost_Clean"]),
            "Age": age,
            "Battery_Charge_Level": battery_charge_level
        }
        
        # Validate fuel type exists for this model
        model_fuel_types = dataset[
            (dataset['Brand'] == data["Brand"]) & 
            (dataset['Model'] == data["Model"])
        ]['Fuel_Type_Clean'].unique()
        
        if data["Fuel_Type_Clean"] not in model_fuel_types:
            return jsonify({
                "error": f"Fuel type '{data['Fuel_Type_Clean']}' is not available for {data['Brand']} {data['Model']}. Available: {', '.join(model_fuel_types)}"
            }), 400
        
        # Validate year is realistic
        if int(data['Year']) > current_year:
            return jsonify({
                "error": f"Year cannot be in the future. Current year is {current_year}"
            }), 400
        
        if int(data['Year']) < 2000:
            return jsonify({
                "error": "Year should be 2000 or later"
            }), 400
        
        # Get reference price range for validation - filter by similar characteristics
        reference_data = dataset[
            (dataset['Brand'] == data["Brand"]) & 
            (dataset['Model'] == data["Model"]) & 
            (dataset['Fuel_Type_Clean'] == data["Fuel_Type_Clean"])
        ].copy()
        
        # When market reference exists, keep only dataset rows with plausible prices (realistic valuation)
        market_baseline = get_market_baseline(data["Brand"], data["Model"], data["Fuel_Type_Clean"])
        if market_baseline and len(reference_data) > 0:
            max_age = max(reference_data['Age'].max(), age, 1)
            dep_floor = max(0.15, 0.51 - (max_age - 5) * 0.06) if max_age > 5 else 0.20
            plausible_min = market_baseline["price_new_min"] * dep_floor * 0.85
            plausible_max = market_baseline["price_new_max"] * 1.15
            filtered = reference_data[
                (reference_data['Price_Clean'] >= plausible_min) & 
                (reference_data['Price_Clean'] <= plausible_max)
            ]
            if len(filtered) > 0:
                reference_data = filtered
        if len(reference_data) == 0:
            return jsonify({
                "error": f"No reference data found for {data['Brand']} {data['Model']} {data['Fuel_Type_Clean']}"
            }), 400
        
        # Get reference statistics for all ages
        ref_min_price = reference_data['Price_Clean'].min()
        ref_max_price = reference_data['Price_Clean'].max()
        ref_avg_price = reference_data['Price_Clean'].mean()
        ref_median_price = reference_data['Price_Clean'].median()
        price_range = ref_max_price - ref_min_price

        # Get price for similar age cars (within 1 year for more precise matching)
        similar_age_data = reference_data[
            abs(reference_data['Age'] - age) <= 1
        ]

        # Use BASE MODEL (entry) price for used-car valuation; used value must not exceed new base (Cars24/CarDekho/OLX aligned)
        newest_data = reference_data[reference_data['Age'] <= 1]
        if market_baseline:
            newest_avg_price = market_baseline["price_new_min"]  # Base model only
        elif len(newest_data) > 0:
            newest_avg_price = newest_data['Price_Clean'].mean()
        else:
            newest_avg_price = ref_max_price
        
        # Realistic age-based depreciation (India: first 2-3 yr fastest; 5yr ~50% retained; 7yr ~44%)
        if age == 0:
            depreciation_factor = 1.0
        elif age == 1:
            depreciation_factor = 0.82  # ~18% first year
        elif age == 2:
            depreciation_factor = 0.72  # ~28% total
        elif age == 3:
            depreciation_factor = 0.64  # ~36% total
        elif age == 4:
            depreciation_factor = 0.57  # ~43% total
        elif age == 5:
            depreciation_factor = 0.51  # ~49% total
        elif age <= 10:
            depreciation_factor = max(0.40, 0.51 - (age - 5) * 0.02)  # 6-10yr: ~2% per year (Indian resale)
        else:
            depreciation_factor = max(0.20, 0.36 - (age - 10) * 0.02)  # Floor 20%
        
        # Calculate age-adjusted base price
        age_adjusted_base_price = newest_avg_price * depreciation_factor
        
        # If we have similar age data, use it as primary reference
        if len(similar_age_data) > 0:
            similar_avg = similar_age_data['Price_Clean'].mean()
            similar_median = similar_age_data['Price_Clean'].median()
            # Blend age-adjusted price with similar age data
            ref_avg_price = (age_adjusted_base_price * 0.4) + (similar_avg * 0.6)
        else:
            # Use age-adjusted price as reference
            ref_avg_price = age_adjusted_base_price
        
        # --- Battery & Km Driven: computed once, applied at end so final price always reflects them ---
        battery_mult = 1.0
        if data.get("Fuel_Type_Clean") == "Electric" and battery_charge_level >= 0:
            battery_mult = 0.70 + 0.30 * (battery_charge_level / 100.0)  # 100% → 1.0, 0% → 0.70
        km_penalty = 0.0
        if "Km_Driven" in data and data["Km_Driven"] is not None and str(data["Km_Driven"]).strip() != "":
            try:
                km_driven_val = float(data["Km_Driven"])
            except (ValueError, TypeError):
                km_driven_val = None
        else:
            km_driven_val = None
        if km_driven_val is not None and km_driven_val > 0:
            expected_km = max(age * 15000, 10000)
            ratio = km_driven_val / expected_km
            km_penalty = min(0.40, ratio * 0.22)

        # Create DataFrame and predict
        df = pd.DataFrame([input_data])
        raw_prediction = model.predict(df)[0]

        # Get reference data with similar age AND similar characteristics
        similar_specs_data = reference_data[
            (abs(reference_data['Age'] - age) <= 2) &  # Similar age
            (abs(reference_data['Mileage_Clean'] - float(data['Mileage_Clean'])) <= 5) &
            (abs(reference_data['Engine_CC_Clean'] - int(data['Engine_CC_Clean'])) <= 200) &
            (abs(reference_data['Service_Cost_Clean'] - float(data['Service_Cost_Clean'])) <= 5000)
        ]
        
        if len(similar_specs_data) > 0:
            # Use similar specs + age data as base
            base_price = similar_specs_data['Price_Clean'].mean()
        else:
            # Use age-adjusted price as base
            base_price = ref_avg_price
        
        # Get average specs for similar age cars (not all cars)
        similar_age_ref = reference_data[abs(reference_data['Age'] - age) <= 2]
        if len(similar_age_ref) > 0:
            avg_mileage = similar_age_ref['Mileage_Clean'].mean()
            avg_engine = similar_age_ref['Engine_CC_Clean'].mean()
            avg_service = similar_age_ref['Service_Cost_Clean'].mean()
        else:
            # Fallback to all reference data
            avg_mileage = reference_data['Mileage_Clean'].mean()
            avg_engine = reference_data['Engine_CC_Clean'].mean()
            avg_service = reference_data['Service_Cost_Clean'].mean()
        
        user_mileage = float(data['Mileage_Clean'])
        user_engine = int(data['Engine_CC_Clean'])
        user_service = float(data['Service_Cost_Clean'])
        
        # Calculate adjustments based on condition/specs (affect price)
        # Lower mileage than average = higher price (better condition)
        # Higher mileage than average = lower price (worse condition)
        if avg_mileage > 0:
            mileage_ratio = user_mileage / avg_mileage
            # If mileage is 20% lower than average, price increases by 5%
            # If mileage is 20% higher than average, price decreases by 5%
            mileage_adjustment = (1 - mileage_ratio) * 0.25  # 25% impact per 100% difference
        else:
            mileage_adjustment = 0
        
        # Higher engine CC = higher price (more powerful, but only if not electric)
        if user_engine > 0 and avg_engine > 0:  # Not electric
            engine_ratio = user_engine / avg_engine
            engine_adjustment = (engine_ratio - 1) * 0.10  # 10% impact per 100% difference
        else:
            engine_adjustment = 0
        
        # Higher service cost = lower price (more maintenance needed, indicates problems)
        if avg_service > 0:
            service_ratio = user_service / avg_service
            # If service cost is 50% higher, price decreases by 4%
            service_adjustment = (1 - service_ratio) * 0.08  # 8% impact per 100% difference
        else:
            service_adjustment = 0
        
        # Apply adjustments to base price (which is already age-adjusted)
        adjusted_price = base_price * (1 + mileage_adjustment + engine_adjustment + service_adjustment)

        # Blend model prediction with adjusted reference price (battery & km applied once at end)
        # Use model prediction but heavily weight the adjusted reference
        prediction_diff_ratio = abs(raw_prediction - adjusted_price) / adjusted_price if adjusted_price > 0 else 1.0
        
        if prediction_diff_ratio <= 0.15:
            # Close match - use 30% model, 70% adjusted reference
            prediction = (raw_prediction * 0.3) + (adjusted_price * 0.7)
        elif prediction_diff_ratio <= 0.30:
            # Moderate difference - use 15% model, 85% adjusted reference
            prediction = (raw_prediction * 0.15) + (adjusted_price * 0.85)
        else:
            # Large difference - use only 5% model, 95% adjusted reference
            prediction = (raw_prediction * 0.05) + (adjusted_price * 0.95)
        
        # Used-car realistic range: from base model + depreciation (never show new-car max for used)
        if market_baseline:
            base_new = market_baseline["price_new_min"]
            used_car_min = base_new * depreciation_factor * 0.80
            used_car_max = base_new * depreciation_factor * 1.25  # used max cap; never above new base
        else:
            used_car_min = ref_min_price
            used_car_max = ref_max_price
        
        # Age-based validation and bounds (used-car range only)
        if len(similar_age_data) > 0:
            age_min_price = similar_age_data['Price_Clean'].min()
            age_max_price = similar_age_data['Price_Clean'].max()
            age_avg_price = similar_age_data['Price_Clean'].mean()
            prediction = (prediction * 0.7) + (age_avg_price * 0.3)
            lower_bound = max(age_min_price * 0.90, used_car_min) if market_baseline else age_min_price * 0.90
            upper_bound = min(age_max_price * 1.10, used_car_max) if market_baseline else age_max_price * 1.10
        else:
            lower_bound = used_car_min
            upper_bound = used_car_max
        
        # Clamp prediction to used-car realistic bounds
        if prediction < lower_bound:
            prediction = lower_bound
        elif prediction > upper_bound:
            prediction = upper_bound
        
        # Final refinement vs age-adjusted reference (keep within used-car range)
        median_diff = abs(prediction - ref_avg_price) / ref_avg_price if ref_avg_price > 0 else 0
        if median_diff > 0.25:
            prediction = (prediction * 0.5) + (ref_avg_price * 0.5)
        
        # Response: ensure estimate reflects battery % and km driven (apply again at end so blending doesn't hide the effect)
        display_min = used_car_min
        display_max = used_car_max
        prediction = max(display_min, min(display_max, float(prediction)))
        # Final pass: price decreases with lower battery % and higher km driven (guarantee visible effect)
        prediction = prediction * battery_mult * (1 - km_penalty)
        prediction = max(display_min, min(display_max, prediction))
        calculated_age = current_year - int(data['Year'])

        return jsonify({
            "predicted_price": float(prediction),
            "predicted_price_formatted": f"₹ {int(prediction):,}",
            "age": calculated_age,
            "depreciation_applied": f"{((1 - depreciation_factor) * 100):.1f}%",
            "input_data": input_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    print("🚀 Starting Car Price Prediction API Server...")
    load_model()
    load_dataset()
    load_market_reference()
    load_metrics()
    print(f"📡 Server running on http://localhost:{port}")
    print("📝 API Endpoints:")
    print("   - GET  /api/health")
    print("   - GET  /api/metrics")
    print("   - GET  /api/options")
    print("   - GET  /api/models?brand=<brand_name>")
    print("   - GET  /api/fuel-types?brand=<brand>&model=<model>")
    print("   - GET  /api/model-specs?brand=<brand>&model=<model>&fuel_type=<fuel_type>")
    print("   - GET  /api/price-range?brand=<brand>&model=<model>&fuel_type=<fuel_type>")
    print("   - POST /api/predict")
    app.run(host='0.0.0.0', port=port, debug=False)

