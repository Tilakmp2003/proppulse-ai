"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { supabase } from "@/lib/supabase";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Building2, Eye, EyeOff, AlertCircle } from "lucide-react";

export default function DevLoginPage() {
  const [email, setEmail] = useState("demo@proppulse.ai");
  const [password, setPassword] = useState("demo123");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleDemoLogin = () => {
    setLoading(true);
    // Simulate loading
    setTimeout(() => {
      router.push("/dashboard");
    }, 1000);
  };

  const handleSupabaseLogin = async () => {
    setLoading(true);
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        alert(`Supabase Auth Error: ${error.message}`);
      } else {
        router.push("/dashboard");
      }
    } catch (err) {
      alert("Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Logo */}
        <div className="flex items-center justify-center">
          <Building2 className="h-10 w-10 text-primary mr-2" />
          <span className="text-2xl font-bold text-primary">PropPulse AI</span>
        </div>

        {/* Demo Login */}
        <Card className="w-full">
          <CardHeader className="text-center">
            <CardTitle className="text-xl">Demo Access</CardTitle>
            <CardDescription>
              Skip authentication and explore the platform
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={handleDemoLogin}
              className="w-full"
              disabled={loading}
            >
              {loading ? "Loading..." : "Continue as Demo User"}
            </Button>
          </CardContent>
        </Card>

        {/* Supabase Login */}
        <Card className="w-full">
          <CardHeader className="text-center">
            <CardTitle className="text-xl">Supabase Login</CardTitle>
            <CardDescription>
              Sign in with your confirmed Supabase account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start space-x-2 p-3 bg-amber-50 border border-amber-200 rounded-md">
              <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-amber-800">
                <p className="font-medium">Email Confirmation Required</p>
                <p className="mt-1">
                  Make sure to confirm your email before signing in. Check your
                  inbox and spam folder.
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email Address
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>

            <Button
              onClick={handleSupabaseLogin}
              className="w-full"
              disabled={loading}
              variant="outline"
            >
              {loading ? "Signing In..." : "Sign In with Supabase"}
            </Button>

            <div className="text-center text-sm text-gray-600">
              <Link
                href="/auth/register"
                className="text-primary hover:underline"
              >
                Need to create an account?
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
