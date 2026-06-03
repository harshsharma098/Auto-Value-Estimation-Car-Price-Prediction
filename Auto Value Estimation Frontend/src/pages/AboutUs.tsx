import Navbar from "@/components/Navbar";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { User, GraduationCap, Building2, Code } from "lucide-react";

const AboutUs = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto space-y-12">
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-4">About Us</h1>
            <p className="text-muted-foreground text-lg">AutoValue — Used Car Price Estimation</p>
          </div>

          <div className="rounded-xl border border-border bg-card p-6 md:p-8 shadow-sm">
            <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
              <Code className="w-5 h-5 text-primary" />
              About the Project
            </h2>
            <p className="text-muted-foreground leading-relaxed mb-4">
              <strong>AutoValue</strong> is a full-stack web application that estimates the market value of used cars in India. 
              It uses machine learning (XGBoost/LightGBM) trained on Indian car data and blends predictions with real market 
              reference prices (base-model ex-showroom 2024–2025) so that estimates stay aligned with current trends.
            </p>
            <p className="text-muted-foreground leading-relaxed mb-4">
              The app supports multiple fuel types (Petrol, Diesel, CNG, Electric), applies age-based depreciation, 
              and adjusts for factors like km driven, battery health (for EVs), mileage, and service cost. 
              Built with React, TypeScript, Flask, and Python ML stack.
            </p>
          </div>

          <div className="rounded-xl border border-border bg-card p-6 md:p-8 shadow-sm">
            <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-primary" />
              Project Owner
            </h2>
            <div className="space-y-3 text-foreground">
              <p className="text-lg font-semibold">Harsh Sharma</p>
              <div className="flex flex-wrap items-center gap-4 text-muted-foreground">
                <span className="flex items-center gap-2">
                  <GraduationCap className="w-4 h-4" />
                  B.Tech CSE
                </span>
                <span className="flex items-center gap-2">
                  <Building2 className="w-4 h-4" />
                  Sharda University
                </span>
              </div>
              <p className="text-sm text-muted-foreground pt-2">
                Software Programmer at Telgoo5, I actively support backend and system-level development by utilizing my skills in Artificial Intelligence, Prompt Engineering, and advanced programming languages like C++ and Python. My contributions focus on delivering efficient and scalable technical solutions.
              </p>
              <p className="text-sm text-muted-foreground">
                Pursuing a Bachelor of Technology in Computer Science Engineering at Sharda University, I aim to complement my academic knowledge with professional experiences to drive innovation. My dedication lies in leveraging AI and programming to enhance backend systems and create impactful, data-driven technological advancements.
              </p>
            </div>
          </div>

          <div className="text-center pt-4">
            <Link to="/estimate">
              <Button size="lg">Estimate Car Value</Button>
            </Link>
          </div>
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

export default AboutUs;
