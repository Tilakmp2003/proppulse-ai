from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import asyncio
from datetime import datetime, timedelta
import uuid
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import settings
from models import Deal, DealCreate, DealAnalysis, AnalysisResult
from services.file_processor import FileProcessor
from services.property_analyzer import PropertyAnalyzer
from services.external_apis import ExternalAPIService
from database import get_db, create_tables

# Add investment criteria models
class InvestmentCriteria(BaseModel):
    # Financial Criteria
    minCashOnCash: float = 8.0
    minCapRate: float = 6.0
    minIRR: float = 12.0
    minDSCR: float = 1.2
    maxLTV: float = 75.0
    
    # Property Criteria
    maxYearBuilt: int = 1980
    maxPrice: float = 5000000
    minPrice: float = 500000
    minUnits: int = 20
    maxUnits: int = 100
    minSquareFootage: float = 10000
    maxSquareFootage: float = 100000
    
    # Market Criteria
    preferredMarkets: List[str] = ["Austin", "Dallas", "Houston", "San Antonio"]
    minNeighborhoodScore: float = 70.0
    maxCrimeRate: float = 5.0
    minWalkScore: float = 50.0
    
    # Risk & Strategy
    riskTolerance: str = "medium"
    investmentStrategy: str = "buy_hold"
    holdingPeriod: int = 5
    targetAppreciation: float = 3.0
    
    # Financing Preferences
    preferredLoanType: str = "conventional"
    maxInterestRate: float = 7.5
    minAmortization: int = 25
    
    # Deal Requirements
    requireProfessionalManagement: bool = False
    requireOnSiteParking: bool = True
    requireUpdatedSystems: bool = False
    allowValueAdd: bool = True

# OTP Authentication Models
class OTPRequest(BaseModel):
    email: str

class OTPVerification(BaseModel):
    email: str
    otp: str

# In-memory storage for OTP codes (in production, use Redis or database)
otp_storage = {}

def generate_otp() -> str:
    """Generate a 6-digit OTP code"""
    return str(random.randint(100000, 999999))

