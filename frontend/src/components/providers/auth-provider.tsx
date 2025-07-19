"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import type { User } from "@supabase/supabase-js";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signOut: () => Promise<void>;
  refreshAuth: () => Promise<void>;
  signUpUser: (
    email: string,
    password: string,
    userData?: any
  ) => Promise<{ success: boolean; error?: string }>;
  signInUser: (
    email: string,
    password: string
  ) => Promise<{ success: boolean; error?: string }>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  signOut: async () => {},
  refreshAuth: async () => {},
  signUpUser: async () => ({ success: false }),
  signInUser: async () => ({ success: false }),
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initialize authentication
    const initAuth = async () => {
      try {
        // First check for our custom OTP authentication
        const demoUserData = localStorage.getItem("demo_user");
        if (demoUserData) {
          const userData = JSON.parse(demoUserData);
          const customUser = {
            id: `otp-user-${userData.email}`,
            email: userData.email,
            created_at: new Date().toISOString(),
            email_confirmed_at: new Date().toISOString(),
            app_metadata: { loginMethod: userData.loginMethod || "otp" },
            user_metadata: {},
            aud: "authenticated",
            role: "authenticated",
          } as User;

          setUser(customUser);
          setLoading(false);
          return;
        }

        // Get current Supabase session
        const {
          data: { session },
        } = await supabase.auth.getSession();

        if (session?.user) {
          // Check if email is confirmed
          if (session.user.email_confirmed_at) {
            setUser(session.user);
          } else {
            // Email not confirmed, don't set user
            console.warn("User email not confirmed");
            setUser(null);
          }
        } else {
          // No session found - user is not authenticated
          setUser(null);
        }
      } catch (error) {
        console.warn("Supabase auth error:", error);
        // No fallback - user is not authenticated
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initAuth();

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user) {
        // Only set user if email is confirmed
        if (session.user.email_confirmed_at) {
          setUser(session.user);
        } else {
          setUser(null);
        }
      } else {
        setUser(null);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const signOut = async () => {
    try {
      // Clear custom OTP authentication
      localStorage.removeItem("demo_user");

      // Sign out from Supabase
      await supabase.auth.signOut();
      setUser(null);
    } catch (error) {
      console.error("Sign out error:", error);
      // Still clear user state even if Supabase fails
      localStorage.removeItem("demo_user");
      setUser(null);
    }
  };

  const refreshAuth = async () => {
    setLoading(true);
    try {
      // Check for custom OTP authentication first
      const demoUserData = localStorage.getItem("demo_user");
      if (demoUserData) {
        const userData = JSON.parse(demoUserData);
        const customUser = {
          id: `otp-user-${userData.email}`,
          email: userData.email,
          created_at: new Date().toISOString(),
          email_confirmed_at: new Date().toISOString(),
          app_metadata: { loginMethod: userData.loginMethod || "otp" },
          user_metadata: {},
          aud: "authenticated",
          role: "authenticated",
        } as User;

        setUser(customUser);
        return;
      }

      // Check Supabase session
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (session?.user?.email_confirmed_at) {
        setUser(session.user);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error("Refresh auth error:", error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const signUpUser = async (
    email: string,
    password: string,
    userData?: any
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      // Directly attempt signup - Supabase will handle duplicate detection
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: userData || {},
        },
      });

      if (error) {
        console.error("Supabase signup error:", error);
        // Handle specific Supabase errors
        if (
          error.message.includes("User already registered") ||
          error.message.includes("already been registered") ||
          error.message.includes(
            "A user with this email address has already been registered"
          )
        ) {
          return {
            success: false,
            error:
              "An account with this email already exists. Please sign in instead.",
          };
        }
        if (error.message.includes("Password should be at least")) {
          return {
            success: false,
            error: "Password must be at least 6 characters long.",
          };
        }
        if (error.message.includes("Invalid email")) {
          return {
            success: false,
            error: "Please enter a valid email address.",
          };
        }
        return { success: false, error: error.message };
      }

      // Check the response to see if this was a duplicate
      if (
        data.user &&
        data.user.identities &&
        data.user.identities.length === 0
      ) {
        // This usually indicates the user already exists
        return {
          success: false,
          error:
            "An account with this email already exists. Please sign in instead.",
        };
      }

      return { success: true };
    } catch (error) {
      console.error("Signup error:", error);
      return {
        success: false,
        error: "An unexpected error occurred during signup.",
      };
    }
  };

  const signInUser = async (
    email: string,
    password: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        if (error.message.includes("Invalid login credentials")) {
          return {
            success: false,
            error:
              "Invalid email or password. Please check your credentials or sign up if you don't have an account.",
          };
        }
        if (error.message.includes("Email not confirmed")) {
          return {
            success: false,
            error:
              "Please check your email and click the confirmation link before signing in.",
          };
        }
        if (error.message.includes("Too many requests")) {
          return {
            success: false,
            error:
              "Too many login attempts. Please wait a moment and try again.",
          };
        }
        return { success: false, error: error.message };
      }

      if (data.user) {
        // Check if the user's email is confirmed
        if (!data.user.email_confirmed_at) {
          return {
            success: false,
            error:
              "Please verify your email address before signing in. Check your inbox for a confirmation link.",
          };
        }

        // Success - user will be set by the auth state change listener
        return { success: true };
      }

      return { success: false, error: "Login failed. Please try again." };
    } catch (error) {
      console.error("Login error:", error);
      return {
        success: false,
        error: "An unexpected error occurred during login.",
      };
    }
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, signOut, refreshAuth, signUpUser, signInUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
