"use client";

import { useState, useEffect } from "react";
import { Navigation } from "@/components/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  GitCompare,
  Plus,
  Trash2,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Building,
  Calculator,
} from "lucide-react";
import { formatCurrency, formatPercent } from "@/lib/utils";

interface ComparisonProperty {
  id: string;
  address: string;
  metrics: {
    cap_rate: number;
    cash_on_cash: number;
    irr: number;
    debt_service_coverage: number;
    market_value: number;
  };
  score: number;
  pass_fail: "PASS" | "FAIL";
}

export default function ComparisonPage() {
  const [properties, setProperties] = useState<ComparisonProperty[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProperties, setSelectedProperties] = useState<string[]>([]);

  useEffect(() => {
    // Fetch user's analyzed properties
    const fetchProperties = async () => {
      try {
        const API_BASE_URL =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${API_BASE_URL}/user/analyses`);

        if (response.ok) {
          const data = await response.json();
          const formattedProperties = data.map((analysis: any) => ({
            id: analysis.id,
            address: analysis.property_address,
            metrics: analysis.analysis_result.metrics,
            score: analysis.analysis_result.score,
            pass_fail: analysis.analysis_result.pass_fail,
          }));
          setProperties(formattedProperties);
        }
      } catch (error) {
        console.error("Error fetching properties:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProperties();
  }, []);

  const handlePropertySelect = (propertyId: string) => {
    setSelectedProperties((prev) => {
      if (prev.includes(propertyId)) {
        return prev.filter((id) => id !== propertyId);
      } else if (prev.length < 4) {
        // Limit to 4 properties for comparison
        return [...prev, propertyId];
      }
      return prev;
    });
  };

  const selectedData = properties.filter((p) =>
    selectedProperties.includes(p.id)
  );

  const getMetricComparison = (metric: keyof ComparisonProperty["metrics"]) => {
    if (selectedData.length < 2) return [];

    const values = selectedData.map((p) => p.metrics[metric]);
    const max = Math.max(...values);

    return selectedData.map((property, index) => ({
      property,
      value: values[index],
      isMax: values[index] === max,
      percentage: (values[index] / max) * 100,
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <span className="ml-3">Loading properties...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center space-x-3 mb-8">
          <GitCompare className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold text-gray-900">
            Property Comparison
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Property Selection */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Select Properties to Compare</CardTitle>
                <p className="text-sm text-gray-600">
                  Choose up to 4 properties from your analyzed deals
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {properties.map((property) => (
                    <div
                      key={property.id}
                      className={`border rounded-lg p-3 cursor-pointer transition-all ${
                        selectedProperties.includes(property.id)
                          ? "border-primary bg-primary/5"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                      onClick={() => handlePropertySelect(property.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-sm truncate">
                            {property.address}
                          </p>
                          <div className="flex items-center space-x-2 mt-1">
                            <span
                              className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                property.pass_fail === "PASS"
                                  ? "bg-green-100 text-green-800"
                                  : "bg-red-100 text-red-800"
                              }`}
                            >
                              {property.pass_fail}
                            </span>
                            <span className="text-xs text-gray-500">
                              Score: {property.score}
                            </span>
                          </div>
                        </div>
                        <input
                          type="checkbox"
                          checked={selectedProperties.includes(property.id)}
                          onChange={() => handlePropertySelect(property.id)}
                          className="rounded border-gray-300 text-primary focus:ring-primary"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Comparison Results */}
          <div className="lg:col-span-2">
            {selectedData.length < 2 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <Building className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Select Properties to Compare
                  </h3>
                  <p className="text-gray-600">
                    Choose at least 2 properties to see a detailed comparison
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-6">
                {/* Overview Table */}
                <Card>
                  <CardHeader>
                    <CardTitle>Comparison Overview</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left py-2">Property</th>
                            <th className="text-center py-2">Score</th>
                            <th className="text-center py-2">Result</th>
                            <th className="text-center py-2">Cap Rate</th>
                            <th className="text-center py-2">CoC Return</th>
                            <th className="text-center py-2">IRR</th>
                            <th className="text-center py-2">DSCR</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedData.map((property) => (
                            <tr key={property.id} className="border-b">
                              <td className="py-3 font-medium">
                                <div className="truncate max-w-xs">
                                  {property.address}
                                </div>
                              </td>
                              <td className="text-center py-3">
                                {property.score}
                              </td>
                              <td className="text-center py-3">
                                <span
                                  className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                    property.pass_fail === "PASS"
                                      ? "bg-green-100 text-green-800"
                                      : "bg-red-100 text-red-800"
                                  }`}
                                >
                                  {property.pass_fail}
                                </span>
                              </td>
                              <td className="text-center py-3">
                                {formatPercent(property.metrics.cap_rate)}
                              </td>
                              <td className="text-center py-3">
                                {formatPercent(property.metrics.cash_on_cash)}
                              </td>
                              <td className="text-center py-3">
                                {formatPercent(property.metrics.irr)}
                              </td>
                              <td className="text-center py-3">
                                {property.metrics.debt_service_coverage.toFixed(
                                  2
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>

                {/* Metric Comparisons */}
                {[
                  "cap_rate",
                  "cash_on_cash",
                  "irr",
                  "debt_service_coverage",
                ].map((metric) => {
                  const comparison = getMetricComparison(
                    metric as keyof ComparisonProperty["metrics"]
                  );
                  const metricNames = {
                    cap_rate: "Cap Rate",
                    cash_on_cash: "Cash-on-Cash Return",
                    irr: "IRR",
                    debt_service_coverage: "DSCR",
                  };

                  return (
                    <Card key={metric}>
                      <CardHeader>
                        <CardTitle>
                          {metricNames[metric as keyof typeof metricNames]}{" "}
                          Comparison
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {comparison.map(
                            ({ property, value, isMax, percentage }) => (
                              <div key={property.id} className="space-y-2">
                                <div className="flex justify-between items-center">
                                  <span className="text-sm font-medium truncate max-w-xs">
                                    {property.address}
                                  </span>
                                  <span
                                    className={`text-sm font-semibold ${
                                      isMax ? "text-green-600" : "text-gray-600"
                                    }`}
                                  >
                                    {metric === "debt_service_coverage"
                                      ? value.toFixed(2)
                                      : formatPercent(value)}
                                    {isMax && (
                                      <TrendingUp className="inline h-4 w-4 ml-1" />
                                    )}
                                  </span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                  <div
                                    className={`h-2 rounded-full ${
                                      isMax ? "bg-green-500" : "bg-blue-500"
                                    }`}
                                    style={{ width: `${percentage}%` }}
                                  ></div>
                                </div>
                              </div>
                            )
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
