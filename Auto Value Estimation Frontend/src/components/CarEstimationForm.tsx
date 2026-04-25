import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Calculator, Loader2 } from "lucide-react";
import { toast } from "sonner";

// API base URL - change this to your backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5001";

interface FormData {
  Brand: string;
  Model: string;
  Year: string;
  Fuel_Type_Clean: string;
  Transmission_Clean: string;
  Mileage_Clean: string;
  Engine_CC_Clean: string;
  Seating_Capacity_Clean: string;
  Service_Cost_Clean: string;
  Km_Driven: string;
  Battery_Charge_Level?: string;
  Battery_Specific_Gravity?: string;
}

interface Options {
  brands: string[];
  models: string[];
  fuel_types: string[];
  transmissions: string[];
  year_range: { min: number; max: number };
  mileage_range: { min: number; max: number };
  ev_range?: { min: number; max: number };
  engine_range: { min: number; max: number };
  seats_range: { min: number; max: number };
  service_range: { min: number; max: number };
}

// Function to calculate battery charge level from specific gravity (interpolated)
const calculateChargeLevelFromGravity = (sg: number): number => {
  // Specific gravity ranges and corresponding charge levels
  // Fully charged: 1.265 - 1.285 (100%)
  // 75% charged: ~1.225 (75%)
  // 50% charged: ~1.190 (50%)
  // 25% charged: ~1.155 (25%)
  // Discharged: 1.120 or less (0%)
  
  if (sg >= 1.285) return 100;
  if (sg <= 1.120) return 0;
  
  // Interpolate between ranges
  if (sg >= 1.265 && sg < 1.285) {
    // Between 100% (1.265) and 100% (1.285) - fully charged range
    return 100;
  } else if (sg >= 1.225 && sg < 1.265) {
    // Between 75% (1.225) and 100% (1.265)
    const ratio = (sg - 1.225) / (1.265 - 1.225);
    return 75 + (ratio * 25); // Interpolate from 75% to 100%
  } else if (sg >= 1.190 && sg < 1.225) {
    // Between 50% (1.190) and 75% (1.225)
    const ratio = (sg - 1.190) / (1.225 - 1.190);
    return 50 + (ratio * 25); // Interpolate from 50% to 75%
  } else if (sg >= 1.155 && sg < 1.190) {
    // Between 25% (1.155) and 50% (1.190)
    const ratio = (sg - 1.155) / (1.190 - 1.155);
    return 25 + (ratio * 25); // Interpolate from 25% to 50%
  } else if (sg >= 1.120 && sg < 1.155) {
    // Between 0% (1.120) and 25% (1.155)
    const ratio = (sg - 1.120) / (1.155 - 1.120);
    return 0 + (ratio * 25); // Interpolate from 0% to 25%
  }
  
  return 0; // Default fallback
};

