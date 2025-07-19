"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter } from "next/navigation";
import { Navigation } from "@/components/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/ui/metric-card";
import {
  CheckCircle,
  XCircle,
  Download,
  FileText,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  DollarSign,
  Building,
  Users,
  Calculator,
} from "lucide-react";
import { formatCurrency, formatPercent } from "@/lib/utils";

// Mock analysis data
const mockAnalysisData = {
  dealStatus: "PASS", // PASS or FAIL
  overallScore: 84,
  metrics: {
    cashOnCash: 8.4,
    capRate: 6.2,
    irr: 14.7,
    dscr: 1.34,
  },
  financials: {
    purchasePrice: 2850000,
    grossRent: 420000,
    operatingExpenses: 168000,
    netOperatingIncome: 252000,
    cashFlow: 89000,
    totalCashRequired: 855000,
  },
  riskAnalysis: [
    {
      type: "Medium Risk",
      description: "Crime rate 12% above city average",
      severity: "medium",
    },
    {
      type: "Low Risk",
      description: "Strong rental demand in area",
      severity: "low",
    },
    {
      type: "Medium Risk",
      description: "Property age requires capital improvements",
      severity: "medium",
    },
  ],
  comparables: [
    {
      address: "1200 Commerce St",
      price: 2750000,
      capRate: 6.0,
      distance: "0.2 miles",
    },
    {
      address: "1456 Main St",
      price: 2950000,
      capRate: 6.4,
      distance: "0.4 miles",
    },
    {
      address: "1789 Oak Ave",
      price: 2650000,
      capRate: 5.8,
      distance: "0.6 miles",
    },
  ],
  recommendations: [
    "Negotiate purchase price down by 5% to improve returns",
    "Budget additional $150K for capital improvements over next 2 years",
    "Consider increasing rents by 3-5% based on market comparables",
    "Implement energy efficiency upgrades to reduce operating expenses",
  ],
};

