import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import CarEstimationForm from "@/components/CarEstimationForm";
import CarBrands from "@/components/CarBrands";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <HeroSection />
      
      <section className="py-16 bg-background">
        <div className="container mx-auto px-4">
          <div className="flex justify-center">
            <CarEstimationForm />
          </div>
        </div>
      </section>

      <CarBrands />

      <footer className="bg-secondary text-secondary-foreground py-8 mt-16">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm">
            © 2025 AutoValue. All rights reserved. Powered by advanced AI technology.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
