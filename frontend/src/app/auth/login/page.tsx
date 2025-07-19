"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/components/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Building2, Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [loginMethod, setLoginMethod] = useState<"password" | "otp">(
    "password"
  );
  const router = useRouter();
  const { refreshAuth, signInUser } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (loginMethod === "password") {
        // Password-based login with improved validation
        const result = await signInUser(email, password);

        if (!result.success) {
          setError(result.error || "Login failed");
        } else {
          // Success - user will be set by auth state change, redirect to dashboard
          router.push("/dashboard");
        }
      } else {
        // OTP-based login verification using our backend
        const API_BASE_URL =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${API_BASE_URL}/auth/verify-otp`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email, otp }),
        });

        const data = await response.json();

        if (!response.ok) {
          setError(data.detail || "Invalid OTP. Please try again.");
        } else {
          // OTP is valid, create a session
          localStorage.setItem(
            "demo_user",
            JSON.stringify({
              email: email,
              token: data.token || "otp-token-" + Date.now(),
              loginMethod: "otp",
            })
          );

          // Refresh auth context and then navigate
          await refreshAuth();
          router.push("/dashboard");
        }
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSendOTP = async () => {
    if (!email) {
      setError("Please enter your email address first");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // Send OTP via our backend API for numeric codes
      const API_BASE_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${API_BASE_URL}/auth/send-otp`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Failed to send OTP");
      } else {
        setOtpSent(true);
        setLoginMethod("otp");
        setError("");
        alert(
          "6-digit OTP code sent to your email! Please check your inbox and enter the code below."
        );
      }
    } catch (err) {
      setError("Failed to send OTP. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setOtpSent(false);
    await handleSendOTP();
  };

  const handleResendConfirmation = async () => {
    if (!email) {
      setError("Please enter your email address first");
      return;
    }

    setLoading(true);
    try {
      const { error } = await supabase.auth.resend({
        type: "signup",
        email: email,
      });

      if (error) {
        setError(error.message);
      } else {
        setError(""); // Clear any existing errors
        alert(
          "Confirmation email sent! Please check your inbox and spam folder."
        );
      }
    } catch (err) {
      setError("Failed to resend confirmation email");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center mb-8">
          <Building2 className="h-10 w-10 text-primary mr-2" />
          <span className="text-2xl font-bold text-primary">PropPulse AI</span>
        </div>

        <Card className="w-full">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Welcome Back</CardTitle>
            <CardDescription>
              Sign in to your PropPulse AI account
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Login Method Toggle */}
            <div className="flex p-1 bg-gray-100 rounded-lg mb-6">
              <button
                type="button"
                onClick={() => {
                  setLoginMethod("password");
                  setOtpSent(false);
                  setError("");
                }}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  loginMethod === "password"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Password
              </button>
              <button
                type="button"
                onClick={() => {
                  setLoginMethod("otp");
                  setError("");
                }}
                className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  loginMethod === "otp"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Email Code
              </button>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              {error && (
                <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md">
                  {error}
                  {error.includes("Email not confirmed") && (
                    <div className="mt-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={handleResendConfirmation}
                        disabled={loading}
                        className="text-xs"
                      >
                        Resend Confirmation Email
                      </Button>
                    </div>
                  )}
                </div>
              )}

              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email Address
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  required
                />
              </div>

              {loginMethod === "password" ? (
                <div className="space-y-2">
                  <label htmlFor="password" className="text-sm font-medium">
                    Password
                  </label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      autoComplete="current-password"
                      required={loginMethod === "password"}
                    />
                    <button
                      type="button"
                      className="absolute right-3 top-1/2 transform -translate-y-1/2"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4 text-gray-400" />
                      ) : (
                        <Eye className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {!otpSent ? (
                    <div className="space-y-2">
                      <p className="text-sm text-gray-600">
                        We'll send a 6-digit code to your email address.
                      </p>
                      <Button
                        type="button"
                        onClick={handleSendOTP}
                        disabled={loading || !email}
                        className="w-full"
                        variant="outline"
                      >
                        {loading ? "Sending..." : "Send Code"}
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <label htmlFor="otp" className="text-sm font-medium">
                        Enter 6-digit code
                      </label>
                      <Input
                        id="otp"
                        type="text"
                        placeholder="123456"
                        value={otp}
                        onChange={(e) =>
                          setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
                        }
                        maxLength={6}
                        autoComplete="one-time-code"
                        required
                        className="text-center text-lg tracking-widest"
                      />
                      <p className="text-xs text-gray-500">
                        Code sent to {email}
                      </p>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={handleResendOTP}
                        disabled={loading}
                        className="text-xs"
                      >
                        Resend Code
                      </Button>
                    </div>
                  )}
                </div>
              )}

              <Button
                type="submit"
                className="w-full"
                disabled={loading || (loginMethod === "otp" && !otpSent)}
              >
                {loading
                  ? "Signing In..."
                  : loginMethod === "password"
                  ? "Sign In"
                  : "Verify Code"}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Don't have an account?{" "}
                <Link
                  href="/auth/register"
                  className="text-primary hover:underline"
                >
                  Sign up
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
