"""
Quick fix for external_apis.py to ensure all property types get smart estimation
"""

import re
import fileinput
import sys
import os

def fix_external_apis():
    """Fix the external_apis.py file to provide estimates for all property types"""
    file_path = 'services/external_apis.py'
    
    # Define the search pattern and replacement
    search_pattern = r"""            # Basic estimates based on address patterns - either multifamily or forced estimation
            if is_likely_multifamily or has_unit_number or force_estimation:
                property_type = "Multifamily"
                
                # Estimate units based on address clues
                if unit_match:
                    # Get all valid unit numbers from the regex groups
                    unit_numbers = \[int\(g\) for g in unit_match.groups\(\) if g and g.isdigit\(\)\]
                    if unit_numbers:
                        unit_num = max\(unit_numbers\)
                        estimated_units = min\(max\(unit_num \+ 10, 20\), 100\)  # Reasonable range
                    else:
                        estimated_units = 48  # Default if no valid numbers found
                else:
                    estimated_units = 48  # Conservative multifamily estimate
                
                # Basic square footage estimate
                estimated_sqft = estimated_units \* 850  # Average unit size
                property_type = "Multifamily"
                
                # Basic value estimate \(conservative\)
                estimated_value = estimated_units \* 55000  # Conservative per-unit value
            elif force_estimation:
                # For non-multifamily addresses with force_estimation
                if 'commercial' in address_lower or 'business' in address_lower or 'office' in address_lower or 'plaza' in address_lower:
                    property_type = "Commercial"
                    estimated_units = 1
                    estimated_sqft = 5000  # Conservative commercial estimate
                    estimated_value = estimated_sqft \* 250  # \$250 per sqft
                else:
                    property_type = "Single Family"
                    estimated_units = 1
                    estimated_sqft = 2000  # Average single family home
                    estimated_value = 450000  # Conservative home value
            else:
                return None  # No estimation if not multifamily and not forced"""
    
    replacement = """            # First check for multifamily properties
            if is_likely_multifamily or has_unit_number:
                property_type = "Multifamily"
                
                # Estimate units based on address clues
                if unit_match:
                    # Get all valid unit numbers from the regex groups
                    unit_numbers = [int(g) for g in unit_match.groups() if g and g.isdigit()]
                    if unit_numbers:
                        unit_num = max(unit_numbers)
                        estimated_units = min(max(unit_num + 10, 20), 100)  # Reasonable range
                    else:
                        estimated_units = 48  # Default if no valid numbers found
                else:
                    estimated_units = 48  # Conservative multifamily estimate
                
                # Basic square footage estimate
                estimated_sqft = estimated_units * 850  # Average unit size
                
                # Basic value estimate (conservative)
                estimated_value = estimated_units * 55000  # Conservative per-unit value
            # Then check for commercial properties or if force_estimation is on
            elif ('commercial' in address_lower or 'business' in address_lower or 
                  'office' in address_lower or 'plaza' in address_lower) or force_estimation:
                # Check if it's likely commercial
                if ('commercial' in address_lower or 'business' in address_lower or 
                    'office' in address_lower or 'plaza' in address_lower):
                    property_type = "Commercial"
                    estimated_units = 1
                    estimated_sqft = 5000  # Conservative commercial estimate
                    estimated_value = estimated_sqft * 250  # $250 per sqft
                # Otherwise assume single family when force_estimation is true
                else:
                    property_type = "Single Family"
                    estimated_units = 1
                    estimated_sqft = 2000  # Average single family home
                    estimated_value = 450000  # Conservative home value
            else:
                return None  # No estimation if not multifamily and not forced"""
                
    # Read the file content
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Replace the pattern
    updated_content = re.sub(search_pattern, replacement, content)
    
    # Write back to the file
    with open(file_path, 'w') as file:
        file.write(updated_content)
        
    print("✅ external_apis.py updated successfully")

def main():
    os.chdir('/app/backend')  # Move to the backend directory in Railway
    print("Current working directory:", os.getcwd())
    fix_external_apis()
    print("All fixes applied successfully!")

if __name__ == "__main__":
    main()
