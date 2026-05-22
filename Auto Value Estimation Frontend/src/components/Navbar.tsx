import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import Logo3D from "@/components/Logo3D";

const navLinks = [
  { to: "/buy-cars", label: "Buy Cars" },
  { to: "/sell-car", label: "Sell Car" },
  { to: "/estimate", label: "Estimate Value" },
  { to: "/about-us", label: "About Us" },
];

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const closeMenu = () => setIsMenuOpen(false);

  return (
    <nav className="sticky top-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Logo3D />
          
          <div className="hidden md:flex items-center gap-6">
            {navLinks.map((link) => (
              <Link key={link.to} to={link.to} className="text-sm font-medium text-foreground hover:text-primary transition-colors">
                {link.label}
              </Link>
            ))}
          </div>

          <div className="hidden sm:flex items-center gap-3">
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

          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            aria-label={isMenuOpen ? "Close navigation menu" : "Open navigation menu"}
            aria-expanded={isMenuOpen}
            onClick={() => setIsMenuOpen((open) => !open)}
          >
            {isMenuOpen ? <X /> : <Menu />}
          </Button>
        </div>

        {isMenuOpen && (
          <div className="md:hidden mt-4 rounded-lg border border-border bg-card p-4 shadow-lg">
            <div className="flex flex-col gap-3">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  onClick={closeMenu}
                  className="rounded-md px-3 py-2 text-sm font-medium text-foreground hover:bg-accent hover:text-primary transition-colors"
                >
                  {link.label}
                </Link>
              ))}
              <div className="grid grid-cols-1 gap-2 border-t border-border pt-3 sm:hidden">
                <Link to="/signin" onClick={closeMenu}>
                  <Button variant="ghost" size="sm" className="w-full">
                    Sign In
                  </Button>
                </Link>
                <Link to="/signup" onClick={closeMenu}>
                  <Button variant="default" size="sm" className="w-full">
                    Get Started
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
