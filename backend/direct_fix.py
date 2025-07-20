import os
import re
import shutil

def fix_external_apis():
    print("Fixing external_apis.py...")
    
    # Path to the file
    file_path = "services/external_apis.py"
    backup_path = "services/external_apis.py.bak"
    
    # Backup original
    shutil.copy(file_path, backup_path)
    
    # Read the file content
    with open(file_path, "r") as f:
        content = f.read()
    
    # Add force_estimation parameter to the function
    pattern = r"def _get_basic_property_estimates\(self, address: str\)"
    replacement = "def _get_basic_property_estimates(self, address: str, force_estimation: bool = False)"
    content = re.sub(pattern, replacement, content)
    
    # Modify the condition to include force_estimation
    pattern = r"if is_likely_multifamily or has_unit_number:"
    replacement = "if is_likely_multifamily or has_unit_number or force_estimation:"
    content = re.sub(pattern, replacement, content)
    
    # Add single family and commercial estimation
    pattern = r"return None\s+# Don't estimate for non-multifamily"
    replacement = """            elif force_estimation:
                # For non-multifamily addresses with force_estimation
                if 'commercial' in address_lower or 'business' in address_lower or 'office' in address_lower or 'plaza' in address_lower:
                    property_type = "Commercial"
                    estimated_units = 1
                    estimated_sqft = 5000  # Conservative commercial estimate
                    estimated_value = estimated_sqft * 250  # $250 per sqft
                else:
                    property_type = "Single Family"
                    estimated_units = 1
                    estimated_sqft = 2000  # Average single family home
                    estimated_value = 450000  # Conservative home value
            
            return None  # No estimation if not multifamily and not forced"""
    content = re.sub(pattern, replacement, content)
    
    # Write back to the file
    with open(file_path, "w") as f:
        f.write(content)
    
    print("✅ Fixed external_apis.py")

def fix_main_py():
    print("Fixing main.py...")
    
    file_path = "main.py"
    backup_path = "main.py.bak"
    
    # Backup original
    shutil.copy(file_path, backup_path)
    
    # Read the file content
    with open(file_path, "r") as f:
        content = f.read()
    
    # Replace multifamily detection with smarter logic for all properties
    pattern = r"# DIRECT SMART ESTIMATION CHECK:.*?\n.*?property_data = await external_api_service\.get_property_data\(address\)"
    replacement = """# Check if address has multifamily indicators (for data quality flag)
        is_multifamily = any(indicator in address.lower() for indicator in ['apt', 'apartment', 'unit', 'suite', '#', 'complex', 'towers', 'plaza'])
        
        # First try to get real property data
        property_data = await external_api_service.get_property_data(address)
        
        # Check if we got meaningful data - if not, use smart estimation for ALL addresses
        has_meaningful_data = property_data.get("property_type") != "Unknown" or property_data.get("units", 0) > 0
        
        if not has_meaningful_data:
            print(f"No meaningful data for: {address} - using smart estimation")
            estimated_data = external_api_service._get_basic_property_estimates(address, force_estimation=True)
            if estimated_data:
                # We have estimation data - use it directly
                property_data = estimated_data"""
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Fix data quality section
    pattern = r"\"data_quality\": property_data\.get\(\"data_quality\", \{\}\) or \{.*?\n.*?\"is_estimated_data\": is_multifamily,"
    replacement = """"data_quality": property_data.get("data_quality", {}) or {
                        "is_estimated_data": True,  # Always mark as estimated if we had to fallback"""
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write back to the file
    with open(file_path, "w") as f:
        f.write(content)
    
    print("✅ Fixed main.py")

def main():
    print("🔧 Direct Fix Script for PropPulse AI")
    print("=" * 60)
    
    fix_external_apis()
    fix_main_py()
    
    print("\n✅ All fixes applied. Commit and push to deploy:")
    print("git add services/external_apis.py main.py")
    print("git commit -m \"Fix estimation for all property types\"")
    print("git push")

if __name__ == "__main__":
    main()
