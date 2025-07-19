"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/components/providers/auth-provider";
import { Navigation } from "@/components/navigation";
import { MetricCard } from "@/components/ui/metric-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Plus,
  Search,
  Filter,
  Building,
  TrendingUp,
  Clock,
  BarChart3,
  MapPin,
  DollarSign,
} from "lucide-react";

// Mock data - replace with real API calls
const mockDeals = [
  {
    id: "1",
    address: "123 Main St, Austin, TX",
    propertyType: "Multifamily",
    dealSize: 2400000,
    cocReturn: 8.9,
    capRate: 6.2,
    confidence: 89,
    status: "analyzed",
    analyzedAt: "2024-01-15",
  },
  {
    id: "2",
    address: "456 Oak Avenue, Dallas, TX",
    propertyType: "Multifamily",
    dealSize: 3200000,
    cocReturn: 7.2,
    capRate: 5.8,
    confidence: 76,
    status: "analyzed",
    analyzedAt: "2024-01-14",
  },
  {
    id: "3",
    address: "789 Pine Street, Houston, TX",
    propertyType: "Multifamily",
    dealSize: 1850000,
    cocReturn: 9.1,
    capRate: 6.7,
    confidence: 92,
    status: "analyzed",
    analyzedAt: "2024-01-13",
  },
];

interface Analysis {
  id: string;
  property_address: string;
  analysis_result: {
    pass_fail: "PASS" | "FAIL";
    score: number;
    metrics: {
      cap_rate: number;
      cash_on_cash: number;
      irr: number;
      debt_service_coverage: number;
    };
    property_details: {
      market_value: number;
      property_type: string;
    };
  };
  created_at: string;
}

interface QuickAnalysisResult {
  id: string;
  property_address: string;
  analysis_result: {
    property_details: {
      property_type: string;
      year_built?: number;
      units: number;
      square_footage?: number;
      market_value: number;
      price_per_unit: number;
    };
    market_data: any;
    neighborhood_info: any;
    demographics: any;
    data_sources: string[];
    ai_analysis: string;
  };
  created_at: string;
  analysis_type: string;
}

