import Navbar from "@/components/Navbar";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Car } from "lucide-react";

const BuyCars = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <Car className="w-16 h-16 mx-auto text-primary mb-6" />
          <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-4">Buy Cars</h1>
          <p className="text-muted-foreground text-lg mb-8">
            Find your next car from a wide selection of verified used cars. Browse by brand, budget, and fuel type.
          </p>
          <p className="text-sm text-muted-foreground mb-8">
            This section is coming soon. Use <strong>Estimate Value</strong> to check the fair price of a car before you buy.
          </p>
          <Link to="/estimate">
            <Button size="lg" className="gap-2">
              <Car className="w-5 h-5" />
              Estimate Car Value
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

export default BuyCars;
