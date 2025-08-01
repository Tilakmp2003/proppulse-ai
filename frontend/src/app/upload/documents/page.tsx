"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Navigation } from "@/components/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { UploadBox } from "@/components/ui/upload-box";
import { Building, MapPin, Users, DollarSign, Calendar } from "lucide-react";

// Mock property data based on address
const mockPropertyData = {
  "1234 Commerce St, Austin, TX 78701": {
    address: "1234 Commerce St, Austin, TX 78701",
    propertyType: "Multifamily",
    units: 48,
    yearBuilt: 1985,
    squareFootage: 45600,
    askingPrice: 2850000,
    marketValue: 2950000,
    neighborhood: "Downtown Austin",
    walkScore: 89,
    dataQuality: null,
  },
  "456 Oak Avenue, Dallas, TX 75201": {
    address: "456 Oak Avenue, Dallas, TX 75201",
    propertyType: "Multifamily",
    units: 64,
    yearBuilt: 1992,
    squareFootage: 58400,
    askingPrice: 3200000,
    marketValue: 3350000,
    neighborhood: "Deep Ellum",
    walkScore: 76,
    dataQuality: null,
  },
  "789 Pine Street, Houston, TX 77002": {
    address: "789 Pine Street, Houston, TX 77002",
    propertyType: "Multifamily",
    units: 32,
    yearBuilt: 1978,
    squareFootage: 28800,
    askingPrice: 1850000,
    marketValue: 1920000,
    neighborhood: "Midtown",
    walkScore: 82,
    dataQuality: null,
  },
};