export default function DashboardPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState("All Deals");
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loadingAnalyses, setLoadingAnalyses] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Quick analysis state
  const [quickAddress, setQuickAddress] = useState("");
  const [quickAnalysisResult, setQuickAnalysisResult] =
    useState<QuickAnalysisResult | null>(null);
  const [loadingQuickAnalysis, setLoadingQuickAnalysis] = useState(false);
  const [showQuickResults, setShowQuickResults] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/auth/login");
    }
  }, [user, loading, router]);

  useEffect(() => {
    // Only fetch analyses when user is authenticated and not loading
    if (!loading && user) {
      const fetchAnalyses = async () => {
        try {
          const API_BASE_URL =
            process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

          // Add timeout to prevent hanging
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

          const response = await fetch(`${API_BASE_URL}/user/analyses`, {
            signal: controller.signal,
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
          });

          clearTimeout(timeoutId);

          if (response.ok) {
            const data = await response.json();
            setAnalyses(data);
          } else {
            console.error("Failed to fetch analyses, status:", response.status);
            throw new Error(`HTTP ${response.status}`);
          }
        } catch (error) {
          console.error("Error fetching analyses:", error);
          // Fallback to mock data
          const fallbackData = mockDeals.map((deal) => ({
            id: deal.id,
            property_address: deal.address,
            analysis_result: {
              pass_fail: "PASS" as const,
              score: deal.confidence,
              metrics: {
                cap_rate: deal.capRate,
                cash_on_cash: deal.cocReturn,
                irr: 14.5,
                debt_service_coverage: 1.3,
              },
              property_details: {
                market_value: deal.dealSize,
                property_type: deal.propertyType,
              },
            },
            created_at: deal.analyzedAt,
          }));
          setAnalyses(fallbackData);
        } finally {
          setLoadingAnalyses(false);
        }
      };

      fetchAnalyses();
    } else if (!loading && !user) {
      // User not authenticated, stop loading
      setLoadingAnalyses(false);
    }
  }, [user, loading]);

  // Quick analysis function
  const handleQuickAnalysis = async () => {
    if (!quickAddress.trim()) {
      alert("Please enter a property address");
      return;
    }

    setLoadingQuickAnalysis(true);
    setError(null);

    try {
      const API_BASE_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const response = await fetch(`${API_BASE_URL}/quick-analysis`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ address: quickAddress }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const result = await response.json();
        setQuickAnalysisResult(result);
        setShowQuickResults(true);
      } else {
        const errorData = await response.text();
        throw new Error(`Analysis failed: ${errorData}`);
      }
    } catch (error) {
      console.error("Quick analysis error:", error);
      setError(error instanceof Error ? error.message : "Analysis failed");
    } finally {
      setLoadingQuickAnalysis(false);
    }
  };

  useEffect(() => {
    if (!loading && !user) {
      router.push("/auth/login");
    }
  }, [user, loading, router]);

  if (loading || loadingAnalyses) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const filteredAnalyses = analyses.filter(
    (analysis) =>
      analysis.property_address
        .toLowerCase()
        .includes(searchQuery.toLowerCase()) ||
      analysis.analysis_result.property_details.property_type
        .toLowerCase()
        .includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Welcome back! Here's your deal pipeline overview.
            </p>
          </div>
          <Link href="/upload">
            <Button size="lg" className="flex items-center space-x-2">
              <Plus className="h-5 w-5" />
              <span>New Deal</span>
            </Button>
          </Link>
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Deals Analyzed"
            value={47}
            change={12}
            changeType="number"
            icon={<BarChart3 className="h-4 w-4" />}
          />
          <MetricCard
            title="Average Deal Size"
            value={3200000}
            change={150000}
            changeType="currency"
            format="currency"
            icon={<DollarSign className="h-4 w-4" />}
          />
          <MetricCard
            title="Pass Rate"
            value={34}
            change={5}
            changeType="percentage"
            format="percentage"
            icon={<TrendingUp className="h-4 w-4" />}
          />
          <MetricCard
            title="Hours Saved"
            value={156}
            change={24}
            changeType="number"
            icon={<Clock className="h-4 w-4" />}
          />
        </div>

        {/* Quick Property Analysis */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl flex items-center space-x-2">
              <MapPin className="h-5 w-5" />
              <span>Quick Property Lookup</span>
            </CardTitle>
            <p className="text-gray-600 text-sm">
              Get instant property insights using real data from free sources
            </p>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Enter property address (e.g., 123 Main St, Austin, TX)"
                  value={quickAddress}
                  onChange={(e) => setQuickAddress(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleQuickAnalysis()}
                  className="w-full"
                />
              </div>
              <Button
                onClick={handleQuickAnalysis}
                disabled={loadingQuickAnalysis || !quickAddress.trim()}
                className="flex items-center space-x-2"
              >
                <Search className="h-4 w-4" />
                <span>{loadingQuickAnalysis ? "Analyzing..." : "Analyze"}</span>
              </Button>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            {showQuickResults && quickAnalysisResult && (
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-blue-900">
                    {quickAnalysisResult.property_address}
                  </h3>
                  <button
                    onClick={() => setShowQuickResults(false)}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    ✕ Close
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="bg-white p-3 rounded border">
                    <p className="text-sm text-gray-600">Property Type</p>
                    <p className="font-semibold">
                      {
                        quickAnalysisResult.analysis_result.property_details
                          .property_type
                      }
                    </p>
                  </div>
                  <div className="bg-white p-3 rounded border">
                    <p className="text-sm text-gray-600">Units</p>
                    <p className="font-semibold">
                      {quickAnalysisResult.analysis_result.property_details
                        .units || "N/A"}
                    </p>
                  </div>
                  <div className="bg-white p-3 rounded border">
                    <p className="text-sm text-gray-600">Estimated Value</p>
                    <p className="font-semibold">
                      {quickAnalysisResult.analysis_result.property_details
                        .market_value > 0
                        ? `$${quickAnalysisResult.analysis_result.property_details.market_value.toLocaleString()}`
                        : "N/A"}
                    </p>
                  </div>
                </div>

                {quickAnalysisResult.analysis_result.data_sources.length >
                  0 && (
                  <div className="mb-3">
                    <p className="text-sm text-gray-600 mb-1">Data Sources:</p>
                    <div className="flex flex-wrap gap-2">
                      {quickAnalysisResult.analysis_result.data_sources.map(
                        (source, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded"
                          >
                            {source}
                          </span>
                        )
                      )}
                    </div>
                  </div>
                )}

                <p className="text-sm text-blue-700 italic">
                  {quickAnalysisResult.analysis_result.ai_analysis}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Deals Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">Recent Deals</CardTitle>
              <div className="flex items-center space-x-4">
                {/* Search Bar */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search by address or property type..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 w-80"
                  />
                </div>

                {/* Filter Dropdown */}
                <div className="flex items-center space-x-2">
                  <Filter className="h-4 w-4 text-gray-400" />
                  <select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value)}
                    className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  >
                    <option>All Deals</option>
                    <option>Multifamily</option>
                    <option>Office</option>
                    <option>Retail</option>
                    <option>Industrial</option>
                  </select>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredAnalyses.map((analysis) => (
                <div
                  key={analysis.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() =>
                    router.push(`/analysis/results/${analysis.id}`)
                  }
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-start space-x-4">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <MapPin className="h-4 w-4 text-gray-400" />
                            <h3 className="font-semibold text-gray-900">
                              {analysis.property_address}
                            </h3>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">
                            {
                              analysis.analysis_result.property_details
                                .property_type
                            }{" "}
                            | $
                            {(
                              analysis.analysis_result.property_details
                                .market_value / 1000000
                            ).toFixed(1)}
                            M
                          </p>
                          <div className="flex items-center space-x-4 text-sm">
                            <span className="text-gray-600">
                              CoC:{" "}
                              <span className="font-semibold text-green-600">
                                {analysis.analysis_result.metrics.cash_on_cash.toFixed(
                                  1
                                )}
                                %
                              </span>
                            </span>
                            <span className="text-gray-600">
                              Cap:{" "}
                              <span className="font-semibold text-blue-600">
                                {analysis.analysis_result.metrics.cap_rate.toFixed(
                                  1
                                )}
                                %
                              </span>
                            </span>
                          </div>
                        </div>

                        <div className="text-right">
                          <div
                            className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                              analysis.analysis_result.pass_fail === "PASS"
                                ? "bg-green-100 text-green-800"
                                : "bg-red-100 text-red-800"
                            }`}
                          >
                            {analysis.analysis_result.pass_fail} - Score:{" "}
                            {analysis.analysis_result.score}
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            Analyzed{" "}
                            {new Date(analysis.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {filteredAnalyses.length === 0 && (
                <div className="text-center py-12">
                  <Building className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No deals found
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {searchQuery
                      ? "Try adjusting your search criteria."
                      : "Get started by analyzing your first deal."}
                  </p>
                  <Link href="/upload">
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      Analyze New Deal
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
