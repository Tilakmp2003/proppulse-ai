"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/components/providers/auth-provider";
import { Navigation } from "@/components/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Building2,
  Clock,
  TrendingUp,
  FileText,
  BarChart3,
  Download,
  Zap,
  Shield,
  Brain,
  CheckCircle,
} from "lucide-react";

export default function LandingPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push("/dashboard");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Navigation />

      {/* Hero Section */}
      <section className="relative py-20 sm:py-28 overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-indigo-50"></div>
        <div className="absolute inset-y-0 right-0 w-1/2 bg-gradient-to-l from-blue-50 to-transparent opacity-50"></div>

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mb-10">
              <span className="inline-flex items-center rounded-full bg-blue-100 px-4 py-2 text-sm font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
                ✨ AI-Powered Real Estate Analysis
              </span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl lg:text-5xl">
              Underwrite any commercial real estate deal in{" "}
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                30 seconds
              </span>
            </h1>
            <p className="mt-8 text-base leading-7 text-gray-600 max-w-3xl mx-auto">
              AI-powered deal analysis that pulls property data, analyzes
              financials, and delivers instant investment decisions with
              institutional-grade accuracy.
            </p>

            <div className="mt-12 flex items-center justify-center gap-x-6">
              <Link href="/auth/register">
                <Button
                  size="lg"
                  className="text-base px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
                >
                  Try Demo Deal
                </Button>
              </Link>
              <Link href="#demo">
                <Button
                  variant="outline"
                  size="lg"
                  className="text-base px-8 py-3 border-2 border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400 rounded-xl shadow-md hover:shadow-lg transition-all duration-200"
                >
                  Watch Demo
                </Button>
              </Link>
            </div>

            {/* Key Metrics */}
            <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
              <div className="text-center group">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 transition-all duration-150 hover:shadow-lg hover:scale-105 cursor-pointer h-24 flex flex-col justify-center">
                  <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-1">
                    100x
                  </div>
                  <div className="text-xs font-medium text-gray-600 uppercase tracking-wide leading-tight">
                    Faster than traditional underwriting
                  </div>
                </div>
              </div>
              <div className="text-center group">
                <div className="bg-gradient-to-br from-green-50 to-emerald-100 rounded-xl p-4 transition-all duration-150 hover:shadow-lg hover:scale-105 cursor-pointer h-24 flex flex-col justify-center">
                  <div className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-1">
                    95%
                  </div>
                  <div className="text-xs font-medium text-gray-600 uppercase tracking-wide leading-tight">
                    Accuracy vs manual analysis
                  </div>
                </div>
              </div>
              <div className="text-center group">
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 transition-all duration-150 hover:shadow-lg hover:scale-105 cursor-pointer h-24 flex flex-col justify-center">
                  <div className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-1">
                    $2B+
                  </div>
                  <div className="text-xs font-medium text-gray-600 uppercase tracking-wide leading-tight">
                    Deals analyzed
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section className="py-24 bg-gradient-to-br from-gray-50 to-gray-100 relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              From property address to investment decision
            </h2>
            <p className="text-base text-gray-600 max-w-3xl mx-auto">
              Our AI-powered platform streamlines the entire underwriting
              process
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative">
            {/* Connection Lines */}
            <div className="hidden md:block absolute top-1/2 left-1/3 w-1/3 h-0.5 bg-gradient-to-r from-blue-200 to-green-200 transform -translate-y-1/2"></div>
            <div className="hidden md:block absolute top-1/2 right-1/3 w-1/3 h-0.5 bg-gradient-to-r from-green-200 to-purple-200 transform -translate-y-1/2"></div>

            {/* Step 1 */}
            <div className="text-center group relative">
              <div className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 hover:scale-105 border border-gray-100 cursor-pointer">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 w-24 h-24 rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-lg group-hover:shadow-xl transition-all duration-200">
                  <Building2 className="h-12 w-12 text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-4">
                  Auto Data Collection
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  Pulls property data, comps, demographics, and financial
                  documents automatically from multiple sources.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="text-center group relative">
              <div className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 hover:scale-105 border border-gray-100 cursor-pointer">
                <div className="bg-gradient-to-br from-green-500 to-green-600 w-24 h-24 rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-lg group-hover:shadow-xl transition-all duration-200">
                  <BarChart3 className="h-12 w-12 text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-4">
                  Smart Financial Analysis
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  Extracts T12 & Rent Roll data, calculates key metrics, and
                  runs comprehensive financial modeling.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="text-center group relative">
              <div className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 hover:scale-105 border border-gray-100 cursor-pointer">
                <div className="bg-gradient-to-br from-purple-500 to-purple-600 w-24 h-24 rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-lg group-hover:shadow-xl transition-all duration-200">
                  <CheckCircle className="h-12 w-12 text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-4">
                  Instant Decision
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  Get immediate Pass/Fail recommendations with detailed
                  reasoning, risk analysis, and actionable insights.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl mb-6">
              Everything you need for 30-second analysis
            </h2>
            <p className="text-base text-gray-600 max-w-3xl mx-auto">
              AI-powered tools that transform how you evaluate commercial real
              estate deals
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {/* Feature 1 */}
            <div className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 hover:scale-105 border border-gray-100 cursor-pointer">
              <div className="bg-gradient-to-br from-yellow-400 to-orange-500 w-16 h-16 rounded-xl flex items-center justify-center mb-6 shadow-lg group-hover:shadow-xl transition-all duration-200">
                <Zap className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                AI Data Integration
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                AI automatically pulls data from CoStar, Crexi, Zillow, and
                NeighborhoodScout. No more manual data gathering.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 hover:scale-105 border border-gray-100 cursor-pointer">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 w-16 h-16 rounded-xl flex items-center justify-center mb-6 shadow-lg group-hover:shadow-xl transition-all duration-200">
                <FileText className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Smart Document Processing
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                Upload T12 & Rent Roll → AI instantly maps all financials. 99%
                accuracy in data extraction.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 hover:scale-105 border border-gray-100 cursor-pointer">
              <div className="bg-gradient-to-br from-purple-500 to-pink-600 w-16 h-16 rounded-xl flex items-center justify-center mb-6 shadow-lg group-hover:shadow-xl transition-all duration-200">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Buy Box Matching
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                Auto-checks against your firm's investment criteria (IRR, CoC,
                Cap Rate). Instant Pass/Fail recommendations.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 hover:scale-105 border border-gray-100 cursor-pointer">
              <div className="bg-gradient-to-br from-green-500 to-emerald-600 w-16 h-16 rounded-xl flex items-center justify-center mb-6 shadow-lg group-hover:shadow-xl transition-all duration-200">
                <Clock className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                30-Second Analysis
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                Complete underwriting in under 30 seconds. Deal score,
                sensitivity analysis, and actionable fix suggestions.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 hover:scale-105 border border-gray-100 cursor-pointer">
              <div className="bg-gradient-to-br from-red-500 to-pink-600 w-16 h-16 rounded-xl flex items-center justify-center mb-6 shadow-lg group-hover:shadow-xl transition-all duration-200">
                <Download className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Export Everything
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                Auto-generated PDF reports, Excel underwriting models, and LOI
                documents ready for investors and lenders.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 hover:scale-105 border border-gray-100 cursor-pointer">
              <div className="bg-gradient-to-br from-indigo-500 to-purple-600 w-16 h-16 rounded-xl flex items-center justify-center mb-6 shadow-lg group-hover:shadow-xl transition-all duration-200">
                <TrendingUp className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Team Collaboration
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                Built-in collaboration tools, versioning, risk scoring, and
                capital stack modeling for your entire team.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-24 bg-gray-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              The Impact: Transform Your CRE Business
            </h2>
          </div>

          <div className="mt-20 grid grid-cols-1 gap-12 lg:grid-cols-4">
            <div className="text-center">
              <div className="flex justify-center">
                <Zap className="h-12 w-12 text-primary" />
              </div>
              <h3 className="mt-6 text-xl font-semibold text-gray-900">
                100x Faster
              </h3>
              <p className="mt-4 text-gray-600">
                Complete underwriting in 30 seconds instead of hours. Focus on
                deals, not data entry.
              </p>
            </div>

            <div className="text-center">
              <div className="flex justify-center">
                <Clock className="h-12 w-12 text-primary" />
              </div>
              <h3 className="mt-6 text-xl font-semibold text-gray-900">
                Save Thousands of Hours
              </h3>
              <p className="mt-4 text-gray-600">
                Eliminate manual data gathering and calculation workflows that
                waste analyst time.
              </p>
            </div>

            <div className="text-center">
              <div className="flex justify-center">
                <TrendingUp className="h-12 w-12 text-primary" />
              </div>
              <h3 className="mt-6 text-xl font-semibold text-gray-900">
                Democratize CRE
              </h3>
              <p className="mt-4 text-gray-600">
                Give small firms the same analytical power as institutional
                players.
              </p>
            </div>

            <div className="text-center">
              <div className="flex justify-center">
                <Building2 className="h-12 w-12 text-primary" />
              </div>
              <h3 className="mt-6 text-xl font-semibold text-gray-900">
                Competitive Edge
              </h3>
              <p className="mt-4 text-gray-600">
                Make faster, data-driven decisions and close more deals than
                your competition.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 py-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-blue-600/50 to-transparent"></div>

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl mb-6">
              Ready to transform your real estate analysis?
            </h2>
            <p className="text-lg text-blue-100 mb-8 max-w-3xl mx-auto">
              Join thousands of real estate professionals who trust PropPulse AI
              to make faster, more accurate investment decisions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/auth/register">
                <Button
                  size="lg"
                  className="text-base px-8 py-3 bg-white text-blue-600 hover:bg-gray-100 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
                >
                  Start Free Trial
                </Button>
              </Link>
              <div className="flex items-center space-x-2 text-blue-100">
                <CheckCircle className="h-5 w-5" />
                <span className="text-sm">No credit card required</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Building2 className="h-6 w-6 text-primary" />
              <span className="font-bold text-primary">PropPulse AI</span>
            </div>
            <p className="text-sm text-gray-500">
              © 2024 PropPulse AI. Built for Persist Ventures.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
