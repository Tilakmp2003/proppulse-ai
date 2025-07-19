const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface DealAnalysis {
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

export interface UploadedFile {
  name: string;
  type: string;
  size: number;
}

export class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          error: errorData.detail || `HTTP error! status: ${response.status}`,
        };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return {
        error:
          error instanceof Error ? error.message : "Unknown error occurred",
      };
    }
  }

  async uploadFiles(
    files: File[],
    propertyAddress: string
  ): Promise<ApiResponse<{ upload_id: string }>> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });
    formData.append("property_address", propertyAddress);

    return this.request<{ upload_id: string }>("/upload", {
      method: "POST",
      headers: {},
      body: formData,
    });
  }

  async analyzeProperty(
    uploadId: string,
    investmentCriteria?: any
  ): Promise<ApiResponse<DealAnalysis>> {
    return this.request<DealAnalysis>("/analyze", {
      method: "POST",
      body: JSON.stringify({
        upload_id: uploadId,
        investment_criteria: investmentCriteria,
      }),
    });
  }

  async getAnalysis(analysisId: string): Promise<ApiResponse<DealAnalysis>> {
    return this.request<DealAnalysis>(`/analysis/${analysisId}`);
  }

  async getUserAnalyses(): Promise<ApiResponse<DealAnalysis[]>> {
    return this.request<DealAnalysis[]>("/user/analyses");
  }

  async exportAnalysis(
    analysisId: string,
    format: "pdf" | "excel"
  ): Promise<ApiResponse<{ download_url: string }>> {
    return this.request<{ download_url: string }>(
      `/export/${analysisId}/${format}`
    );
  }
}

export const apiClient = new ApiClient();
