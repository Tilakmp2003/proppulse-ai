"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Navigation } from "@/components/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MapPin, Search } from "lucide-react";

export default function UploadPage() {
  const [propertyAddress, setPropertyAddress] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleAnalyzeProperty = async () => {
    if (!propertyAddress.trim()) return;

    setLoading(true);

    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Navigate to upload documents page with address
    router.push(
      `/upload/documents?address=${encodeURIComponent(propertyAddress)}`
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            New Deal Analysis
          </h1>
          <p className="text-gray-600">
            Start by entering the property address to begin your AI-powered
            underwriting analysis
          </p>
        </div>

        <div className="max-w-2xl mx-auto">
          <Card className="shadow-lg">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <div className="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center">
                  <MapPin className="h-8 w-8 text-primary" />
                </div>
              </div>
              <CardTitle className="text-2xl">Enter Property Address</CardTitle>
              <p className="text-gray-600 mt-2">
                Our AI will gather comprehensive property data from multiple
                sources
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <label
                  htmlFor="address"
                  className="text-sm font-medium text-gray-700"
                >
                  Property Address
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    id="address"
                    type="text"
                    placeholder="123 Main Street, Austin, TX 78701"
                    value={propertyAddress}
                    onChange={(e) => setPropertyAddress(e.target.value)}
                    className="pl-10 text-lg py-6"
                    disabled={loading}
                  />
                </div>
                <p className="text-xs text-gray-500">
                  Include street address, city, state, and ZIP code for best
                  results
                </p>
              </div>

              <Button
                onClick={handleAnalyzeProperty}
                disabled={!propertyAddress.trim() || loading}
                className="w-full py-6 text-lg"
                size="lg"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Analyzing Property...</span>
                  </div>
                ) : (
                  "Analyze Property"
                )}
              </Button>

              {loading && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center space-x-3">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <div>
                      <p className="text-sm font-medium text-blue-900">
                        AI Analysis in Progress...
                      </p>
                      <p className="text-xs text-blue-700">
                        Gathering comprehensive property data from CoStar,
                        Zillow, and market sources
                      </p>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="bg-blue-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full animate-pulse"
                        style={{ width: "75%" }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Sample addresses for demo */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-600 mb-4">
              Try these sample addresses:
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {[
                "1234 Commerce St, Austin, TX 78701",
                "456 Oak Avenue, Dallas, TX 75201",
                "789 Pine Street, Houston, TX 77002",
              ].map((address) => (
                <Button
                  key={address}
                  variant="outline"
                  size="sm"
                  onClick={() => setPropertyAddress(address)}
                  disabled={loading}
                  className="text-xs"
                >
                  {address}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
