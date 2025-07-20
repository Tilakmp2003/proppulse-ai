import requests

api_url = 'http://localhost:8000'

def test_address(address):
    print(f'\nTesting address: {address}')
    response = requests.post(
        f'{api_url}/quick-analysis',
        json={'address': address}
    )
    
    if response.status_code != 200:
        print(f'Error: {response.status_code}, {response.text}')
        return
    
    data = response.json()
    property_details = data.get('analysis_result', {}).get('property_details', {})
    market_data = data.get('analysis_result', {}).get('market_data', {})
    data_quality = market_data.get('data_quality', {})
    
    print(f'Property Type: {property_details.get("property_type")}')
    print(f'Units: {property_details.get("units")}')
    print(f'Square Footage: {property_details.get("square_footage")}')
    print(f'Market Value: ${property_details.get("market_value")}')
    print(f'Price per Unit: ${property_details.get("price_per_unit")}')
    print(f'Price per Sqft: ${property_details.get("price_per_sqft")}')
    print(f'Data Quality: {"Estimated" if data_quality.get("is_estimated_data") else "Real"} data')
    print(f'Notes: {data_quality.get("notes")}')

# Test a clear single family home address
test_address('123 Main St, Anytown USA')

# Test a commercial address
test_address('123 Office Plaza, Business District, Anytown USA')

# Test a multifamily address
test_address('Wilshire Apartment Complex, 5678 Wilshire Blvd, Los Angeles, CA')
