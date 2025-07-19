// Test script to check property data from the backend
// Using global fetch (works in modern Node.js)

async function testPropertyAPI() {
  const address =
    "5678, Wilshire Boulevard, Miracle Mile, Mid-Wilshire, Los Angeles, Los Angeles County, California, 90036, United States";

  try {
    console.log(`Testing quick-analysis API with address: ${address}`);
    const API_URL =
      process.env.NEXT_PUBLIC_API_URL ||
      "https://proppulse-ai-production.up.railway.app";

    const response = await fetch(`${API_URL}/quick-analysis`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ address }),
    });

    if (response.ok) {
      const data = await response.json();
      console.log("API Response:");
      console.log(JSON.stringify(data, null, 2));

      // Check specific values
      console.log("\nSpecific values:");
      console.log("Units:", data.analysis_result?.property_details?.units);
      console.log(
        "Year Built:",
        data.analysis_result?.property_details?.year_built
      );
      console.log(
        "Square Footage:",
        data.analysis_result?.property_details?.square_footage
      );
      console.log(
        "Market Value:",
        data.analysis_result?.property_details?.market_value
      );
      console.log(
        "Neighborhood:",
        data.analysis_result?.neighborhood_info?.location_quality ||
          data.analysis_result?.neighborhood_data?.location_quality
      );
      console.log(
        "Walk Score:",
        data.analysis_result?.neighborhood_info?.walkability_score ||
          data.analysis_result?.neighborhood_data?.walkability_score
      );
    } else {
      console.error("Error from API:", response.status);
      console.error(await response.text());
    }
  } catch (error) {
    console.error("Error testing API:", error.message);
  }
}

testPropertyAPI();
