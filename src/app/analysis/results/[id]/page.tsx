"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
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
  ArrowLeft,
  Share2,
} from "lucide-react";
import { formatCurrency, formatPercent } from "@/lib/utils";

interface AnalysisData {
  id: string;
  property_address: string;
  analysis_result: {
    pass_fail: "PASS" | "FAIL";
    score: number;
    metrics: {
      cap_rate: number;
      cash_on_cash: number;
      irr: number;
      net_present_value: number;
      debt_service_coverage: number;
    };
    property_details: {
      year_built: number;
      square_footage: number;
      units: number;
      property_type: string;
      market_value: number;
    };
    financial_summary: {
      gross_rental_income: number;
      operating_expenses: number;
      net_operating_income: number;
      cash_flow: number;
    };
    market_data: {
      comp_properties: Array<{
        address: string;
        price: number;
        cap_rate: number;
      }>;
      neighborhood_score: number;
      market_trends: string;
    };
  };
  created_at: string;
}

export default function AnalysisResultsPage() {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const params = useParams();
  const analysisId = params.id as string;

  useEffect(() => {
    const fetchAnalysisData = async () => {
      try {
        const API_BASE_URL =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}`);

        if (!response.ok) {
          throw new Error("Failed to fetch analysis data");
        }

        const data = await response.json();
        setAnalysisData(data);
      } catch (err) {
        setError("Failed to load analysis results");
        console.error("Error fetching analysis:", err);
      } finally {
        setLoading(false);
      }
    };

    if (analysisId) {
      fetchAnalysisData();
    }
  }, [analysisId]);

  const handleExport = async (format: "pdf" | "excel") => {
    try {
      const API_BASE_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${API_BASE_URL}/export/${analysisId}/${format}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Export failed");
      }

      // Create blob from response
      const blob = await response.blob();

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      // Set filename based on format
      const timestamp = new Date().toISOString().split("T")[0];
      const filename =
        format === "pdf"
          ? `proppulse_analysis_${timestamp}.pdf`
          : `proppulse_model_${timestamp}.xlsx`;

      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export error:", err);
      alert("Export failed. Please try again.");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <span className="ml-3 text-lg">Loading analysis results...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !analysisData) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Error Loading Results
            </h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <Button onClick={() => router.push("/dashboard")}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const { analysis_result, property_address, created_at } = analysisData;
  const {
    pass_fail,
    score,
    metrics,
    property_details,
    financial_summary,
    market_data,
  } = analysis_result;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <Button
                variant="outline"
                onClick={() => router.push("/dashboard")}
                className="mb-4"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <h1 className="text-3xl font-bold text-gray-900">
                {property_address}
              </h1>
              <p className="text-gray-600">
                Analysis completed on{" "}
                {new Date(created_at).toLocaleDateString()}
              </p>
            </div>

            <div className="flex space-x-3">
              <Button variant="outline" onClick={() => handleExport("pdf")}>
                <FileText className="h-4 w-4 mr-2" />
                Export PDF
              </Button>
              <Button variant="outline" onClick={() => handleExport("excel")}>
                <Download className="h-4 w-4 mr-2" />
                Export Excel
              </Button>
              <Button variant="outline">
                <Share2 className="h-4 w-4 mr-2" />
                Share
              </Button>
            </div>
          </div>
        </div>

        {/* Deal Status and Score */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <Card
            className={`${
              pass_fail === "PASS"
                ? "border-green-500 bg-green-50"
                : "border-red-500 bg-red-50"
            }`}
          >
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                {pass_fail === "PASS" ? (
                  <CheckCircle className="h-8 w-8 text-green-500" />
                ) : (
                  <XCircle className="h-8 w-8 text-red-500" />
                )}
                <div>
                  <p className="text-sm text-gray-600">Deal Status</p>
                  <p
                    className={`text-2xl font-bold ${
                      pass_fail === "PASS" ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {pass_fail}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <Calculator className="h-8 w-8 text-blue-500" />
                <div>
                  <p className="text-sm text-gray-600">Overall Score</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {score}/100
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <Building className="h-8 w-8 text-purple-500" />
                <div>
                  <p className="text-sm text-gray-600">Property Type</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {property_details.property_type}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Key Metrics */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Key Investment Metrics
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Cap Rate"
              value={formatPercent(metrics.cap_rate)}
              change={undefined}
              icon={<TrendingUp className="h-5 w-5" />}
            />
            <MetricCard
              title="Cash-on-Cash Return"
              value={formatPercent(metrics.cash_on_cash)}
              change={undefined}
              icon={<DollarSign className="h-5 w-5" />}
            />
            <MetricCard
              title="IRR"
              value={formatPercent(metrics.irr)}
              change={undefined}
              icon={<TrendingUp className="h-5 w-5" />}
            />
            <MetricCard
              title="DSCR"
              value={metrics.debt_service_coverage.toFixed(2)}
              change={undefined}
              icon={<Calculator className="h-5 w-5" />}
            />
          </div>
        </div>

        {/* Financial Summary and Property Details */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5" />
                <span>Financial Summary</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">Gross Rental Income</span>
                  <span className="font-semibold">
                    {formatCurrency(financial_summary.gross_rental_income)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Operating Expenses</span>
                  <span className="font-semibold text-red-600">
                    -{formatCurrency(financial_summary.operating_expenses)}
                  </span>
                </div>
                <div className="flex justify-between border-t pt-2">
                  <span className="text-gray-600 font-medium">
                    Net Operating Income
                  </span>
                  <span className="font-bold text-green-600">
                    {formatCurrency(financial_summary.net_operating_income)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Annual Cash Flow</span>
                  <span className="font-bold text-blue-600">
                    {formatCurrency(financial_summary.cash_flow)}
                  </span>
                </div>
                <div className="flex justify-between border-t pt-2">
                  <span className="text-gray-600 font-medium">
                    Net Present Value
                  </span>
                  <span className="font-bold text-green-600">
                    {formatCurrency(metrics.net_present_value)}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Building className="h-5 w-5" />
                <span>Property Details</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">Market Value</span>
                  <span className="font-semibold">
                    {formatCurrency(property_details.market_value)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Units</span>
                  <span className="font-semibold">
                    {property_details.units}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Square Footage</span>
                  <span className="font-semibold">
                    {property_details.square_footage.toLocaleString()} sq ft
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Year Built</span>
                  <span className="font-semibold">
                    {property_details.year_built}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Price per Unit</span>
                  <span className="font-semibold">
                    {formatCurrency(
                      property_details.market_value / property_details.units
                    )}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Price per Sq Ft</span>
                  <span className="font-semibold">
                    $
                    {(
                      property_details.market_value /
                      property_details.square_footage
                    ).toFixed(2)}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Market Analysis */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Market Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">
                  Comparable Properties
                </h4>
                <div className="space-y-3">
                  {market_data.comp_properties.map((comp, index) => (
                    <div
                      key={index}
                      className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
                    >
                      <div>
                        <p className="font-medium text-sm">{comp.address}</p>
                        <p className="text-xs text-gray-600">
                          Cap Rate: {formatPercent(comp.cap_rate)}
                        </p>
                      </div>
                      <span className="font-semibold">
                        {formatCurrency(comp.price)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-3">
                  Market Insights
                </h4>
                <div className="space-y-3">
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm font-medium text-blue-900">
                      Neighborhood Score
                    </p>
                    <p className="text-2xl font-bold text-blue-600">
                      {market_data.neighborhood_score}/100
                    </p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-900">
                      Market Trends
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      {market_data.market_trends}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          <Button onClick={() => router.push("/upload")} size="lg">
            Analyze Another Property
          </Button>
          <Button
            variant="outline"
            onClick={() => router.push("/dashboard")}
            size="lg"
          >
            Back to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
