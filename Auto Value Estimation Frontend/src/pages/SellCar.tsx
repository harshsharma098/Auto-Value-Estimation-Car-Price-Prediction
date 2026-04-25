import Navbar from "@/components/Navbar";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Calculator } from "lucide-react";

const SellCar = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <Calculator className="w-16 h-16 mx-auto text-primary mb-6" />
          <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-4">Sell Car</h1>
          <p className="text-muted-foreground text-lg mb-8">
            Get a fair, data-driven estimate for your car before you sell. Know your car’s value in minutes.
          </p>
          <p className="text-sm text-muted-foreground mb-8">
            Use our <strong>Estimate Value</strong> tool to see the market-aligned price for your car based on brand, model, year, and condition.
          </p>
          <Link to="/estimate">
            <Button size="lg" className="gap-2">
              <Calculator className="w-5 h-5" />
              Get Your Car’s Value
            </Button>
          </Link>
        </div>
      </section>
      <footer className="bg-secondary text-secondary-foreground py-8 mt-16">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm">© 2025 AutoValue. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default SellCar;