function DocumentsUploadContent() {
  const [t12File, setT12File] = useState<File | null>(null);
  const [rentRollFile, setRentRollFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");
  const [realPropertyData, setRealPropertyData] = useState<any>(null);
  const [fetchingPropertyData, setFetchingPropertyData] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  const [address, setAddress] = useState<string>("");

  useEffect(() => {
    const addressFromUrl = searchParams.get("address");
    if (addressFromUrl) {
      setAddress(addressFromUrl);
    }
  }, [searchParams]);

  // Fetch real property data when address is available
  useEffect(() => {
    if (address && address.trim()) {
      console.log("Fetching data for address:", address);
      fetchRealPropertyData(address);
    }
  }, [address]);

  // Debug property data whenever it changes
  useEffect(() => {
    if (realPropertyData) {
      console.log("Real property data loaded:", realPropertyData);
      console.log("Processed property data:", {
        address: realPropertyData.property_address,
        propertyType:
          realPropertyData.analysis_result?.property_details?.property_type,
        units: realPropertyData.analysis_result?.property_details?.units,
        yearBuilt:
          realPropertyData.analysis_result?.property_details?.year_built,
        squareFootage:
          realPropertyData.analysis_result?.property_details?.square_footage,
        neighborhood_info: realPropertyData.analysis_result?.neighborhood_info,
        neighborhood_data: realPropertyData.analysis_result?.neighborhood_data,
        market_data: realPropertyData.analysis_result?.market_data,
      });
    }
  }, [realPropertyData]);

  const fetchRealPropertyData = async (propertyAddress: string) => {
    setFetchingPropertyData(true);

    // Check if we have mock data for this address
    const mockDataExists =
      Object.keys(mockPropertyData).includes(propertyAddress);
    console.log("Mock data exists for this address?", mockDataExists);

    // If we have mock data and it's a development environment, use the mock data
    if (mockDataExists && process.env.NODE_ENV === "development") {
      console.log("Using mock data for:", propertyAddress);
      // We don't set realPropertyData, so it will fall back to mock data
      setFetchingPropertyData(false);
      return;
    }

    try {
      const API_BASE_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      console.log("Fetching from API:", `${API_BASE_URL}/quick-analysis`);

      const response = await fetch(`${API_BASE_URL}/quick-analysis`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ address: propertyAddress }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log("Property data received:", result);
        setRealPropertyData(result);
      } else {
        console.error(
          "Failed to fetch property data:",
          response.status,
          await response.text()
        );
      }
    } catch (error) {
      console.error("Error fetching property data:", error);
    } finally {
      setFetchingPropertyData(false);
    }
  };

  // Use real property data if available, otherwise fall back to mock data
  const propertyData = realPropertyData
    ? {
        address: realPropertyData.property_address,
        propertyType:
          realPropertyData.analysis_result?.property_details?.property_type,
        units: realPropertyData.analysis_result?.property_details?.units,
        yearBuilt:
          realPropertyData.analysis_result?.property_details?.year_built,
        squareFootage:
          realPropertyData.analysis_result?.property_details?.square_footage,
        askingPrice:
          realPropertyData.analysis_result?.property_details?.market_value,
        marketValue:
          realPropertyData.analysis_result?.property_details?.market_value,
        // Check both neighborhood_info and neighborhood_data
        neighborhood:
          realPropertyData.analysis_result?.neighborhood_info
            ?.location_quality ||
          realPropertyData.analysis_result?.neighborhood_data?.location_quality,
        walkScore:
          realPropertyData.analysis_result?.neighborhood_info
            ?.walkability_score ||
          realPropertyData.analysis_result?.neighborhood_data
            ?.walkability_score,
        // Add data quality information from market data
        dataQuality:
          realPropertyData.analysis_result?.market_data?.data_quality,
      }
    : mockPropertyData[address as keyof typeof mockPropertyData] || {
        address,
        propertyType: null,
        units: null,
        yearBuilt: null,
        squareFootage: null,
        askingPrice: null,
        marketValue: null,
        neighborhood: null,
        walkScore: null,
        dataQuality: null,
      };

  const handleContinueToAnalysis = async () => {
    if (!t12File || !rentRollFile) return;

    setLoading(true);
    setUploadProgress(0);
    setCurrentStep("Uploading documents...");

    try {
      // Step 1: Upload files to backend
      const formData = new FormData();
      formData.append("files", t12File);
      formData.append("files", rentRollFile);
      formData.append("property_address", address); // Add property address to form data

      const API_BASE_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"; // Fixed port

      setUploadProgress(20);

      // Add timeout to prevent hanging
      const uploadController = new AbortController();
      const uploadTimeoutId = setTimeout(() => uploadController.abort(), 30000); // 30 second timeout

      const uploadResponse = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
        signal: uploadController.signal,
      });

      clearTimeout(uploadTimeoutId);

      if (!uploadResponse.ok) {
        throw new Error("Upload failed");
      }

      const uploadResult = await uploadResponse.json();
      const uploadId = uploadResult.upload_id;

      setUploadProgress(50);
      setCurrentStep("Analyzing property data...");

      // Step 2: Trigger analysis with timeout
      const analysisController = new AbortController();
      const analysisTimeoutId = setTimeout(
        () => analysisController.abort(),
        60000
      ); // 60 second timeout for analysis

      const analysisResponse = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          upload_id: uploadId,
          investment_criteria: {
            minCapRate: 6.0,
            minCashOnCash: 8.0,
            minDSCR: 1.2,
          },
        }),
        signal: analysisController.signal,
      });

      clearTimeout(analysisTimeoutId);

      if (!analysisResponse.ok) {
        throw new Error("Analysis failed");
      }

      const analysisResult = await analysisResponse.json();
      setUploadProgress(100);
      setCurrentStep("Analysis complete!");

      // Small delay to show completion
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Navigate to results page with analysis ID
      router.push(`/analysis/results/${analysisResult.id}`);
    } catch (error) {
      console.error("Error during upload/analysis:", error);
      alert("An error occurred during processing. Please try again.");
      setLoading(false);
      setUploadProgress(0);
      setCurrentStep("");
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
            <div className="h-8 w-8 bg-primary rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">2</span>
            </div>
            <span className="ml-2 text-sm font-medium text-primary">
              Documents
            </span>
          </div>
          <div className="h-0.5 w-16 bg-gray-300"></div>
          <div className="flex items-center">
            <div className="h-8 w-8 bg-gray-300 rounded-full flex items-center justify-center">
              <span className="text-gray-600 text-sm font-medium">3</span>
            </div>
            <span className="ml-2 text-sm font-medium text-gray-600">
              Analysis
            </span>
          </div>
        </div>
      </div>

      {/* Property Overview */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Building className="h-5 w-5" />
            <span>Property Overview</span>
          </CardTitle>
          {/* Data Quality Indicator */}
          {propertyData.dataQuality && (
            <div className="mt-2">
              {propertyData.dataQuality?.is_estimated_data ? (
                <div className="flex items-center space-x-2 text-amber-600 bg-amber-50 px-3 py-2 rounded-lg">
                  <svg
                    className="h-4 w-4"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="text-sm font-medium">
                    Estimated Data -{" "}
                    {propertyData.dataQuality?.notes ||
                      "Limited data available"}
                  </span>
                </div>
              ) : propertyData.dataQuality?.is_free_data ? (
                <div className="flex items-center space-x-2 text-blue-600 bg-blue-50 px-3 py-2 rounded-lg">
                  <svg
                    className="h-4 w-4"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="text-sm font-medium">
                    Real Data from Free Public Sources
                  </span>
                </div>
              ) : null}
            </div>
          )}
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <MapPin className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">Address</span>
              </div>
              <p className="font-semibold">{propertyData.address}</p>
            </div>

            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <Building className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">Type</span>
              </div>
              <p className="font-semibold">
                {propertyData.propertyType || "Not available"}
              </p>
            </div>

            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <Users className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">Units</span>
              </div>
              <p className="font-semibold">
                {propertyData.units ? propertyData.units : "Not available"}
              </p>
            </div>

            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <DollarSign className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">Asking Price</span>
              </div>
              <p className="font-semibold">
                {propertyData.askingPrice
                  ? `$${propertyData.askingPrice.toLocaleString()}`
                  : "Not available"}
              </p>
            </div>

            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">Year Built</span>
              </div>
              <p className="font-semibold">
                {propertyData.yearBuilt
                  ? propertyData.yearBuilt
                  : "Not available"}
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-sm text-gray-600">Square Footage</span>
              <p className="font-semibold">
                {propertyData.squareFootage
                  ? `${propertyData.squareFootage.toLocaleString()} sq ft`
                  : "Not available"}
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-sm text-gray-600">Neighborhood</span>
              <p className="font-semibold">
                {propertyData.neighborhood
                  ? propertyData.neighborhood
                  : "Not available"}
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-sm text-gray-600">Walk Score</span>
              <p className="font-semibold">
                {propertyData.walkScore
                  ? `${propertyData.walkScore}/100`
                  : "Not available"}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Document Upload Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Upload Financial Documents
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <UploadBox
            title="T12 (Trailing 12 Months)"
            description="Upload your T12 operating statement in PDF or Excel format"
            acceptedTypes={[".pdf", ".xlsx", ".xls"]}
            onFileSelect={setT12File}
            selectedFile={t12File}
            disabled={loading}
          />

          <UploadBox
            title="Rent Roll"
            description="Upload your current rent roll in Excel or CSV format"
            acceptedTypes={[".xlsx", ".xls", ".csv"]}
            onFileSelect={setRentRollFile}
            selectedFile={rentRollFile}
            disabled={loading}
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={() => router.push("/upload")}
          disabled={loading}
        >
          Back to Address
        </Button>

        <Button
          onClick={handleContinueToAnalysis}
          disabled={!t12File || !rentRollFile || loading}
          size="lg"
          className="px-8"
        >
          {loading ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Processing Documents...</span>
            </div>
          ) : (
            "Continue to Analysis"
          )}
        </Button>
      </div>

      {loading && (
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <div>
              <p className="text-sm font-medium text-blue-900">
                {currentStep || "Processing Financial Documents..."}
              </p>
              <p className="text-xs text-blue-700">
                Our AI is extracting and analyzing your financial data
              </p>
            </div>
          </div>
          <div className="mt-3">
            <div className="bg-blue-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-xs text-blue-700 mt-1">
              {uploadProgress}% complete
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default function DocumentsUploadPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <Suspense fallback={<Loading />}>
        <DocumentsUploadContent />
      </Suspense>
    </div>
  );
}

function Loading() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
      <p className="text-gray-600">Loading property data...</p>
    </div>
  );
}
