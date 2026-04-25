import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

const SignIn = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error("Please enter your email and password");
      return;
    }
    setLoading(true);
    try {
      await new Promise((r) => setTimeout(r, 800));
      toast.success("Signed in (demo)");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center px-4 py-12 relative">
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_top_right,rgba(236,72,153,0.18),transparent_40%),radial-gradient(ellipse_at_bottom_left,rgba(59,130,246,0.2),transparent_45%)]" />
      <Card className="relative w-full max-w-2xl md:w-3/4 border-border rounded-xl card-3d shine bg-card/90">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-extrabold logo-3d-text">Welcome back</CardTitle>
          <CardDescription className="text-primary font-bold"style={{ fontSize: "1.2rem" }}>Sign In</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-primary font-bold">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-background/90 input-3d text-foreground placeholder:text-foreground/70 h-12 text-base"
                autoComplete="email"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-primary font-bold">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="********"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-background/90 input-3d text-foreground placeholder:text-foreground/70 h-12 text-base"
                autoComplete="current-password"
              />
            </div>
            <Button type="submit" className="w-full mt-2 btn-glow text-primary-foreground h-12 text-base font-semibold" disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default SignIn;


