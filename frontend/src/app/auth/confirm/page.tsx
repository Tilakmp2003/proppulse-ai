"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Building2, CheckCircle, XCircle, Loader2 } from "lucide-react";

export default function ConfirmPage() {
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [message, setMessage] = useState("");
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const confirmEmail = async () => {
      try {
        const token_hash = searchParams.get("token_hash");
        const type = searchParams.get("type");

        if (!token_hash || type !== "signup") {
          setStatus("error");
          setMessage("Invalid confirmation link");
          return;
        }

        const { data, error } = await supabase.auth.verifyOtp({
          token_hash,
          type: "signup",
        });

        if (error) {
          setStatus("error");
          setMessage(error.message);
        } else if (data.user) {
          setStatus("success");
          setMessage("Email confirmed successfully! You can now sign in.");

          // Redirect to login page after 3 seconds
          setTimeout(() => {
            router.push("/auth/login");
          }, 3000);
        }
      } catch (err) {
        setStatus("error");
        setMessage("An unexpected error occurred");
      }
    };

    confirmEmail();
  }, [searchParams, router]);

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
            <CardTitle className="text-2xl">Email Confirmation</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            {status === "loading" && (
              <div className="space-y-4">
                <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary" />
                <p className="text-gray-600">Confirming your email...</p>
              </div>
            )}

            {status === "success" && (
              <div className="space-y-4">
                <CheckCircle className="h-12 w-12 mx-auto text-green-500" />
                <div>
                  <h3 className="text-lg font-semibold text-green-600 mb-2">
                    Success!
                  </h3>
                  <p className="text-gray-600 mb-4">{message}</p>
                  <p className="text-sm text-gray-500">
                    Redirecting to login page in a few seconds...
                  </p>
                </div>
              </div>
            )}

            {status === "error" && (
              <div className="space-y-4">
                <XCircle className="h-12 w-12 mx-auto text-red-500" />
                <div>
                  <h3 className="text-lg font-semibold text-red-600 mb-2">
                    Confirmation Failed
                  </h3>
                  <p className="text-gray-600 mb-4">{message}</p>
                  <Button onClick={() => router.push("/auth/login")}>
                    Go to Login
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
