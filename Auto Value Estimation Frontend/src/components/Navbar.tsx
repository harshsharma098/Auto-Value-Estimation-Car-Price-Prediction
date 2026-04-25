import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import Logo3D from "@/components/Logo3D";

const Navbar = () => {
  return (
    <nav className="sticky top-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Logo3D />
          
          <div className="hidden md:flex items-center gap-6">
            <Link to="/buy-cars" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
              Buy Cars
            </Link>
            <Link to="/sell-car" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
              Sell Car
            </Link>
            <Link to="/estimate" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
              Estimate Value
            </Link>
            <Link to="/about-us" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
              About Us
            </Link>
          </div>

          <div className="flex items-center gap-3">
            <Link to="/signin">
              <Button variant="ghost" size="sm">
                Sign In
              </Button>
            </Link>
            <Link to="/signup">
              <Button variant="default" size="sm">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
