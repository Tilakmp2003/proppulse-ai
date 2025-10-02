"use client";

import { useState, useEffect } from "react";
import { Navigation } from "@/components/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Settings,
  Save,
  RotateCcw,
  DollarSign,
  Target,
  TrendingUp,
  Shield,
  Building,
  Users,
  Calendar,
  Map,
} from "lucide-react";

const defaultCriteria = {
  // Financial Criteria
  minCashOnCash: 8,
  minCapRate: 6,
  minIRR: 12,
  minDSCR: 1.2,
  maxLTV: 75,

  // Property Criteria
  maxYearBuilt: 1980,
  maxPrice: 5000000,
  minPrice: 500000,
  minUnits: 20,
  maxUnits: 100,
  minSquareFootage: 10000,
  maxSquareFootage: 100000,

  // Market Criteria
  preferredMarkets: ["Austin", "Dallas", "Houston", "San Antonio"],
  minNeighborhoodScore: 70,
  maxCrimeRate: 5,
  minWalkScore: 50,

  // Risk & Strategy
  riskTolerance: "medium",
  investmentStrategy: "buy_hold",
  holdingPeriod: 5,
  targetAppreciation: 3,

  // Financing Preferences
  preferredLoanType: "conventional",
  maxInterestRate: 7.5,
  minAmortization: 25,

  // Deal Requirements
  requireProfessionalManagement: false,
  requireOnSiteParking: true,
  requireUpdatedSystems: false,
  allowValueAdd: true,
};

