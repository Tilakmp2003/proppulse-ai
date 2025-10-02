"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/providers/auth-provider";
import { Navigation } from "@/components/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Building2,
  CheckCircle,
  ExternalLink,
  Settings,
  Zap,
} from "lucide-react";

// Mock integration data
const integrations = [
  {
    name: "CoStar",
    description: "Commercial real estate market data and analytics",
    status: "connected",
    logo: "🏢",
    lastSync: "2024-01-15T10:30:00Z",
  },
  {
    name: "Zillow",
    description: "Residential and commercial property data",
    status: "connected",
    logo: "🏠",
    lastSync: "2024-01-15T09:15:00Z",
  },
  {
    name: "NeighborhoodScout",
    description: "Crime, demographics, and neighborhood analytics",
    status: "connected",
    logo: "📊",
    lastSync: "2024-01-15T08:45:00Z",
  },
  {
    name: "Crexi",
    description: "Commercial real estate marketplace data",
    status: "available",
    logo: "🏬",
    lastSync: null,
  },
];

export default function IntegrationsPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/auth/login");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Integrations</h1>
          <p className="text-gray-600 mt-1">
            Manage your data sources and external platform connections
          </p>
        </div>

        {/* Integration Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {integrations.map((integration) => (
            <Card key={integration.name} className="relative">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">{integration.logo}</div>
                    <div>
                      <CardTitle className="text-lg">
                        {integration.name}
                      </CardTitle>
                      <p className="text-sm text-gray-500 mt-1">
                        {integration.description}
                      </p>
                    </div>
                  </div>
                  {integration.status === "connected" && (
                    <CheckCircle className="h-6 w-6 text-green-500" />
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {integration.status === "connected" ? (
                    <>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">Status:</span>
                        <span className="text-green-600 font-medium">
                          Connected
                        </span>
                      </div>
                      {integration.lastSync && (
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-500">Last sync:</span>
                          <span className="text-gray-900">
                            {new Date(
                              integration.lastSync
                            ).toLocaleDateString()}
                          </span>
                        </div>
                      )}
                      <div className="flex space-x-2">
                        <Button variant="outline" size="sm" className="flex-1">
                          <Settings className="h-4 w-4 mr-2" />
                          Configure
                        </Button>
                        <Button variant="outline" size="sm" className="flex-1">
                          <Zap className="h-4 w-4 mr-2" />
                          Sync Now
                        </Button>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">Status:</span>
                        <span className="text-yellow-600 font-medium">
                          Available
                        </span>
                      </div>
                      <Button className="w-full">
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Connect {integration.name}
                      </Button>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* API Status Section */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Building2 className="h-5 w-5" />
              <span>API Status & Usage</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">99.9%</div>
                <div className="text-sm text-gray-500">Uptime</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">1,247</div>
                <div className="text-sm text-gray-500">API Calls Today</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">34ms</div>
                <div className="text-sm text-gray-500">Avg Response Time</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
