"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/components/providers/auth-provider";
import { Button } from "@/components/ui/button";
import {
  Building2,
  LogOut,
  User,
  BarChart3,
  Upload,
  Settings,
  Plus,
  GitCompare,
} from "lucide-react";
import { cn } from "@/lib/utils";

export function Navigation() {
  const { user, signOut } = useAuth();
  const pathname = usePathname();

  const navigation = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: BarChart3,
    },
    {
      name: "Compare",
      href: "/comparison",
      icon: GitCompare,
    },
    {
      name: "Settings",
      href: "/settings",
      icon: Settings,
    },
  ];

  if (!user) {
    return (
      <nav className="border-b border-gray-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <Link href="/" className="flex items-center space-x-2 group">
              <Building2 className="h-8 w-8 text-blue-600 group-hover:text-blue-700 transition-colors" />
              <span className="text-xl font-bold text-blue-600 group-hover:text-blue-700 transition-colors">
                PropPulse AI
              </span>
            </Link>
            <div className="flex items-center space-x-4">
              <Link href="/auth/login">
                <Button
                  variant="ghost"
                  className="text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-all duration-200"
                >
                  Sign In
                </Button>
              </Link>
              <Link href="/auth/login?demo=true">
                <Button
                  variant="outline"
                  className="text-blue-600 border-blue-600 hover:bg-blue-50 transition-all duration-200"
                >
                  Try Demo
                </Button>
              </Link>
              <Link href="/auth/register">
                <Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-2 rounded-lg shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-105">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link href="/dashboard" className="flex items-center space-x-2">
            <Building2 className="h-7 w-7 text-blue-600" />
            <span className="text-xl font-bold text-blue-600">
              PropPulse AI
            </span>
          </Link>

          <div className="flex items-center space-x-8">
            <div className="flex space-x-6">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "text-sm font-medium transition-colors",
                    pathname === item.href
                      ? "text-blue-600"
                      : "text-gray-600 hover:text-gray-900"
                  )}
                >
                  <span>{item.name}</span>
                </Link>
              ))}
            </div>

            <div className="flex items-center space-x-4">
              <Link href="/upload">
                <Button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg">
                  <Plus className="h-4 w-4 mr-2" />
                  New Deal
                </Button>
              </Link>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <User className="h-4 w-4" />
                <span>{user.email}</span>
              </div>
              <Button variant="ghost" size="sm" onClick={signOut}>
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
