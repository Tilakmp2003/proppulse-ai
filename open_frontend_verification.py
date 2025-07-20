import webbrowser
import urllib.parse
import time

def open_test_urls():
    """Open test URLs to verify frontend display of estimated property data"""
    frontend_base_url = "https://proppulse-7q5aj8h8l-tilaks-projects-d3d027be.vercel.app/upload?address="
    
    addresses = [
        # Single family home
        "123 Main St, Austin, TX 78701",
        
        # Commercial property
        "789 Office Plaza, Dallas, TX 75201",
        
        # Multifamily property
        "Wilshire Plaza, 5678 Wilshire Blvd, Los Angeles, CA 90036"
    ]
    
    for i, address in enumerate(addresses):
        encoded_address = urllib.parse.quote(address)
        url = f"{frontend_base_url}{encoded_address}"
        
        print(f"\nOpening test URL {i+1}/{len(addresses)}:")
        print(f"Address: {address}")
        print(f"URL: {url}")
        
        # Open URL in browser
        webbrowser.open(url)
        
        # Wait before opening next URL to avoid overwhelming the browser
        if i < len(addresses) - 1:
            time.sleep(5)
    
    print("\nVerification URLs opened in browser.")
    print("Please check each one to verify that:")
    print("1. Property data is shown for all addresses (no 'Not available')")
    print("2. 'Estimated Data' badge appears when data is estimated")
    print("3. No empty or default values are displayed")

if __name__ == "__main__":
    open_test_urls()