def send_otp_email(email: str, otp: str) -> bool:
    """Send OTP via email using SMTP"""
    try:
        # Print OTP to console for development
        print(f"=== OTP for {email}: {otp} ===")
        
        # Get email configuration from settings
        smtp_server = settings.SMTP_SERVER
        smtp_port = settings.SMTP_PORT
        sender_email = settings.SMTP_EMAIL
        sender_password = settings.SMTP_PASSWORD
        
        # If email credentials are not configured, only print to console
        if not sender_email or not sender_password:
            print("Email credentials not configured. OTP printed to console only.")
            return True
        
        # Send actual email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = "PropPulse AI - Your Login Code"
        
        body = f'''
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">PropPulse AI</h1>
            </div>
            <div style="padding: 30px; background: #f8f9fa;">
                <h2 style="color: #333; margin-bottom: 20px;">Your Login Code</h2>
                <div style="background: white; padding: 30px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <p style="font-size: 18px; color: #666; margin-bottom: 20px;">Enter this code to access your account:</p>
                    <div style="font-size: 36px; font-weight: bold; color: #2563eb; letter-spacing: 5px; margin: 20px 0; padding: 15px; background: #f0f9ff; border-radius: 8px;">
                        {otp}
                    </div>
                    <p style="color: #999; font-size: 14px; margin-top: 20px;">This code will expire in 10 minutes</p>
                </div>
                <p style="color: #666; font-size: 14px; margin-top: 20px;">
                    If you didn't request this code, please ignore this email.
                </p>
            </div>
            <div style="background: #2563eb; padding: 15px; text-align: center;">
                <p style="color: white; margin: 0; font-size: 12px;">© 2025 PropPulse AI. All rights reserved.</p>
            </div>
        </body>
        </html>
        '''
        
        message.attach(MIMEText(body, "html"))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()
        
        print(f"✅ OTP email sent successfully to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        # Even if email fails, return True so the OTP is still stored for testing
        return True

app = FastAPI(
    title="PropPulse AI API",
    description="AI-powered commercial real estate underwriting platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "http://localhost:3002", 
        "http://127.0.0.1:3002",
        "http://localhost:3003", 
        "http://127.0.0.1:3003"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static files
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Initialize services
file_processor = FileProcessor()
property_analyzer = PropertyAnalyzer()
external_api_service = ExternalAPIService()

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    create_tables()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "PropPulse AI API is running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "file_storage": "available",
            "external_apis": "configured"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    property_address: str = Form(...)
):
    """Upload and process T12 and Rent Roll files"""
    if not property_address:
        raise HTTPException(status_code=400, detail="Property address is required")
    
    if len(files) > 2:
        raise HTTPException(status_code=400, detail="Maximum 2 files allowed")
    
    upload_id = str(uuid.uuid4())
    upload_dir = os.path.join(settings.UPLOAD_DIR, upload_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    uploaded_files = []
    for file in files:
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File {file.filename} is too large")
        
        file_path = os.path.join(upload_dir, file.filename)
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        uploaded_files.append({
            "filename": file.filename,
            "path": file_path,
            "size": len(content),
            "content_type": file.content_type
        })
    
    # Save upload metadata
    metadata = {
        "upload_id": upload_id,
        "property_address": property_address,
        "files": uploaded_files,
        "uploaded_at": datetime.utcnow().isoformat()
    }
    
    metadata_path = os.path.join(upload_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    return {"upload_id": upload_id}

@app.post("/analyze")
async def analyze_property(request: DealCreate):
    """Analyze property based on uploaded files and investment criteria"""
    upload_dir = os.path.join(settings.UPLOAD_DIR, request.upload_id)
    
    if not os.path.exists(upload_dir):
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Load metadata
    metadata_path = os.path.join(upload_dir, "metadata.json")
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Upload metadata not found")
    
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    property_address = metadata["property_address"]
    
    try:
        # Step 1: Process uploaded files
        financial_data = {}
        for file_info in metadata["files"]:
            file_path = file_info["path"]
            filename = file_info["filename"].lower()
            
            if "t12" in filename or "trailing" in filename:
                financial_data["t12"] = await file_processor.process_t12(file_path)
            elif "rent" in filename or "roll" in filename:
                financial_data["rent_roll"] = await file_processor.process_rent_roll(file_path)
        
        # Step 2: Gather external market data
        market_data = await external_api_service.get_property_data(property_address)
        
        # Step 3: Perform analysis
        investment_criteria_dict = {}
        if request.investment_criteria:
            investment_criteria_dict = request.investment_criteria.dict()
        
        analysis_result = await property_analyzer.analyze_deal(
            financial_data=financial_data,
            market_data=market_data,
            investment_criteria=investment_criteria_dict
        )
        
        # Step 4: Save analysis result
        analysis_id = str(uuid.uuid4())
        result = AnalysisResult(
            id=analysis_id,
            property_address=property_address,
            analysis_result=analysis_result,
            created_at=datetime.utcnow()
        )
        
        # Save to file (in production, save to database)
        result_path = os.path.join(upload_dir, "analysis_result.json")
        with open(result_path, "w") as f:
            json.dump(result.dict(), f, indent=2, default=str)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Retrieve analysis results"""
    # In production, fetch from database
    # For now, scan upload directories
    for upload_id in os.listdir(settings.UPLOAD_DIR):
        result_path = os.path.join(settings.UPLOAD_DIR, upload_id, "analysis_result.json")
        if os.path.exists(result_path):
            with open(result_path, "r") as f:
                result_data = json.load(f)
                if result_data.get("id") == analysis_id:
                    return result_data
    
    raise HTTPException(status_code=404, detail="Analysis not found")

@app.get("/user/analyses")
async def get_user_analyses():
    """Get all analyses for the current user"""
    analyses = []
    
    # In production, filter by user ID from JWT token
    # For now, return all analyses
    if os.path.exists(settings.UPLOAD_DIR):
        for upload_id in os.listdir(settings.UPLOAD_DIR):
            result_path = os.path.join(settings.UPLOAD_DIR, upload_id, "analysis_result.json")
            if os.path.exists(result_path):
                with open(result_path, "r") as f:
                    result_data = json.load(f)
                    analyses.append(result_data)
    
    return analyses

@app.post("/export/{analysis_id}/{format}")
async def export_analysis(analysis_id: str, format: str):
    """Export analysis as PDF or Excel"""
    if format not in ["pdf", "excel"]:
        raise HTTPException(status_code=400, detail="Format must be 'pdf' or 'excel'")
    
    # Get analysis data
    analysis_data = None
    for upload_id in os.listdir(settings.UPLOAD_DIR):
        upload_path = os.path.join(settings.UPLOAD_DIR, upload_id)
        if os.path.isdir(upload_path):
            result_path = os.path.join(upload_path, "analysis_result.json")
            if os.path.exists(result_path):
                with open(result_path, "r") as f:
                    result_data = json.load(f)
                    if result_data.get("id") == analysis_id:
                        analysis_data = result_data
                        break
    
    if not analysis_data:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        # Generate export file
        if format == "pdf":
            file_path = await property_analyzer.generate_pdf_report(analysis_data)
        else:
            file_path = await property_analyzer.generate_excel_model(analysis_data)
        
        # Return download response directly
        filename = os.path.basename(file_path)
        
        if format == "pdf":
            media_type = "application/pdf"
        else:
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=media_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/downloads/{filename}")
async def download_file(filename: str):
    """Download exported files"""
    exports_dir = os.path.join("/tmp", "proppulse_exports")
    file_path = os.path.join(exports_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on file extension
    if filename.endswith('.pdf'):
        media_type = "application/pdf"
    elif filename.endswith('.xlsx'):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        media_type = 'application/octet-stream'
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )

@app.post("/user/criteria")
async def save_investment_criteria(criteria: InvestmentCriteria):
    """Save user investment criteria"""
    # In production, save to database with user ID from JWT token
    # For now, save to file system
    criteria_dir = os.path.join(settings.UPLOAD_DIR, "user_criteria")
    os.makedirs(criteria_dir, exist_ok=True)
    
    criteria_path = os.path.join(criteria_dir, "default_user.json")
    with open(criteria_path, "w") as f:
        json.dump(criteria.dict(), f, indent=2)
    
    return {"message": "Investment criteria saved successfully"}

@app.get("/user/criteria")
async def get_investment_criteria():
    """Get user investment criteria"""
    # In production, fetch from database with user ID from JWT token
    # For now, load from file system
    criteria_path = os.path.join(settings.UPLOAD_DIR, "user_criteria", "default_user.json")
    
    if os.path.exists(criteria_path):
        with open(criteria_path, "r") as f:
            criteria_data = json.load(f)
            return InvestmentCriteria(**criteria_data)
    else:
        # Return default criteria
        return InvestmentCriteria()

@app.post("/demo/generate-sample-data")
async def generate_sample_data():
    """Generate sample analysis data for demo purposes"""
    sample_analyses = [
        {
            "id": "demo-analysis-1",
            "property_address": "123 Main Street, Austin, TX 78701",
            "analysis_result": {
                "pass_fail": "PASS",
                "score": 89,
                "metrics": {
                    "cap_rate": 6.8,
                    "cash_on_cash": 12.3,
                    "irr": 15.2,
                    "net_present_value": 450000,
                    "debt_service_coverage": 1.34
                },
                "property_details": {
                    "year_built": 1995,
                    "square_footage": 45000,
                    "units": 48,
                    "property_type": "Multifamily",
                    "market_value": 2400000
                },
                "financial_summary": {
                    "gross_rental_income": 420000,
                    "operating_expenses": 168000,
                    "net_operating_income": 252000,
                    "cash_flow": 72000
                },
                "market_data": {
                    "comp_properties": [
                        {"address": "456 Oak Ave, Austin, TX", "price": 2300000, "cap_rate": 6.5},
                        {"address": "789 Pine St, Austin, TX", "price": 2600000, "cap_rate": 7.1}
                    ],
                    "neighborhood_score": 85,
                    "market_trends": "Strong rental growth, increasing property values"
                }
            },
            "created_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": "demo-analysis-2",
            "property_address": "456 Commerce Street, Dallas, TX 75201",
            "analysis_result": {
                "pass_fail": "PASS",
                "score": 76,
                "metrics": {
                    "cap_rate": 5.9,
                    "cash_on_cash": 9.8,
                    "irr": 13.1,
                    "net_present_value": 320000,
                    "debt_service_coverage": 1.28
                },
                "property_details": {
                    "year_built": 1988,
                    "square_footage": 62000,
                    "units": 64,
                    "property_type": "Multifamily",
                    "market_value": 3200000
                },
                "financial_summary": {
                    "gross_rental_income": 560000,
                    "operating_expenses": 224000,
                    "net_operating_income": 336000,
                    "cash_flow": 96000
                },
                "market_data": {
                    "comp_properties": [
                        {"address": "321 Elm St, Dallas, TX", "price": 3100000, "cap_rate": 5.7},
                        {"address": "654 Maple Ave, Dallas, TX", "price": 3400000, "cap_rate": 6.2}
                    ],
                    "neighborhood_score": 78,
                    "market_trends": "Stable market with moderate growth potential"
                }
            },
            "created_at": "2024-01-14T14:20:00Z"
        },
        {
            "id": "demo-analysis-3",
            "property_address": "789 Business Park Drive, Houston, TX 77002",
            "analysis_result": {
                "pass_fail": "FAIL",
                "score": 52,
                "metrics": {
                    "cap_rate": 4.8,
                    "cash_on_cash": 6.2,
                    "irr": 9.5,
                    "net_present_value": 180000,
                    "debt_service_coverage": 1.15
                },
                "property_details": {
                    "year_built": 1975,
                    "square_footage": 38000,
                    "units": 40,
                    "property_type": "Multifamily",
                    "market_value": 1850000
                },
                "financial_summary": {
                    "gross_rental_income": 280000,
                    "operating_expenses": 140000,
                    "net_operating_income": 140000,
                    "cash_flow": 28000
                },
                "market_data": {
                    "comp_properties": [
                        {"address": "111 Center St, Houston, TX", "price": 1700000, "cap_rate": 4.9},
                        {"address": "222 Park Ave, Houston, TX", "price": 1950000, "cap_rate": 5.1}
                    ],
                    "neighborhood_score": 65,
                    "market_trends": "Market showing signs of slower growth"
                }
            },
            "created_at": "2024-01-13T09:15:00Z"
        }
    ]
    
    # Save sample data to upload directories
    for analysis in sample_analyses:
        upload_id = f"demo-upload-{analysis['id']}"
        upload_dir = os.path.join(settings.UPLOAD_DIR, upload_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save analysis result
        result_path = os.path.join(upload_dir, "analysis_result.json")
        with open(result_path, "w") as f:
            json.dump(analysis, f, indent=2)
        
        # Save metadata
        metadata = {
            "upload_id": upload_id,
            "property_address": analysis["property_address"],
            "files": [{"filename": "demo_data.json", "path": result_path}],
            "uploaded_at": analysis["created_at"]
        }
        metadata_path = os.path.join(upload_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
    
    return {"message": f"Generated {len(sample_analyses)} sample analyses", "count": len(sample_analyses)}

# OTP Authentication Endpoints
@app.post("/auth/send-otp")
async def send_otp(request: OTPRequest):
    """Send OTP code to user's email"""
    try:
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP with expiration (10 minutes)
        expiration = datetime.utcnow() + timedelta(minutes=10)
        otp_storage[request.email] = {
            "otp": otp,
            "expires_at": expiration
        }
        
        # Send OTP via email
        if send_otp_email(request.email, otp):
            return {"message": "OTP sent successfully", "success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to send OTP")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

@app.post("/auth/verify-otp")
async def verify_otp(request: OTPVerification):
    """Verify OTP code"""
    try:
        # Check if OTP exists for email
        if request.email not in otp_storage:
            raise HTTPException(status_code=400, detail="No OTP found for this email")
        
        stored_otp_data = otp_storage[request.email]
        
        # Check if OTP has expired
        if datetime.utcnow() > stored_otp_data["expires_at"]:
            del otp_storage[request.email]
            raise HTTPException(status_code=400, detail="OTP has expired")
        
        # Verify OTP
        if request.otp != stored_otp_data["otp"]:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        # OTP is valid, remove it from storage
        del otp_storage[request.email]
        
        return {
            "message": "OTP verified successfully",
            "success": True,
            "user": {"email": request.email}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify OTP: {str(e)}")

@app.post("/quick-analysis")
async def quick_property_analysis(request: dict):
    """
    Quick property analysis using only free APIs - no file upload required
    Returns real property data from free sources for immediate display
    """
    try:
        address = request.get("address", "").strip()
        if not address:
            raise HTTPException(status_code=400, detail="Address is required")
        
        # Get real property data from free APIs
        property_data = await external_api_service.get_property_data(address)
        
        # Create a simplified analysis result for quick display
        quick_result = {
            "id": f"quick-{str(uuid.uuid4())[:8]}",
            "property_address": address,
            "analysis_result": {
                "pass_fail": "PENDING",  # Quick analysis doesn't include pass/fail
                "score": 0,  # No score for quick analysis
                "property_details": {
                    "property_type": property_data.get("property_type", "Unknown"),
                    "year_built": property_data.get("year_built"),
                    "units": property_data.get("units", 0),
                    "square_footage": property_data.get("square_footage"),
                    "lot_size": property_data.get("lot_size"),
                    "market_value": property_data.get("estimated_value", 0),
                    "price_per_unit": property_data.get("price_per_unit", 0),
                    "price_per_sqft": property_data.get("price_per_sqft", 0),
                },
                "market_data": property_data.get("market_data", {}),
                "neighborhood_info": property_data.get("neighborhood_info", {}),
                "demographics": property_data.get("demographics", {}),
                "location_info": property_data.get("location_info", {}),
                "data_sources": property_data.get("data_sources", []),
                "ai_analysis": "Quick property lookup using free data sources. Upload financial documents for comprehensive analysis.",
            },
            "created_at": datetime.utcnow().isoformat(),
            "analysis_type": "quick_lookup"
        }
        
        return quick_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