function AnalysisResultsContent() {
  const [activeTab, setActiveTab] = useState("financials");
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const [address, setAddress] = useState<string>("");

  useEffect(() => {
    // Simulate analysis completion
    const timer = setTimeout(() => {
      setLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const handleExport = (format: "pdf" | "excel") => {
    // Simulate export functionality
    // Export functionality would be implemented here
  };

  const handleGenerateLOI = () => {
    // Simulate LOI generation
    // LOI generation would be implemented here
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Analyzing Your Deal
          </h2>
          <p className="text-gray-600">
            Our AI is processing your property data and generating insights...
          </p>
        </div>
      </div>
    );
  }

  const isPassing = mockAnalysisData.dealStatus === "PASS";

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Progress Indicator */}
      <div className="flex items-center justify-center mb-8">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <div className="h-8 w-8 bg-green-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">1</span>
            </div>
            <span className="ml-2 text-sm font-medium text-green-600">
              Address
            </span>
          </div>
          <div className="h-0.5 w-16 bg-green-500"></div>
          <div className="flex items-center">
            <div className="h-8 w-8 bg-green-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">2</span>
            </div>
            <span className="ml-2 text-sm font-medium text-green-600">
              Documents
            </span>
          </div>
          <div className="h-0.5 w-16 bg-green-500"></div>
          <div className="flex items-center">
            <div className="h-8 w-8 bg-primary rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">3</span>
            </div>
            <span className="ml-2 text-sm font-medium text-primary">
              Analysis
            </span>
          </div>
        </div>
      </div>

      {/* Deal Status */}
      <div className="text-center mb-8">
        <div
          className={`inline-flex items-center px-6 py-3 rounded-full text-lg font-semibold ${
            isPassing
              ? "bg-green-100 text-green-800 border-2 border-green-300"
              : "bg-red-100 text-red-800 border-2 border-red-300"
          }`}
        >
          {isPassing ? (
            <CheckCircle className="h-6 w-6 mr-2" />
          ) : (
            <XCircle className="h-6 w-6 mr-2" />
          )}
          Deal {mockAnalysisData.dealStatus === "PASS" ? "Passes" : "Fails"}
        </div>
        <p className="text-gray-600 mt-2">
          Overall Score: {mockAnalysisData.overallScore}/100
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Cash-on-Cash Return"
          value={mockAnalysisData.metrics.cashOnCash}
          format="percentage"
          icon={<TrendingUp className="h-4 w-4" />}
        />
        <MetricCard
          title="Cap Rate"
          value={mockAnalysisData.metrics.capRate}
          format="percentage"
          icon={<Calculator className="h-4 w-4" />}
        />
        <MetricCard
          title="IRR"
          value={mockAnalysisData.metrics.irr}
          format="percentage"
          icon={<TrendingUp className="h-4 w-4" />}
        />
        <MetricCard
          title="DSCR"
          value={mockAnalysisData.metrics.dscr.toFixed(2)}
          icon={<Building className="h-4 w-4" />}
        />
      </div>

      {/* Detailed Analysis Tabs */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Detailed Analysis</CardTitle>
          <div className="flex space-x-1 mt-4">
            {[
              { id: "financials", label: "Financials" },
              { id: "risk", label: "Risk Analysis" },
              { id: "comparables", label: "Comparables" },
              { id: "recommendations", label: "Recommendations" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === tab.id
                    ? "bg-primary text-white"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </CardHeader>
        <CardContent>
          {activeTab === "financials" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900">
                  Purchase Details
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Purchase Price</span>
                    <span className="font-medium">
                      {formatCurrency(
                        mockAnalysisData.financials.purchasePrice
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Cash Required</span>
                    <span className="font-medium">
                      {formatCurrency(
                        mockAnalysisData.financials.totalCashRequired
                      )}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900">
                  Income & Expenses
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Gross Rental Income</span>
                    <span className="font-medium">
                      {formatCurrency(mockAnalysisData.financials.grossRent)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Operating Expenses</span>
                    <span className="font-medium">
                      {formatCurrency(
                        mockAnalysisData.financials.operatingExpenses
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Net Operating Income</span>
                    <span className="font-medium">
                      {formatCurrency(
                        mockAnalysisData.financials.netOperatingIncome
                      )}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900">Cash Flow</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Annual Cash Flow</span>
                    <span className="font-medium text-green-600">
                      {formatCurrency(mockAnalysisData.financials.cashFlow)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Monthly Cash Flow</span>
                    <span className="font-medium text-green-600">
                      {formatCurrency(
                        mockAnalysisData.financials.cashFlow / 12
                      )}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "risk" && (
            <div className="space-y-4">
              {mockAnalysisData.riskAnalysis.map((risk, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-3 p-4 border border-gray-200 rounded-lg"
                >
                  <div
                    className={`p-2 rounded-full ${
                      risk.severity === "high"
                        ? "bg-red-100"
                        : risk.severity === "medium"
                        ? "bg-yellow-100"
                        : "bg-green-100"
                    }`}
                  >
                    <AlertTriangle
                      className={`h-4 w-4 ${
                        risk.severity === "high"
                          ? "text-red-600"
                          : risk.severity === "medium"
                          ? "text-yellow-600"
                          : "text-green-600"
                      }`}
                    />
                  </div>
                  <div>
                    <h5 className="font-medium text-gray-900">{risk.type}</h5>
                    <p className="text-gray-600 text-sm">{risk.description}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "comparables" && (
            <div className="space-y-4">
              {mockAnalysisData.comparables.map((comp, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                >
                  <div>
                    <h5 className="font-medium text-gray-900">
                      {comp.address}
                    </h5>
                    <p className="text-gray-600 text-sm">{comp.distance}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{formatCurrency(comp.price)}</p>
                    <p className="text-sm text-gray-600">
                      Cap Rate: {formatPercent(comp.capRate)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "recommendations" && (
            <div className="space-y-4">
              {mockAnalysisData.recommendations.map((recommendation, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-3 p-4 border border-gray-200 rounded-lg"
                >
                  <div className="p-2 bg-blue-100 rounded-full">
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                  </div>
                  <p className="text-gray-700">{recommendation}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex items-center justify-center space-x-4">
        <Button variant="outline" onClick={() => handleExport("pdf")}>
          <Download className="h-4 w-4 mr-2" />
          Export PDF Report
        </Button>
        <Button variant="outline" onClick={() => handleExport("excel")}>
          <FileText className="h-4 w-4 mr-2" />
          Export Excel Model
        </Button>
        <Button onClick={handleGenerateLOI} size="lg">
          Generate LOI
        </Button>
      </div>
    </div>
  );
}

export default function AnalysisResultsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <Suspense fallback={<Loading />}>
        <AnalysisResultsContent />
      </Suspense>
    </div>
  );
}

function Loading() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Analyzing Your Deal
        </h2>
        <p className="text-gray-600">
          Our AI is processing your property data and generating insights...
        </p>
      </div>
    </div>
  );
}
