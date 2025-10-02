"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/components/providers/auth-provider";

export default function AuthCallback() {
  const router = useRouter();
  const { refreshAuth } = useAuth();

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // Handle the auth callback from email confirmation
        const { data, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error("Auth callback error:", error);
          // Redirect to login with error
          router.push("/auth/login?error=auth_error");
          return;
        }

        if (data.session?.user) {
          // Check if email is confirmed
          if (data.session.user.email_confirmed_at) {
            console.log("Email confirmed, user authenticated");
            // Refresh auth state
            await refreshAuth();
            // Redirect to dashboard
            router.push("/dashboard");
          } else {
            // Email not confirmed yet
            console.log("Email not confirmed");
            router.push("/auth/login?error=email_not_confirmed");
          }
        } else {
          // No session - redirect to login
          console.log("No session found");
          router.push("/auth/login");
        }
      } catch (error) {
        console.error("Auth callback error:", error);
        router.push("/auth/login?error=callback_error");
      }
    };

    handleAuthCallback();
  }, [router, refreshAuth]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <h2 className="text-lg font-medium text-gray-900 mb-2">
              Confirming your account...
            </h2>
            <p className="text-sm text-gray-600">
              Please wait while we verify your email and sign you in.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
