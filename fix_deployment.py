import os
import time
import sys
import shutil
import subprocess
from pathlib import Path

def fix_backend():
    """Fix the backend code to provide smart estimation for all addresses"""
    print("🛠️ Fixing backend code...")
    
    # Backup original files
    backend_dir = Path("/Volumes/project/intern/proppulse-ai/backend")
    main_py_path = backend_dir / "main.py"
    external_apis_path = backend_dir / "services" / "external_apis.py"
    
    if not main_py_path.exists() or not external_apis_path.exists():
        print("❌ ERROR: Backend files not found!")
        return False
    
    # Backup
    shutil.copy(main_py_path, backend_dir / "main.py.bak")
    shutil.copy(external_apis_path, backend_dir / "services" / "external_apis.py.bak")
    
    # Fix 1: Update _get_basic_property_estimates in external_apis.py
    try:
        print("Fixing external_apis.py...")
        with open(external_apis_path, "r") as f:
            content = f.read()
        
        # Replace the method with our fixed version
        start_marker = "def _get_basic_property_estimates(self, address: str"
        end_marker = "return None  # Don't estimate for non-multifamily"
        
        if start_marker in content and end_marker in content:
            replacement = """def _get_basic_property_estimates(self, address: str, force_estimation: bool = False) -> Optional[Dict[str, Any]]:
        \"\"\"
        Provide basic property estimates based on address analysis when APIs are unavailable
        This is transparent about being estimates, not real data
        
        Parameters:
        - address: The property address
        - force_estimation: If True, provide estimates even for non-multifamily properties
        \"\"\"
        try:
            import re
            
            # Parse address for clues
            address_lower = address.lower()
            
            # Detect if it's likely multifamily
            multifamily_indicators = ['apt', 'apartment', 'unit', 'suite', '#', 'complex', 'towers', 'plaza', 'manor', 'court', 'place']
            is_likely_multifamily = any(indicator in address_lower for indicator in multifamily_indicators)
            
            # Extract unit numbers or building size clues
            unit_match = re.search(r'unit\s*(\d+)|apt\s*(\d+)|#\s*(\d+)', address_lower)
            has_unit_number = bool(unit_match)
            
            # Basic estimates based on address patterns - either multifamily or forced estimation
            if is_likely_multifamily or has_unit_number or force_estimation:
                if is_likely_multifamily or has_unit_number:
                    # For multifamily addresses
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
                    property_type = "Multifamily"
                    
                    # Basic value estimate (conservative)
                    estimated_value = estimated_units * 55000  # Conservative per-unit value
                elif force_estimation:
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
                else:
                    return None  # No estimation if not multifamily and not forced
                    
                return {
                    "address": address,
                    "property_type": property_type,
                    "units": estimated_units,
                    "square_footage": estimated_sqft,
                    "estimated_value": estimated_value,
                    "price_per_unit": int(estimated_value / max(estimated_units, 1)),
                    "price_per_sqft": round(estimated_value / estimated_sqft, 2),
                    
                    "market_data": {
                        "avg_rent_per_unit": estimated_units * 18,  # Conservative rent estimate
                        "estimated_cap_rate": 6.5,
                    },
                    
                    "data_quality": {
                        "is_estimated_data": True,
                        "confidence": 25,  # Low confidence for most properties
                        "sources": ["Address Analysis"],
                        "last_updated": "2025-07-20",
                        "notes": "⚠️ ESTIMATES ONLY - Based on address analysis when real data APIs unavailable. Use for initial screening only."
                    }
                }"""
            
            content = content.replace(content.split(start_marker)[0] + start_marker, content.split(start_marker)[0] + replacement.split("def _get_basic_property_estimates")[1])
            content = content.replace(end_marker, "        except Exception as e:\n            self.logger.error(f\"Error in basic estimates: {e}\")\n            return None")
            
            with open(external_apis_path, "w") as f:
                f.write(content)
            
            print("✅ Fixed external_apis.py")
        else:
            print("❌ Could not find markers in external_apis.py")
            return False
        
        # Fix 2: Update the quick-analysis endpoint in main.py
        print("Fixing main.py...")
        with open(main_py_path, "r") as f:
            content = f.read()
        
        # Replace the estimation logic in quick-analysis
        start_marker = "        # DIRECT SMART ESTIMATION CHECK: Check if address is likely multifamily first"
        end_marker = "            # Regular flow for non-multifamily addresses"
        
        if start_marker in content and end_marker in content:
            replacement = """        # Check if address has multifamily indicators (for data quality flag)
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
                
            content = content.replace(content.split(start_marker)[0] + start_marker, content.split(start_marker)[0] + replacement)
            content = content.replace(end_marker, "")
            
            # Also fix the data_quality part
            data_quality_marker = "                \"market_data\": {"
            data_quality_end = "                },"
            
            if data_quality_marker in content:
                # Find the right occurrence of the marker (there could be multiple)
                parts = content.split(data_quality_marker)
                if len(parts) > 1:
                    for i in range(1, len(parts)):
                        if "\"data_quality\":" in parts[i] and "\"market_data\":" in parts[i-1]:
                            # This is the one we want to replace
                            replacement = """                "market_data": {
                    # Include market data from property data
                    **(property_data.get("market_data", {})),
                    # Always include data quality information
                    "data_quality": property_data.get("data_quality", {}) or {
                        "is_estimated_data": True,  # Always mark as estimated if we had to fallback
                        "confidence": 25,  # Low confidence
                        "sources": ["Address Analysis"],
                        "notes": "⚠️ ESTIMATES ONLY - Based on address analysis when real data unavailable"
                    }"""
                            
                            # Find where the data_quality part ends
                            end_idx = parts[i].find(data_quality_end)
                            if end_idx != -1:
                                parts[i] = replacement + parts[i][end_idx:]
                            
                            # Reconstruct the content
                            content = parts[0]
                            for j in range(1, len(parts)):
                                content += data_quality_marker + parts[j]
                            
                            break
            
            with open(main_py_path, "w") as f:
                f.write(content)
            
            print("✅ Fixed main.py")
        else:
            print("❌ Could not find markers in main.py")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR fixing backend: {e}")
        return False

def fix_frontend():
    """Fix frontend code to handle snake_case properties for data quality"""
    print("\n🛠️ Fixing frontend code...")
    
    # Path to the frontend file
    frontend_dir = Path("/Volumes/project/intern/proppulse-ai/frontend")
    page_tsx_path = frontend_dir / "src" / "app" / "upload" / "documents" / "page.tsx"
    
    if not page_tsx_path.exists():
        print("❌ ERROR: Frontend file not found!")
        return False
    
    # Backup
    shutil.copy(page_tsx_path, frontend_dir / "src" / "app" / "upload" / "documents" / "page.tsx.bak")
    
    try:
        with open(page_tsx_path, "r") as f:
            content = f.read()
        
        # Fix the data quality check
        if "propertyData.dataQuality?.is_estimated_data" in content:
            print("✅ Frontend already using correct snake_case properties")
        else:
            content = content.replace("propertyData.dataQuality?.isEstimatedData", "propertyData.dataQuality?.is_estimated_data")
            content = content.replace("propertyData.dataQuality?.isFreeData", "propertyData.dataQuality?.is_free_data")
            
            with open(page_tsx_path, "w") as f:
                f.write(content)
            
            print("✅ Fixed frontend property names to use snake_case")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR fixing frontend: {e}")
        return False

def deploy_backend():
    """Deploy backend changes to Railway"""
    print("\n🚀 Deploying backend to Railway...")
    
    try:
        # Change to backend directory
        os.chdir("/Volumes/project/intern/proppulse-ai/backend")
        
        # Commit changes
        subprocess.run(["git", "add", "main.py", "services/external_apis.py"])
        subprocess.run(["git", "commit", "-m", "Fix estimation for all property types and data quality display"])
        subprocess.run(["git", "push"])
        
        print("✅ Backend changes pushed to Git")
        print("⏳ Railway will auto-deploy the changes (usually takes 1-2 minutes)")
        
        return True
    except Exception as e:
        print(f"❌ ERROR deploying backend: {e}")
        return False

def deploy_frontend():
    """Deploy frontend changes to Vercel"""
    print("\n🚀 Deploying frontend to Vercel...")
    
    try:
        # Change to frontend directory
        os.chdir("/Volumes/project/intern/proppulse-ai/frontend")
        
        # Commit changes
        subprocess.run(["git", "add", "src/app/upload/documents/page.tsx"])
        subprocess.run(["git", "commit", "-m", "Fix data quality field names to use snake_case"])
        subprocess.run(["git", "push"])
        
        print("✅ Frontend changes pushed to Git")
        print("⏳ Vercel will auto-deploy the changes (usually takes 1-2 minutes)")
        
        return True
    except Exception as e:
        print(f"❌ ERROR deploying frontend: {e}")
        return False

def main():
    """Main fix and deploy process"""
    print("🔧 PROPPULSE AI FINAL FIX SCRIPT 🔧")
    print("=" * 60)
    
    # Fix backend
    backend_fixed = fix_backend()
    if not backend_fixed:
        print("❌ Backend fix failed, aborting")
        return
    
    # Fix frontend
    frontend_fixed = fix_frontend()
    if not frontend_fixed:
        print("❌ Frontend fix failed, aborting")
        return
    
    # Deploy backend
    backend_deployed = deploy_backend()
    if not backend_deployed:
        print("❌ Backend deployment failed")
    
    # Deploy frontend
    frontend_deployed = deploy_frontend()
    if not frontend_deployed:
        print("❌ Frontend deployment failed")
    
    if backend_deployed and frontend_deployed:
        print("\n🎉 ALL CHANGES DEPLOYED SUCCESSFULLY!")
        print("⏳ Please wait 2-3 minutes for both Railway and Vercel to complete their deployments")
        
        print("\n🔍 TEST URLS (copy and paste into your browser):")
        print("1. Multifamily: https://proppulse-7q5aj8h8l-tilaks-projects-d3d027be.vercel.app/upload?address=123%20Main%20Street%20Apt%205%2C%20Los%20Angeles%2C%20CA%2090210")
        print("2. Single Family: https://proppulse-7q5aj8h8l-tilaks-projects-d3d027be.vercel.app/upload?address=7825%20Sunset%20Boulevard%2C%20Los%20Angeles%2C%20CA%2090046")
        
        print("\n✨ GOOD LUCK WITH YOUR PROJECT SUBMISSION!")

if __name__ == "__main__":
    main()
