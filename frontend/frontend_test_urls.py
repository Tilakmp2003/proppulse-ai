import requests
import json
import webbrowser
from urllib.parse import quote

def test_frontend_fix():
    """Test the frontend with different addresses after fixes"""
    
    # Test addresses (multifamily and regular)
    addresses = [
        "123 Main Street Apt 5, Los Angeles, CA 90210",  # Multifamily with unit number
        "7825 Sunset Boulevard, Los Angeles, CA 90046",  # Regular single-family
        "Gateway Business Plaza, 1200 Commerce St, Dallas, TX 75202",  # Commercial
    ]
    
    # Generate frontend URLs for testing
    frontend_base_url = "https://proppulse-7q5aj8h8l-tilaks-projects-d3d027be.vercel.app/upload?address="
    
    print("\n🔍 FRONTEND TEST URLS\n" + "=" * 60)
    for address in addresses:
        encoded_address = quote(address)
        url = f"{frontend_base_url}{encoded_address}"
        print(f"\n🏢 Address: {address}")
        print(f"🌐 URL: {url}")
    
    print("\n✨ Please copy and paste these URLs to test in your browser")
    print("After the backend changes are deployed, ALL addresses should show estimated data with badges")

if __name__ == "__main__":
    test_frontend_fix()