const CarEstimationForm = () => {
  const [formData, setFormData] = useState<FormData>({
    Brand: "",
    Model: "",
    Year: "",
    Fuel_Type_Clean: "",
    Transmission_Clean: "",
    Mileage_Clean: "",
    Engine_CC_Clean: "",
    Seating_Capacity_Clean: "",
    Service_Cost_Clean: "",
    Km_Driven: "",
    Battery_Charge_Level: "",
    Battery_Specific_Gravity: "",
  });

  const [options, setOptions] = useState<Options | null>(null);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [availableFuelTypes, setAvailableFuelTypes] = useState<string[]>([]);
  const [modelSpecs, setModelSpecs] = useState<{
    engine_cc: number | null;
    seating_capacity: number | null;
    avg_mileage: number | null;
    avg_service_cost: number | null;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [predicting, setPredicting] = useState(false);
  const [prediction, setPrediction] = useState<number | null>(null);
  const [predictionAge, setPredictionAge] = useState<number | null>(null);
  const [depreciationApplied, setDepreciationApplied] = useState<string | null>(null);

  // Load options from API
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/options`);
        if (response.ok) {
          const data = await response.json();
          setOptions(data);
        } else {
          toast.error("Failed to load form options");
        }
      } catch (error) {
        console.error("Error fetching options:", error);
        toast.error("Could not connect to backend API. Make sure the server is running.");
      }
    };
    fetchOptions();
  }, []);

  // Load models when brand changes
  useEffect(() => {
    const fetchModels = async () => {
      if (!formData.Brand) {
        setAvailableModels([]);
        setAvailableFuelTypes([]);
        setFormData((prev) => ({ ...prev, Model: "", Fuel_Type_Clean: "" }));
        return;
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/models?brand=${encodeURIComponent(formData.Brand)}`);
        if (response.ok) {
          const data = await response.json();
          setAvailableModels(data.models);
          setFormData((prev) => ({ ...prev, Model: "", Fuel_Type_Clean: "" })); // Reset model and fuel type when brand changes
        }
      } catch (error) {
        console.error("Error fetching models:", error);
      }
    };
    fetchModels();
  }, [formData.Brand]);

  // Load fuel types when model changes
  useEffect(() => {
    const fetchFuelTypes = async () => {
      if (!formData.Brand || !formData.Model) {
        setAvailableFuelTypes([]);
        setModelSpecs(null);
        setFormData((prev) => ({ ...prev, Fuel_Type_Clean: "", Engine_CC_Clean: "", Seating_Capacity_Clean: "" }));
        return;
      }

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/fuel-types?brand=${encodeURIComponent(formData.Brand)}&model=${encodeURIComponent(formData.Model)}`
        );
        if (response.ok) {
          const data = await response.json();
          setAvailableFuelTypes(data.fuel_types);
          // Reset fuel type if current selection is not available
          setFormData((prev) => {
            if (prev.Fuel_Type_Clean && !data.fuel_types.includes(prev.Fuel_Type_Clean)) {
              return { ...prev, Fuel_Type_Clean: "", Engine_CC_Clean: "", Seating_Capacity_Clean: "", Mileage_Clean: "", Service_Cost_Clean: "" };
            }
            return prev;
          });
        }
      } catch (error) {
        console.error("Error fetching fuel types:", error);
      }
    };
    fetchFuelTypes();
  }, [formData.Brand, formData.Model]);

  // Load model specs when fuel type is selected
  useEffect(() => {
    const fetchModelSpecs = async () => {
      if (!formData.Brand || !formData.Model || !formData.Fuel_Type_Clean) {
        setModelSpecs(null);
        return;
      }

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/model-specs?brand=${encodeURIComponent(formData.Brand)}&model=${encodeURIComponent(formData.Model)}&fuel_type=${encodeURIComponent(formData.Fuel_Type_Clean)}`
        );
        if (response.ok) {
          const data = await response.json();
          setModelSpecs(data);
          
          // Auto-fill Engine CC and Seating Capacity (fixed specs from dataset)
          if (data.engine_cc !== null && data.engine_cc !== undefined) {
            setFormData((prev) => ({
              ...prev,
              Engine_CC_Clean: data.engine_cc.toString(),
            }));
          }
          
          if (data.seating_capacity !== null && data.seating_capacity !== undefined) {
            setFormData((prev) => ({
              ...prev,
              Seating_Capacity_Clean: data.seating_capacity.toString(),
            }));
          }
          
          // Auto-fill average mileage and service cost as defaults if empty
          if (data.avg_mileage !== null && !formData.Mileage_Clean) {
            setFormData((prev) => ({
              ...prev,
              Mileage_Clean: data.avg_mileage.toString(),
            }));
          }
          
          if (data.avg_service_cost !== null && !formData.Service_Cost_Clean) {
            setFormData((prev) => ({
              ...prev,
              Service_Cost_Clean: data.avg_service_cost.toString(),
            }));
          }
        }
      } catch (error) {
        console.error("Error fetching model specs:", error);
      }
    };
    fetchModelSpecs();
  }, [formData.Brand, formData.Model, formData.Fuel_Type_Clean]);

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => {
      const updated = { ...prev, [field]: value };
      
      // If fuel type changes, reset specs (they will be auto-filled by useEffect)
      if (field === "Fuel_Type_Clean") {
        updated.Engine_CC_Clean = "";
        updated.Seating_Capacity_Clean = "";
        updated.Battery_Charge_Level = "";
        updated.Battery_Specific_Gravity = "";
        
        // If fuel type is electric, set engine CC to 0 immediately
        if (value === "Electric") {
          updated.Engine_CC_Clean = "0";
        }
      }
      
      // Prevent manual changes to Engine CC if it's auto-filled
      if (field === "Engine_CC_Clean" && modelSpecs?.engine_cc !== null && modelSpecs?.engine_cc !== undefined) {
        // Don't allow changes if it's a fixed spec
        if (formData.Fuel_Type_Clean !== "Electric") {
          return prev; // Keep the auto-filled value
        }
      }
      
      // Prevent manual changes to Seating Capacity if it's auto-filled
      if (field === "Seating_Capacity_Clean" && modelSpecs?.seating_capacity !== null && modelSpecs?.seating_capacity !== undefined) {
        return prev; // Keep the auto-filled value
      }
      
      // Auto-calculate charge level from specific gravity (interpolated)
      if (field === "Battery_Specific_Gravity" && value) {
        const sg = parseFloat(value);
        if (!isNaN(sg)) {
          const chargeLevel = calculateChargeLevelFromGravity(sg);
          updated.Battery_Charge_Level = chargeLevel.toFixed(1);
        }
      }
      
      return updated;
    });
    // Clear prediction when any field changes so user sees impact of their changes
    setPrediction(null);
    setPredictionAge(null);
    setDepreciationApplied(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    const requiredFields: (keyof FormData)[] = [
      "Brand", "Model", "Year", "Fuel_Type_Clean", "Transmission_Clean",
      "Mileage_Clean", "Engine_CC_Clean", "Seating_Capacity_Clean", "Service_Cost_Clean"
    ];
    
    const emptyFields = requiredFields.filter((field) => !formData[field]);
    
    if (emptyFields.length > 0) {
      toast.error("Please fill in all fields");
      return;
    }

    setPredicting(true);
    setPrediction(null);
    setPredictionAge(null);
    setDepreciationApplied(null);

    try {
      // Prepare submission data
      const submitData: any = { ...formData };
      if (formData.Km_Driven.trim() !== "") {
        submitData.Km_Driven = formData.Km_Driven.trim();
      }
      // For electric cars, include battery data
      if (formData.Fuel_Type_Clean === "Electric") {
        if (formData.Battery_Charge_Level) {
          submitData.Battery_Charge_Level = parseFloat(formData.Battery_Charge_Level);
        }
        if (formData.Battery_Specific_Gravity) {
          submitData.Battery_Specific_Gravity = parseFloat(formData.Battery_Specific_Gravity);
        }
      }
      
      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(submitData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Prediction failed");
      }

      const data = await response.json();
      setPrediction(data.predicted_price);
      if (data.age !== undefined) {
        setPredictionAge(data.age);
      }
      if (data.depreciation_applied) {
        setDepreciationApplied(data.depreciation_applied);
      }
      toast.success("Price calculated successfully!");
    } catch (error: any) {
      console.error("Prediction error:", error);
      toast.error(error.message || "Failed to calculate price. Please try again.");
    } finally {
      setPredicting(false);
    }
  };

  const currentYear = new Date().getFullYear();
  const years = options
    ? Array.from({ length: options.year_range.max - options.year_range.min + 1 }, (_, i) => 
        options.year_range.max - i
      )
    : Array.from({ length: 30 }, (_, i) => currentYear - i);

  return (
    <Card className="relative w-full max-w-2xl border-border rounded-xl card-3d shine shadow-2xl bg-gradient-to-br from-background to-muted/20">
      <CardHeader className="text-center pb-6">
        <div className="mx-auto mb-4 w-fit bg-gradient-to-br from-primary/20 to-primary/10 p-4 rounded-full shadow-lg animate-pulse">
          <Calculator className="h-10 w-10 text-primary" />
        </div>
        <CardTitle className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mb-2">
          Get Your Car's Value
        </CardTitle>
        <CardDescription className="text-base">Fill in the details below to get an instant, accurate estimate</CardDescription>
      </CardHeader>
      <CardContent className="pt-2">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="space-y-2">
              <Label htmlFor="brand" className="font-semibold">
                Brand *
              </Label>
              <Select 
                value={formData.Brand} 
                onValueChange={(value) => handleInputChange("Brand", value)}
                disabled={!options}
              >
                <SelectTrigger className="bg-background input-3d h-11 transition-all duration-200 hover:border-primary/50 focus:ring-2 focus:ring-primary/50">
                  <SelectValue placeholder="Select brand" />
                </SelectTrigger>
                <SelectContent>
                  {options?.brands.map((brand) => (
                    <SelectItem key={brand} value={brand}>
                      {brand}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="model" className="font-semibold">
                Model *
              </Label>
              <Select 
                value={formData.Model} 
                onValueChange={(value) => handleInputChange("Model", value)}
                disabled={!formData.Brand || availableModels.length === 0}
              >
                <SelectTrigger className="bg-background input-3d h-11 transition-all duration-200 hover:border-primary/50 focus:ring-2 focus:ring-primary/50">
                  <SelectValue placeholder={formData.Brand ? "Select model" : "Select brand first"} />
                </SelectTrigger>
                <SelectContent>
                  {availableModels.map((model) => (
                    <SelectItem key={model} value={model}>
                      {model}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="year" className="font-semibold">
                Model Year *
              </Label>
              <Select value={formData.Year} onValueChange={(value) => handleInputChange("Year", value)}>
                <SelectTrigger className="bg-background input-3d h-11 transition-all duration-200 hover:border-primary/50 focus:ring-2 focus:ring-primary/50">
                  <SelectValue placeholder="Select year" />
                </SelectTrigger>
                <SelectContent>
                  {years.map((year) => (
                    <SelectItem key={year} value={year.toString()}>
                      {year}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {formData.Year && (
                <p className="text-xs text-foreground/85">
                  Car age: {currentYear - parseInt(formData.Year)} {currentYear - parseInt(formData.Year) === 1 ? 'year' : 'years'} old
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="fuel" className="font-semibold">
                Fuel Type *
              </Label>
              <Select 
                value={formData.Fuel_Type_Clean} 
                onValueChange={(value) => handleInputChange("Fuel_Type_Clean", value)}
                disabled={!formData.Model || availableFuelTypes.length === 0}
              >
                <SelectTrigger className="bg-background input-3d h-11 transition-all duration-200 hover:border-primary/50 focus:ring-2 focus:ring-primary/50">
                  <SelectValue placeholder={
                    !formData.Model 
                      ? "Select model first" 
                      : availableFuelTypes.length === 0 
                        ? "Loading fuel types..." 
                        : "Select fuel type"
                  } />
                </SelectTrigger>
                <SelectContent>
                  {availableFuelTypes.length > 0 ? (
                    availableFuelTypes.map((fuel) => (
                      <SelectItem key={fuel} value={fuel}>
                        {fuel}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="none" disabled>No fuel types available</SelectItem>
                  )}
                </SelectContent>
              </Select>
              {formData.Model && availableFuelTypes.length > 0 && (
                <p className="text-xs text-foreground/85">
                  Available variants: {availableFuelTypes.join(", ")}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="transmission" className="font-semibold">
                Transmission *
              </Label>
              <Select 
                value={formData.Transmission_Clean} 
                onValueChange={(value) => handleInputChange("Transmission_Clean", value)}
                disabled={!options}
              >
                <SelectTrigger className="bg-background input-3d h-11 transition-all duration-200 hover:border-primary/50 focus:ring-2 focus:ring-primary/50">
                  <SelectValue placeholder="Select transmission" />
                </SelectTrigger>
                <SelectContent>
                  {options?.transmissions.map((trans) => (
                    <SelectItem key={trans} value={trans}>
                      {trans}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="mileage">
                {formData.Fuel_Type_Clean === "Electric" ? "Range (km) *" : "Mileage (kmpl) *"}
              </Label>
              <Input
                id="mileage"
                type="number"
                step={formData.Fuel_Type_Clean === "Electric" ? "1" : "0.1"}
                placeholder={
                  formData.Fuel_Type_Clean === "Electric"
                    ? options?.ev_range
                      ? `e.g., ${options.ev_range.min} - ${options.ev_range.max} km`
                      : "e.g., 200 - 600 km"
                    : options
                    ? `e.g., ${options.mileage_range.min.toFixed(1)} - ${options.mileage_range.max.toFixed(1)} kmpl`
                    : "e.g., 18.5 kmpl"
                }
                value={formData.Mileage_Clean}
                onChange={(e) => handleInputChange("Mileage_Clean", e.target.value)}
                className="bg-background input-3d transition-all duration-200 focus:ring-2 focus:ring-primary/50"
                min={formData.Fuel_Type_Clean === "Electric" ? (options?.ev_range?.min ?? 200) : options?.mileage_range.min}
                max={formData.Fuel_Type_Clean === "Electric" ? (options?.ev_range?.max ?? 600) : options?.mileage_range.max}
              />
              {formData.Fuel_Type_Clean === "Electric" ? (
                <p className="text-xs text-foreground/85">
                  Enter the driving range on a full charge (typically 200-600 km for EVs). Lower range = lower price.
                </p>
              ) : (
                <p className="text-xs text-foreground/85">
                  Enter fuel efficiency in kilometers per liter. Lower mileage = lower price (worse condition).
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="engine" className="font-semibold">
                Engine CC *
              </Label>
              <Input
                id="engine"
                type="number"
                placeholder={formData.Fuel_Type_Clean === "Electric" ? "0 (Electric vehicles)" : modelSpecs?.engine_cc ? `${modelSpecs.engine_cc} (Auto-filled from dataset)` : "Loading..."}
                value={formData.Engine_CC_Clean}
                onChange={(e) => handleInputChange("Engine_CC_Clean", e.target.value)}
                className="bg-background input-3d h-11 transition-all duration-200 focus:ring-2 focus:ring-primary/50"
                min={options?.engine_range.min}
                max={options?.engine_range.max}
                disabled={formData.Fuel_Type_Clean === "Electric" || (modelSpecs?.engine_cc !== null && modelSpecs?.engine_cc !== undefined)}
                readOnly={formData.Fuel_Type_Clean !== "Electric" && modelSpecs?.engine_cc !== null && modelSpecs?.engine_cc !== undefined}
              />
              {formData.Fuel_Type_Clean === "Electric" ? (
                <p className="text-xs text-foreground/85">Electric vehicles have 0 Engine CC (fixed)</p>
              ) : modelSpecs?.engine_cc !== null && modelSpecs?.engine_cc !== undefined ? (
                <p className="text-xs text-foreground/85">Fixed specification extracted from dataset for {formData.Brand} {formData.Model} {formData.Fuel_Type_Clean}</p>
              ) : formData.Fuel_Type_Clean ? (
                <p className="text-xs text-foreground/85">Loading engine specification from dataset...</p>
              ) : (
                <p className="text-xs text-foreground/85">Select fuel type to auto-fill engine specification</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="seats" className="font-semibold">
                Seating Capacity *
              </Label>
              <Select 
                value={formData.Seating_Capacity_Clean} 
                onValueChange={(value) => handleInputChange("Seating_Capacity_Clean", value)}
                disabled={!options || (modelSpecs?.seating_capacity !== null && modelSpecs?.seating_capacity !== undefined)}
              >
                <SelectTrigger className="bg-background input-3d h-11 transition-all duration-200 hover:border-primary/50 focus:ring-2 focus:ring-primary/50">
                  <SelectValue placeholder={
                    modelSpecs?.seating_capacity !== null && modelSpecs?.seating_capacity !== undefined
                      ? `${modelSpecs.seating_capacity} (Auto-filled from dataset)`
                      : formData.Fuel_Type_Clean
                      ? "Loading..."
                      : "Select fuel type first"
                  } />
                </SelectTrigger>
                <SelectContent>
                  {options && Array.from({ length: options.seats_range.max - options.seats_range.min + 1 }, (_, i) => 
                    options.seats_range.min + i
                  ).map((seat) => (
                    <SelectItem key={seat} value={seat.toString()}>
                      {seat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {modelSpecs?.seating_capacity !== null && modelSpecs?.seating_capacity !== undefined ? (
                <p className="text-xs text-foreground/85">Fixed specification extracted from dataset for {formData.Brand} {formData.Model} {formData.Fuel_Type_Clean}</p>
              ) : formData.Fuel_Type_Clean ? (
                <p className="text-xs text-foreground/85">Loading seating capacity from dataset...</p>
              ) : (
                <p className="text-xs text-foreground/85">Select fuel type to auto-fill seating capacity</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="service" className="font-semibold">
                Service Cost (₹) *
              </Label>
              <Input
                id="service"
                type="number"
                step="100"
                placeholder={options ? `e.g., ${options.service_range.min.toLocaleString()} - ${options.service_range.max.toLocaleString()}` : "e.g., 10000"}
                value={formData.Service_Cost_Clean}
                onChange={(e) => handleInputChange("Service_Cost_Clean", e.target.value)}
                className="bg-background input-3d h-11 transition-all duration-200 focus:ring-2 focus:ring-primary/50"
                min={options?.service_range.min}
                max={options?.service_range.max}
              />
              <p className="text-xs text-foreground/85">
                Enter annual service cost in Indian Rupees. Higher service cost = lower price (more maintenance needed).
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="km_driven" className="font-semibold">
                Km Driven (Odometer)
              </Label>
              <Input
                id="km_driven"
                type="number"
                step="1000"
                placeholder="e.g., 45000"
                value={formData.Km_Driven}
                onChange={(e) => handleInputChange("Km_Driven", e.target.value)}
                className="bg-background input-3d h-11 transition-all duration-200 focus:ring-2 focus:ring-primary/50"
                min={0}
              />
              <p className="text-xs text-foreground/85">
                Total kilometers driven (odometer reading). As km driven increases, estimated price decreases. Optional; leave blank if unknown.
              </p>
            </div>
          </div>

          {/* Battery Charge Level Fields (for Electric Cars only) */}
          {formData.Fuel_Type_Clean === "Electric" && availableFuelTypes.includes("Electric") && (
            <div className="mt-6 p-5 bg-gradient-to-br from-primary/10 via-primary/5 to-accent/5 border-2 border-primary/30 rounded-xl shadow-lg">
              <h3 className="text-base font-bold mb-4 text-primary">
                Battery Information (Electric Vehicles)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="battery_sg">Battery Specific Gravity</Label>
                  <Input
                    id="battery_sg"
                    type="number"
                    step="0.001"
                    placeholder="1.265 - 1.285 (Fully charged)"
                    value={formData.Battery_Specific_Gravity}
                    onChange={(e) => handleInputChange("Battery_Specific_Gravity", e.target.value)}
                    className="bg-background input-3d h-11 transition-all duration-200 focus:ring-2 focus:ring-primary/50"
                    min="1.100"
                    max="1.285"
                  />
                  <p className="text-xs text-foreground/85">
                    Lower specific gravity = lower battery health = lower car price. Range: 1.100 (Discharged) - 1.285 (Fully charged)
                  </p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="battery_charge">Battery Charge Level (%)</Label>
                  <Input
                    id="battery_charge"
                    type="number"
                    step="0.1"
                    placeholder="0 - 100"
                    value={formData.Battery_Charge_Level}
                    onChange={(e) => handleInputChange("Battery_Charge_Level", e.target.value)}
                    className="bg-background input-3d h-11 transition-all duration-200 focus:ring-2 focus:ring-primary/50"
                    min="0"
                    max="100"
                    readOnly={!!formData.Battery_Specific_Gravity && formData.Battery_Specific_Gravity !== ""}
                  />
                  <p className="text-xs text-foreground/85">
                    {formData.Battery_Specific_Gravity 
                      ? "Auto-calculated from Specific Gravity"
                      : "Enter charge level manually or use Specific Gravity"}
                  </p>
                </div>
              </div>
              <div className="mt-3 text-xs text-foreground/85 space-y-1">
                <p><strong>Charge Level Guide:</strong></p>
                <p>• Battery Specific Gravity and battery % directly affect price: as either decreases, estimated value decreases.</p>
                <p>• Fully charged: 1.265 - 1.285 (100%)</p>
                <p>• 75% charged: ~1.225 (75%)</p>
                <p>• 50% charged: ~1.190 (50%)</p>
                <p>• 25% charged: ~1.155 (25%)</p>
                <p>• Discharged: 1.120 or less (0%)</p>
              </div>
            </div>
          )}

          {prediction !== null && (
            <div className="mt-8 p-6 bg-gradient-to-br from-primary/15 via-primary/10 to-accent/10 border-2 border-primary/30 rounded-xl shadow-xl animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="text-center">
                <p className="text-sm font-medium text-foreground mb-2 uppercase tracking-wide">Estimated Car Value</p>
                <p className="text-4xl md:text-5xl font-bold text-foreground">
                  ₹ {prediction.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                </p>
              </div>
            </div>
          )}

          <Button 
            type="submit" 
            variant="hero" 
            size="lg" 
            className="w-full mt-8 h-12 text-base font-semibold btn-glow shadow-lg hover:shadow-xl transition-all duration-300"
            disabled={predicting || !options}
          >
            {predicting ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Calculating...
              </>
            ) : (
              <>
                <Calculator className="mr-2 h-5 w-5" />
                Calculate Car Value
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default CarEstimationForm;

