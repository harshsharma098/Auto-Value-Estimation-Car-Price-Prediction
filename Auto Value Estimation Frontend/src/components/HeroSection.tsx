import { CheckCircle2 } from "lucide-react";
import heroImage from "@/assets/hero-bg.jpg";

const HeroSection = () => {
  return (
    <section className="relative min-h-[600px] flex items-center overflow-hidden">
      {/* GIF Background Layer (enhanced visibility) */}
      <div className="absolute inset-0 z-0">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: "image-set(url('/Sports%20Car%20GIF%20by%20FaZe%20Clan.gif') 1x, url('/Sports%20Car%20GIF%20by%20FaZe%20Clan.gif') 2x)",
            backgroundSize: "cover",
            backgroundRepeat: "no-repeat",
            zIndex: 0,
            filter: "contrast(1.28) saturate(1.22) brightness(1.06)",
            imageRendering: "-webkit-optimize-contrast",
            WebkitImageRendering: "-webkit-optimize-contrast",
            MozImageRendering: "crisp-edges",
            imageRendering: "crisp-edges"
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-secondary/25 via-secondary/20 to-secondary/10" style={{ zIndex: 1 }}></div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-16 relative z-10">
        <div className="max-w-2xl">
          <h1 className="text-5xl md:text-6xl font-bold text-secondary-foreground mb-6 leading-tight">
            Get Your Car's{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              True Value
            </span>{" "}
            Instantly
          </h1>
          
          <p className="text-xl text-secondary-foreground/90 mb-8 leading-relaxed">
            Powered by advanced AI algorithms, get an accurate market valuation for your car in seconds
          </p>

          <div className="space-y-4 mb-8">
            <div className="flex items-center gap-3">
              <div className="bg-primary/20 rounded-full p-1">
                <CheckCircle2 className="h-5 w-5 text-primary" />
              </div>
              <span className="text-secondary-foreground font-medium">Free instant valuation</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="bg-primary/20 rounded-full p-1">
                <CheckCircle2 className="h-5 w-5 text-primary" />
              </div>
              <span className="text-secondary-foreground font-medium">Based on real market data</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="bg-primary/20 rounded-full p-1">
                <CheckCircle2 className="h-5 w-5 text-primary" />
              </div>
              <span className="text-secondary-foreground font-medium">Quick & accurate results</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
