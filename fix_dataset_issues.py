"""
Comprehensive script to fix all dataset issues:
1. Remove Electric fuel type from non-EV models
2. Fix incorrect seating capacities
3. Ensure Engine CC is correct for each model
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Real electric cars in India (dataset uses "Nexon" for Nexon EV)
REAL_EV_MODELS = {
    "Tata Motors": ["Nexon EV", "Nexon", "Tigor EV", "Tiago EV", "Punch EV"],
    "Mahindra": ["XUV400", "eVerito"],
    "Hyundai": ["Kona Electric", "Ioniq 5"],
    "MG": ["ZS EV", "Comet EV"],
    "BYD": ["e6"],
    "Kia": ["EV6"],
    "Citroen": ["eC3"],
    "Nissan": ["Leaf"]
}

# Known non-EV models (should NEVER have Electric option)
NON_EV_MODELS = [
    ("Hyundai", "i10"), ("Hyundai", "i20"), ("Hyundai", "Creta"), ("Hyundai", "Venue"), ("Hyundai", "Verna"),
    ("Maruti Suzuki", "Baleno"), ("Maruti Suzuki", "Swift"), ("Maruti Suzuki", "Dzire"), ("Maruti Suzuki", "WagonR"), ("Maruti Suzuki", "Ertiga"),
    ("Honda", "Amaze"), ("Honda", "City"), ("Honda", "Jazz"), ("Honda", "Civic"), ("Honda", "WR-V"),
    ("Toyota", "Innova"), ("Toyota", "Glanza"), ("Toyota", "Fortuner"), ("Toyota", "Camry"), ("Toyota", "Urban Cruiser"),
    ("Kia", "Sonet"), ("Kia", "Seltos"), ("Kia", "Carnival"), ("Kia", "Carens"),
    ("Tata Motors", "Punch"), ("Tata Motors", "Altroz"), ("Tata Motors", "Tiago"), ("Tata Motors", "Harrier"),
    ("Mahindra", "Scorpio"), ("Mahindra", "XUV700"), ("Mahindra", "Thar"), ("Mahindra", "XUV300"), ("Mahindra", "Bolero"),
    ("Skoda", "Kushaq"), ("Skoda", "Slavia"), ("Skoda", "Superb"), ("Skoda", "Octavia"), ("Skoda", "Rapid"),
    ("Volkswagen", "Taigun"), ("Volkswagen", "Polo"), ("Volkswagen", "Virtus"), ("Volkswagen", "Vento"), ("Volkswagen", "Tiguan"),
    ("Renault", "Kiger"), ("Renault", "Lodgy"), ("Renault", "Kwid"), ("Renault", "Duster"), ("Renault", "Triber")
]

# Correct seating capacities for models
MODEL_SEATING_CAPACITY = {
    # Hatchbacks (5-seater)
    ("Hyundai", "i10"): 5,
    ("Hyundai", "i20"): 5,
    ("Maruti Suzuki", "Baleno"): 5,
    ("Maruti Suzuki", "Swift"): 5,
    ("Maruti Suzuki", "WagonR"): 5,
    ("Maruti Suzuki", "Dzire"): 5,
    ("Tata Motors", "Punch"): 5,
    ("Tata Motors", "Altroz"): 5,
    ("Tata Motors", "Tiago"): 5,
    ("Tata Motors", "Nexon"): 5,  # Regular Nexon
    ("Renault", "Kwid"): 5,
    ("Renault", "Kiger"): 5,
    
    # Sedans (5-seater)
    ("Hyundai", "Verna"): 5,
    ("Honda", "Amaze"): 5,
    ("Honda", "City"): 5,
    ("Honda", "Civic"): 5,
    ("Skoda", "Slavia"): 5,
    ("Skoda", "Octavia"): 5,
    ("Skoda", "Rapid"): 5,
    ("Volkswagen", "Virtus"): 5,
    ("Volkswagen", "Vento"): 5,
    ("Tata Motors", "Tigor"): 5,  # Regular Tigor
    
    # SUVs (5-seater)
    ("Hyundai", "Creta"): 5,
    ("Hyundai", "Venue"): 5,
    ("Kia", "Sonet"): 5,
    ("Kia", "Seltos"): 5,
    ("Tata Motors", "Harrier"): 5,
    ("Mahindra", "XUV300"): 5,
    ("Skoda", "Kushaq"): 5,
    ("Volkswagen", "Taigun"): 5,
    ("Renault", "Duster"): 5,
    
    # SUVs (7-seater)
    ("Toyota", "Innova"): 7,
    ("Toyota", "Fortuner"): 7,
    ("Mahindra", "Scorpio"): 7,
    ("Mahindra", "XUV700"): 7,
    ("Kia", "Carnival"): 7,
    ("Kia", "Carens"): 7,
    ("Maruti Suzuki", "Ertiga"): 7,
    ("Renault", "Lodgy"): 7,
    ("Renault", "Triber"): 7,
    
    # Special cases
    ("Mahindra", "Thar"): 4,
    ("Toyota", "Glanza"): 5,
    ("Honda", "Jazz"): 5,
    ("Honda", "WR-V"): 5,
    ("Volkswagen", "Polo"): 5,
    ("Volkswagen", "Tiguan"): 5,
    ("Skoda", "Superb"): 5,
    ("Toyota", "Camry"): 5,
    ("Toyota", "Urban Cruiser"): 5,
    ("Mahindra", "Bolero"): 7,
    ("Kia", "EV6"): 5,
    ("Tata Motors", "Nexon"): 5,
}

def is_real_ev(brand, model):
    """Check if this is a real electric car"""
    return brand in REAL_EV_MODELS and model in REAL_EV_MODELS[brand]

def fix_dataset(input_file, output_file):
    """Fix all dataset issues"""
    print("=" * 60)
    print("Comprehensive Dataset Fixing Script")
    print("=" * 60)
    
    print("\nLoading dataset...")
    df = pd.read_csv(input_file)
    print(f"Original dataset shape: {df.shape}")
    
    # Initialize battery columns if they don't exist
    if 'Battery_Charge_Level' not in df.columns:
        df['Battery_Charge_Level'] = np.nan
    if 'Battery_Specific_Gravity' not in df.columns:
        df['Battery_Specific_Gravity'] = np.nan
    
    electric_removed = 0
    seating_fixed = 0
    
    print("\nFixing dataset issues...")
    
    for idx, row in df.iterrows():
        brand = row['Brand']
        model = row['Model']
        fuel_clean = row['Fuel_Type_Clean']
        
        # Fix 1: Remove Electric from non-EV models
        if fuel_clean == "Electric":
            if not is_real_ev(brand, model):
                # This is a fake EV, convert to correct fuel type
                # Get most common fuel type for this model (excluding Electric)
                model_data = df[
                    (df['Brand'] == brand) & 
                    (df['Model'] == model) & 
                    (df['Fuel_Type_Clean'] != 'Electric') &
                    (df.index != idx)  # Exclude current row
                ]
                
                if len(model_data) > 0:
                    most_common_fuel = model_data['Fuel_Type_Clean'].mode()
                    if len(most_common_fuel) > 0:
                        correct_fuel = most_common_fuel.iloc[0]
                        df.at[idx, 'Fuel_Type_Clean'] = correct_fuel
                        
                        # Fix Engine CC
                        if row['Engine_CC_Clean'] == 0:
                            # Get most common engine CC for this model+fuel
                            engine_data = model_data[model_data['Fuel_Type_Clean'] == correct_fuel]['Engine_CC_Clean']
                            if len(engine_data) > 0:
                                df.at[idx, 'Engine_CC_Clean'] = int(engine_data.mode().iloc[0]) if len(engine_data.mode()) > 0 else int(engine_data.median())
                            else:
                                df.at[idx, 'Engine_CC_Clean'] = 1500  # Default
                        
                        # Clear battery data
                        df.at[idx, 'Battery_Charge_Level'] = np.nan
                        df.at[idx, 'Battery_Specific_Gravity'] = np.nan
                        electric_removed += 1
        
        # Fix 2: Correct seating capacity
        if (brand, model) in MODEL_SEATING_CAPACITY:
            correct_seats = MODEL_SEATING_CAPACITY[(brand, model)]
            if row['Seating_Capacity_Clean'] != correct_seats:
                df.at[idx, 'Seating_Capacity_Clean'] = correct_seats
                seating_fixed += 1
    
    print(f"\n✅ Removed Electric from {electric_removed} non-EV entries")
    print(f"✅ Fixed seating capacity for {seating_fixed} entries")
    
    # Add battery data for real EVs
    print("\nAdding battery data for real electric cars...")
    ev_count = 0
    current_year = datetime.now().year
    
    for idx, row in df.iterrows():
        if row['Fuel_Type_Clean'] == 'Electric' and is_real_ev(row['Brand'], row['Model']):
            age = row['Age']
            
            # Generate realistic specific gravity based on age
            if age <= 2:
                sg = np.random.uniform(1.265, 1.285)
            elif age <= 5:
                sg = np.random.uniform(1.220, 1.250)
            else:
                sg = np.random.uniform(1.150, 1.200)
            
            # Calculate charge level
            if sg >= 1.265:
                charge_level = 100.0
            elif sg >= 1.225:
                ratio = (sg - 1.225) / (1.265 - 1.225)
                charge_level = 75.0 + (ratio * 25.0)
            elif sg >= 1.190:
                ratio = (sg - 1.190) / (1.225 - 1.190)
                charge_level = 50.0 + (ratio * 25.0)
            elif sg >= 1.155:
                ratio = (sg - 1.155) / (1.190 - 1.155)
                charge_level = 25.0 + (ratio * 25.0)
            else:
                ratio = (sg - 1.120) / (1.155 - 1.120) if sg > 1.120 else 0
                charge_level = 0.0 + (ratio * 25.0)
            
            df.at[idx, 'Battery_Specific_Gravity'] = round(sg, 3)
            df.at[idx, 'Battery_Charge_Level'] = round(charge_level, 1)
            ev_count += 1
    
    print(f"✅ Added battery data for {ev_count} real electric cars")
    
    # Ensure battery data is NaN for non-electric cars
    df.loc[df['Fuel_Type_Clean'] != 'Electric', 'Battery_Charge_Level'] = np.nan
    df.loc[df['Fuel_Type_Clean'] != 'Electric', 'Battery_Specific_Gravity'] = np.nan
    
    # Drop redundant columns (model and API use only *_Clean and key fields)
    cols_to_drop = [c for c in df.columns if c in (
        "Fuel_Type", "Transmission", "Mileage", "Engine_CC",
        "Seating_Capacity", "Service_Cost", "Segment"
    )]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
        print(f"\nDropped redundant columns: {cols_to_drop}")
    
    # Save cleaned dataset
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*60}")
    print("Dataset Fixing Completed!")
    print(f"{'='*60}")
    print(f"Final dataset shape: {df.shape}")
    print(f"Electric cars (real): {len(df[df['Fuel_Type_Clean'] == 'Electric'])}")
    print(f"Electric cars removed from non-EVs: {electric_removed}")
    print(f"Seating capacity fixed: {seating_fixed}")
    
    # Verify fixes
    print("\nVerification:")
    for brand, model in [("Hyundai", "i10"), ("Maruti Suzuki", "Baleno"), ("Maruti Suzuki", "WagonR")]:
        model_data = df[(df['Brand'] == brand) & (df['Model'] == model)]
        fuel_types = model_data['Fuel_Type_Clean'].unique()
        seats = model_data['Seating_Capacity_Clean'].mode().iloc[0] if len(model_data['Seating_Capacity_Clean'].mode()) > 0 else None
        print(f"  {brand} {model}: Fuel types = {list(fuel_types)}, Seating = {seats}")
    
    return df

if __name__ == "__main__":
    input_file = "car_dataset_india_cleaned.csv"
    output_file = "car_dataset_india_cleaned.csv"
    
    df = fix_dataset(input_file, output_file)
    print("\n✅ All fixes applied successfully!")