export default function SettingsPage() {
  const [criteria, setCriteria] = useState(defaultCriteria);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("financial");

  useEffect(() => {
    // Load saved criteria from backend API
    const loadCriteria = async () => {
      try {
        const API_BASE_URL =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${API_BASE_URL}/user/criteria`);

        if (response.ok) {
          const data = await response.json();
          setCriteria({ ...defaultCriteria, ...data });
        } else {
          // Fallback to localStorage if API fails
          const saved = localStorage.getItem("investmentCriteria");
          if (saved) {
            setCriteria({ ...defaultCriteria, ...JSON.parse(saved) });
          }
        }
      } catch (error) {
        console.error("Error loading criteria:", error);
        // Fallback to localStorage
        try {
          const saved = localStorage.getItem("investmentCriteria");
          if (saved) {
            setCriteria({ ...defaultCriteria, ...JSON.parse(saved) });
          }
        } catch (localError) {
          console.error("Error loading from localStorage:", localError);
        }
      } finally {
        setLoading(false);
      }
    };

    loadCriteria();
  }, []);

  const handleInputChange = (field: string, value: any) => {
    setCriteria((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const API_BASE_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      const response = await fetch(`${API_BASE_URL}/user/criteria`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(criteria),
      });

      if (response.ok) {
        // Also save to localStorage as backup
        localStorage.setItem("investmentCriteria", JSON.stringify(criteria));
        alert("Investment criteria saved successfully!");
      } else {
        throw new Error("Failed to save to backend");
      }
    } catch (error) {
      console.error("Error saving criteria:", error);

      // Fallback to localStorage only
      try {
        localStorage.setItem("investmentCriteria", JSON.stringify(criteria));
        alert("Investment criteria saved locally (backend unavailable)!");
      } catch (localError) {
        alert("Error saving criteria. Please try again.");
      }
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setCriteria(defaultCriteria);
  };

  const tabs = [
    { id: "financial", label: "Financial", icon: DollarSign },
    { id: "property", label: "Property", icon: Building },
    { id: "market", label: "Market", icon: Map },
    { id: "risk", label: "Risk & Strategy", icon: Shield },
    { id: "financing", label: "Financing", icon: TrendingUp },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <span className="ml-3">Loading settings...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center space-x-3 mb-8">
          <Settings className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold text-gray-900">
            Investment Criteria Settings
          </h1>
        </div>

        <div className="space-y-6">
          {/* Financial Criteria */}
          <Card>
            <CardHeader>
              <CardTitle>Financial Criteria ("Buy Box")</CardTitle>
              <p className="text-sm text-gray-600">
                Set your minimum return requirements for deal evaluation
              </p>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Minimum Cash-on-Cash Return (%)
                </label>
                <Input
                  type="number"
                  step="0.1"
                  value={criteria.minCashOnCash}
                  onChange={(e) =>
                    handleInputChange(
                      "minCashOnCash",
                      parseFloat(e.target.value)
                    )
                  }
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Minimum Cap Rate (%)
                </label>
                <Input
                  type="number"
                  step="0.1"
                  value={criteria.minCapRate}
                  onChange={(e) =>
                    handleInputChange("minCapRate", parseFloat(e.target.value))
                  }
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Minimum IRR (%)</label>
                <Input
                  type="number"
                  step="0.1"
                  value={criteria.minIRR}
                  onChange={(e) =>
                    handleInputChange("minIRR", parseFloat(e.target.value))
                  }
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Minimum DSCR</label>
                <Input
                  type="number"
                  step="0.1"
                  value={criteria.minDSCR}
                  onChange={(e) =>
                    handleInputChange("minDSCR", parseFloat(e.target.value))
                  }
                />
              </div>
            </CardContent>
          </Card>

          {/* Property Criteria */}
          <Card>
            <CardHeader>
              <CardTitle>Property Criteria</CardTitle>
              <p className="text-sm text-gray-600">
                Define your preferred property characteristics
              </p>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Maximum Purchase Price ($)
                </label>
                <Input
                  type="number"
                  value={criteria.maxPrice}
                  onChange={(e) =>
                    handleInputChange("maxPrice", parseInt(e.target.value))
                  }
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Minimum Year Built
                </label>
                <Input
                  type="number"
                  value={criteria.maxYearBuilt}
                  onChange={(e) =>
                    handleInputChange("maxYearBuilt", parseInt(e.target.value))
                  }
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Minimum Units</label>
                <Input
                  type="number"
                  value={criteria.minUnits}
                  onChange={(e) =>
                    handleInputChange("minUnits", parseInt(e.target.value))
                  }
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Maximum Units</label>
                <Input
                  type="number"
                  value={criteria.maxUnits}
                  onChange={(e) =>
                    handleInputChange("maxUnits", parseInt(e.target.value))
                  }
                />
              </div>
            </CardContent>
          </Card>

          {/* Market Preferences */}
          <Card>
            <CardHeader>
              <CardTitle>Market Preferences</CardTitle>
              <p className="text-sm text-gray-600">
                Select your preferred investment markets
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <label className="text-sm font-medium">Preferred Markets</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    "Austin",
                    "Dallas",
                    "Houston",
                    "San Antonio",
                    "Fort Worth",
                    "El Paso",
                    "Arlington",
                    "Corpus Christi",
                  ].map((market) => (
                    <label key={market} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={criteria.preferredMarkets.includes(market)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            handleInputChange("preferredMarkets", [
                              ...criteria.preferredMarkets,
                              market,
                            ]);
                          } else {
                            handleInputChange(
                              "preferredMarkets",
                              criteria.preferredMarkets.filter(
                                (m) => m !== market
                              )
                            );
                          }
                        }}
                        className="rounded border-gray-300 text-primary focus:ring-primary"
                      />
                      <span className="text-sm">{market}</span>
                    </label>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Risk Tolerance */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Tolerance</CardTitle>
              <p className="text-sm text-gray-600">
                Set your risk tolerance level for deal evaluation
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  {
                    value: "conservative",
                    label: "Conservative",
                    description: "Minimal risk, stable returns",
                  },
                  {
                    value: "medium",
                    label: "Moderate",
                    description: "Balanced risk and return",
                  },
                  {
                    value: "aggressive",
                    label: "Aggressive",
                    description: "Higher risk for higher returns",
                  },
                ].map((option) => (
                  <label
                    key={option.value}
                    className="flex items-start space-x-3 cursor-pointer"
                  >
                    <input
                      type="radio"
                      name="riskTolerance"
                      value={option.value}
                      checked={criteria.riskTolerance === option.value}
                      onChange={(e) =>
                        handleInputChange("riskTolerance", e.target.value)
                      }
                      className="mt-1 text-primary focus:ring-primary"
                    />
                    <div>
                      <div className="font-medium">{option.label}</div>
                      <div className="text-sm text-gray-600">
                        {option.description}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex items-center justify-between pt-6">
            <Button variant="outline" onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset to Defaults
            </Button>

            <Button onClick={handleSave} disabled={saving}>
              {saving ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </div>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Settings
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
