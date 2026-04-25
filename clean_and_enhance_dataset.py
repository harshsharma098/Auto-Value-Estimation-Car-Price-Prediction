"""
Script to clean dataset and add battery charge level for electric cars
Fixes electric car data inconsistencies and adds real Indian EV models
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Battery charge level mapping based on specific gravity
# Specific Gravity -> Charge Level
BATTERY_CHARGE_LEVELS = {
    "Fully charged": {"min": 1.265, "max": 1.285, "value": 100},
    "75% charged": {"min": 1.220, "max": 1.230, "value": 75},
    "50% charged": {"min": 1.185, "max": 1.195, "value": 50},
    "25% charged": {"min": 1.150, "max": 1.160, "value": 25},
    "Discharged": {"min": 1.100, "max": 1.120, "value": 0}
}

def get_charge_level_from_specific_gravity(sg):
    """Convert specific gravity to charge level percentage"""
    if pd.isna(sg) or sg == 0:
        return 75  # Default to 75% for unknown
    
    for level_name, level_data in BATTERY_CHARGE_LEVELS.items():
        if level_data["min"] <= sg <= level_data["max"]:
            return level_data["value"]
    
    # Interpolate for values between ranges
    if sg > 1.285:
        return 100
    elif sg < 1.100:
        return 0
    elif 1.230 < sg < 1.265:
        return 87.5  # Between 75% and 100%
    elif 1.195 < sg < 1.220:
        return 62.5  # Between 50% and 75%
    elif 1.160 < sg < 1.185:
        return 37.5  # Between 25% and 50%
    elif 1.120 < sg < 1.150:
        return 12.5  # Between 0% and 25%
    
    return 75  # Default

def is_real_electric_car(brand, model):
    """Check if this is a real electric car model in India"""
    real_evs = {
        "Tata Motors": ["Nexon EV", "Tigor EV", "Tiago EV", "Punch EV"],
        "Mahindra": ["XUV400", "eVerito"],
        "Hyundai": ["Kona Electric", "Ioniq 5"],
        "MG": ["ZS EV", "Comet EV", "Astor"],
        "BYD": ["e6"],
        "Kia": ["EV6"],
        "Mercedes-Benz": ["EQC"],
        "Audi": ["e-tron"],
        "Jaguar": ["I-PACE"],
        "BMW": ["iX", "i4"],
        "Volvo": ["XC40 Recharge"],
        "Citroen": ["eC3"],
        "Nissan": ["Leaf"]
    }
    
    return brand in real_evs and model in real_evs[brand]

def clean_dataset(input_file, output_file):
    """Clean and enhance the dataset"""
    print("Loading dataset...")
    df = pd.read_csv(input_file)
    
    print(f"Original dataset shape: {df.shape}")
    
    # Create Battery_Charge_Level column (NaN for non-electric, will be filled)
    df['Battery_Charge_Level'] = np.nan
    df['Battery_Specific_Gravity'] = np.nan
    
    # Fix electric car inconsistencies
    print("\nFixing electric car data inconsistencies...")
    
    # List of cars that should NOT be electric (based on real models)
    # Format: (Brand, Model): (correct_fuel_type, correct_seating_capacity)
    non_electric_models = {
        ("Honda", "Amaze"): ("Petrol", 5),
        ("Honda", "City"): ("Petrol", 5),
        ("Honda", "Jazz"): ("Petrol", 5),
        ("Honda", "Civic"): ("Petrol", 5),
        ("Honda", "WR-V"): ("Petrol", 5),
        ("Toyota", "Innova"): ("Diesel", 7),
        ("Toyota", "Glanza"): ("Petrol", 5),
        ("Toyota", "Fortuner"): ("Diesel", 7),
        ("Toyota", "Camry"): ("Petrol", 5),
        ("Toyota", "Urban Cruiser"): ("Petrol", 5),
        ("Maruti Suzuki", "Ertiga"): ("Petrol", 7),
        ("Maruti Suzuki", "Baleno"): ("Petrol", 5),
        ("Maruti Suzuki", "Dzire"): ("Petrol", 5),
        ("Maruti Suzuki", "Swift"): ("Petrol", 5),
        ("Maruti Suzuki", "WagonR"): ("Petrol", 5),
        ("Tata Motors", "Punch"): ("Petrol", 5),
        ("Tata Motors", "Altroz"): ("Petrol", 5),
        ("Tata Motors", "Harrier"): ("Diesel", 5),
        ("Tata Motors", "Tiago"): ("Petrol", 5),
        ("Tata Motors", "Nexon"): ("Petrol", 5),  # Regular Nexon (not EV)
        ("Mahindra", "Scorpio"): ("Diesel", 7),
        ("Mahindra", "XUV700"): ("Diesel", 7),
        ("Mahindra", "Thar"): ("Diesel", 4),
        ("Mahindra", "Bolero"): ("Diesel", 7),
        ("Mahindra", "XUV300"): ("Diesel", 5),
        ("Kia", "Sonet"): ("Petrol", 5),
        ("Kia", "Seltos"): ("Petrol", 5),
        ("Kia", "Carnival"): ("Diesel", 7),
        ("Kia", "Carens"): ("Petrol", 7),
        ("Hyundai", "Verna"): ("Petrol", 5),
        ("Hyundai", "Creta"): ("Petrol", 5),
        ("Hyundai", "Venue"): ("Petrol", 5),
        ("Hyundai", "i20"): ("Petrol", 5),
        ("Hyundai", "i10"): ("Petrol", 5),
        ("Skoda", "Kushaq"): ("Petrol", 5),
        ("Skoda", "Slavia"): ("Petrol", 5),
        ("Skoda", "Superb"): ("Petrol", 5),
        ("Skoda", "Octavia"): ("Petrol", 5),
        ("Skoda", "Rapid"): ("Petrol", 5),
        ("Volkswagen", "Taigun"): ("Petrol", 5),
        ("Volkswagen", "Polo"): ("Petrol", 5),
        ("Volkswagen", "Virtus"): ("Petrol", 5),
        ("Volkswagen", "Vento"): ("Petrol", 5),
        ("Volkswagen", "Tiguan"): ("Petrol", 5),
        ("Renault", "Kiger"): ("Petrol", 5),
        ("Renault", "Lodgy"): ("Diesel", 7),
        ("Renault", "Kwid"): ("Petrol", 5),
        ("Renault", "Duster"): ("Petrol", 5),
        ("Renault", "Triber"): ("Petrol", 7)
    }
    
    # Model-specific seating capacity (for models not in non_electric_models)
    # Format: (Brand, Model): seating_capacity
    model_seating_capacity = {
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
        ("Tata Motors", "Nexon"): 5,  # Regular Nexon
        ("Tata Motors", "Punch"): 5,
        ("Tata Motors", "Altroz"): 5,
        ("Tata Motors", "Tiago"): 5,
        ("Tata Motors", "Harrier"): 5,
        ("Mahindra", "Thar"): 4,
        ("Mahindra", "Scorpio"): 7,
        ("Mahindra", "XUV700"): 7,
        ("Mahindra", "XUV300"): 5,
        ("Kia", "Sonet"): 5,
        ("Kia", "Seltos"): 5,
        ("Kia", "Carens"): 7,
        ("Kia", "Carnival"): 7,
    }
    
    fixed_count = 0
    seating_fixed_count = 0
    
    for idx, row in df.iterrows():
        brand = row['Brand']
        model = row['Model']
        fuel_clean = row['Fuel_Type_Clean']
        
        # Fix incorrect electric classifications and seating capacity
        if (brand, model) in non_electric_models:
            correct_fuel, correct_seats = non_electric_models[(brand, model)]
            
            # Fix Electric fuel type
            if fuel_clean == "Electric":
                df.at[idx, 'Fuel_Type_Clean'] = correct_fuel
                df.at[idx, 'Engine_CC_Clean'] = row['Engine_CC'] if row['Engine_CC'] > 0 else 1500
                df.at[idx, 'Seating_Capacity_Clean'] = correct_seats
                df.at[idx, 'Battery_Charge_Level'] = np.nan
                df.at[idx, 'Battery_Specific_Gravity'] = np.nan
                fixed_count += 1
            
            # Fix seating capacity for this model
            if row['Seating_Capacity_Clean'] != correct_seats:
                df.at[idx, 'Seating_Capacity_Clean'] = correct_seats
                seating_fixed_count += 1
        
        # Fix seating capacity for other models
        elif (brand, model) in model_seating_capacity:
            correct_seats = model_seating_capacity[(brand, model)]
            if row['Seating_Capacity_Clean'] != correct_seats:
                df.at[idx, 'Seating_Capacity_Clean'] = correct_seats
                seating_fixed_count += 1
        
        # Remove Electric from any model that's not a real EV (catch-all)
        if fuel_clean == "Electric" and not is_real_electric_car(brand, model):
            # Find the most common fuel type for this model (excluding Electric and current row)
            model_data = df[(df['Brand'] == brand) & (df['Model'] == model) & (df['Fuel_Type_Clean'] != 'Electric') & (df.index != idx)]
            if len(model_data) > 0:
                most_common_fuel = model_data['Fuel_Type_Clean'].mode()
                if len(most_common_fuel) > 0:
                    correct_fuel = most_common_fuel.iloc[0]
                    df.at[idx, 'Fuel_Type_Clean'] = correct_fuel
                    
                    # Fix Engine CC if it's 0 (Electric default)
                    if row['Engine_CC_Clean'] == 0:
                        engine_data = model_data[model_data['Fuel_Type_Clean'] == correct_fuel]['Engine_CC_Clean']
                        if len(engine_data) > 0:
                            engine_mode = engine_data.mode()
                            if len(engine_mode) > 0:
                                df.at[idx, 'Engine_CC_Clean'] = int(engine_mode.iloc[0])
                            else:
                                df.at[idx, 'Engine_CC_Clean'] = int(engine_data.median())
                        else:
                            df.at[idx, 'Engine_CC_Clean'] = 1500  # Default
                    
                    df.at[idx, 'Battery_Charge_Level'] = np.nan
                    df.at[idx, 'Battery_Specific_Gravity'] = np.nan
                    fixed_count += 1
    
    print(f"Fixed {fixed_count} incorrect electric car classifications")
    print(f"Fixed {seating_fixed_count} incorrect seating capacity entries")
    
    # Add battery charge level for REAL electric cars
    print("\nAdding battery charge level for electric cars...")
    ev_count = 0
    
    for idx, row in df.iterrows():
        if row['Fuel_Type_Clean'] == 'Electric':
            # Only process if it's a real EV or keep existing data
            if is_real_electric_car(row['Brand'], row['Model']) or pd.isna(row['Battery_Charge_Level']):
                # Generate realistic specific gravity based on age and condition
                # Older EVs or those with more wear have lower charge capacity
                age = row['Age']
                
                # Simulate specific gravity (1.100 to 1.285)
                # Newer cars (age 0-2): 1.265-1.285 (fully charged)
                # Older cars (age 3-5): 1.220-1.250 (75% charged)
                # Very old (age 6+): 1.150-1.200 (25-50% charged)
                
                if age <= 2:
                    sg = np.random.uniform(1.265, 1.285)
                elif age <= 5:
                    sg = np.random.uniform(1.220, 1.250)
                else:
                    sg = np.random.uniform(1.150, 1.200)
                
                charge_level = get_charge_level_from_specific_gravity(sg)
                
                df.at[idx, 'Battery_Specific_Gravity'] = round(sg, 3)
                df.at[idx, 'Battery_Charge_Level'] = charge_level
                ev_count += 1
    
    print(f"Added battery data for {ev_count} electric cars")
    
    # Add new real Indian electric cars
    print("\nAdding new Indian electric car models...")
    new_evs = []
    current_year = datetime.now().year
    
    # Real Indian EV models with realistic pricing
    real_ev_data = [
        # Tata Motors EVs
        {"Brand": "Tata Motors", "Model": "Nexon EV", "Year": 2023, "Fuel_Type": "Electric", 
         "Transmission": "Automatic", "Mileage": 312.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 8000.0, "Segment": "SUV", "Price_Clean": 1450000.0},
        {"Brand": "Tata Motors", "Model": "Nexon EV", "Year": 2022, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 312.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 8500.0, "Segment": "SUV", "Price_Clean": 1320000.0},
        {"Brand": "Tata Motors", "Model": "Nexon EV", "Year": 2021, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 312.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 9000.0, "Segment": "SUV", "Price_Clean": 1180000.0},
        {"Brand": "Tata Motors", "Model": "Tigor EV", "Year": 2023, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 315.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 7500.0, "Segment": "Sedan", "Price_Clean": 1250000.0},
        {"Brand": "Tata Motors", "Model": "Tigor EV", "Year": 2022, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 315.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 8000.0, "Segment": "Sedan", "Price_Clean": 1120000.0},
        {"Brand": "Tata Motors", "Model": "Tiago EV", "Year": 2023, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 315.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 7000.0, "Segment": "Hatchback", "Price_Clean": 850000.0},
        {"Brand": "Tata Motors", "Model": "Tiago EV", "Year": 2022, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 315.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 7500.0, "Segment": "Hatchback", "Price_Clean": 780000.0},
        {"Brand": "Tata Motors", "Model": "Punch EV", "Year": 2024, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 320.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 7500.0, "Segment": "SUV", "Price_Clean": 1100000.0},
        
        # MG EVs
        {"Brand": "MG", "Model": "ZS EV", "Year": 2023, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 461.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 12000.0, "Segment": "SUV", "Price_Clean": 2200000.0},
        {"Brand": "MG", "Model": "ZS EV", "Year": 2022, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 461.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 13000.0, "Segment": "SUV", "Price_Clean": 1980000.0},
        {"Brand": "MG", "Model": "Comet EV", "Year": 2024, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 230.0, "Engine_CC": 0, "Seating_Capacity": 4,
         "Service_Cost": 6000.0, "Segment": "Hatchback", "Price_Clean": 780000.0},
        {"Brand": "MG", "Model": "Comet EV", "Year": 2023, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 230.0, "Engine_CC": 0, "Seating_Capacity": 4,
         "Service_Cost": 6500.0, "Segment": "Hatchback", "Price_Clean": 720000.0},
        
        # Mahindra EVs
        {"Brand": "Mahindra", "Model": "XUV400", "Year": 2023, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 456.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 11000.0, "Segment": "SUV", "Price_Clean": 1950000.0},
        {"Brand": "Mahindra", "Model": "XUV400", "Year": 2022, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 456.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 12000.0, "Segment": "SUV", "Price_Clean": 1780000.0},
        
        # Hyundai EVs
        {"Brand": "Hyundai", "Model": "Kona Electric", "Year": 2023, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 452.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 15000.0, "Segment": "SUV", "Price_Clean": 2450000.0},
        {"Brand": "Hyundai", "Model": "Kona Electric", "Year": 2022, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 452.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 16000.0, "Segment": "SUV", "Price_Clean": 2200000.0},
        {"Brand": "Hyundai", "Model": "Ioniq 5", "Year": 2024, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 631.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 18000.0, "Segment": "SUV", "Price_Clean": 4500000.0},
        
        # Citroen EVs
        {"Brand": "Citroen", "Model": "eC3", "Year": 2024, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 320.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 7000.0, "Segment": "Hatchback", "Price_Clean": 1150000.0},
        {"Brand": "Citroen", "Model": "eC3", "Year": 2023, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 320.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 7500.0, "Segment": "Hatchback", "Price_Clean": 1050000.0},
        
        # Kia EV6
        {"Brand": "Kia", "Model": "EV6", "Year": 2024, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 528.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 20000.0, "Segment": "SUV", "Price_Clean": 6200000.0},
        {"Brand": "Kia", "Model": "EV6", "Year": 2023, "Fuel_Type": "Electric",
         "Transmission": "Automatic", "Mileage": 528.0, "Engine_CC": 0, "Seating_Capacity": 5,
         "Service_Cost": 21000.0, "Segment": "SUV", "Price_Clean": 5800000.0},
    ]
    
    for ev_data in real_ev_data:
        age = current_year - ev_data['Year']
        
        # Generate battery charge level based on age
        if age <= 2:
            sg = np.random.uniform(1.265, 1.285)
        elif age <= 5:
            sg = np.random.uniform(1.220, 1.250)
        else:
            sg = np.random.uniform(1.150, 1.200)
        
        charge_level = get_charge_level_from_specific_gravity(sg)
        
        new_row = {
            'Car_ID': len(df) + len(new_evs) + 1,
            'Brand': ev_data['Brand'],
            'Model': ev_data['Model'],
            'Year': ev_data['Year'],
            'Fuel_Type': ev_data['Fuel_Type'],
            'Transmission': ev_data['Transmission'],
            'Mileage': ev_data['Mileage'],
            'Engine_CC': ev_data['Engine_CC'],
            'Seating_Capacity': ev_data['Seating_Capacity'],
            'Service_Cost': ev_data['Service_Cost'],
            'Segment': ev_data['Segment'],
            'Fuel_Type_Clean': 'Electric',
            'Transmission_Clean': ev_data['Transmission'],
            'Engine_CC_Clean': 0,
            'Mileage_Clean': ev_data['Mileage'],
            'Seating_Capacity_Clean': ev_data['Seating_Capacity'],
            'Service_Cost_Clean': ev_data['Service_Cost'],
            'Age': age,
            'Price_Clean': ev_data['Price_Clean'],
            'Battery_Specific_Gravity': round(sg, 3),
            'Battery_Charge_Level': charge_level
        }
        
        new_evs.append(new_row)
    
    # Add new EVs to dataframe
    new_evs_df = pd.DataFrame(new_evs)
    df = pd.concat([df, new_evs_df], ignore_index=True)
    
    print(f"Added {len(new_evs)} new electric car entries")
    
    # Ensure Battery_Charge_Level is NaN for non-electric cars
    df.loc[df['Fuel_Type_Clean'] != 'Electric', 'Battery_Charge_Level'] = np.nan
    df.loc[df['Fuel_Type_Clean'] != 'Electric', 'Battery_Specific_Gravity'] = np.nan
    
    # Save cleaned dataset
    df.to_csv(output_file, index=False)
    print(f"\nCleaned dataset saved to: {output_file}")
    print(f"Final dataset shape: {df.shape}")
    print(f"Electric cars: {len(df[df['Fuel_Type_Clean'] == 'Electric'])}")
    print(f"Cars with battery data: {df['Battery_Charge_Level'].notna().sum()}")
    
    return df

if __name__ == "__main__":
    input_file = "car_dataset_india_cleaned.csv"
    output_file = "car_dataset_india_cleaned.csv"
    
    print("=" * 60)
    print("Dataset Cleaning and Enhancement Script")
    print("=" * 60)
    
    df = clean_dataset(input_file, output_file)
    
    print("\n" + "=" * 60)
    print("Dataset cleaning completed successfully!")
    print("=" * 60)

