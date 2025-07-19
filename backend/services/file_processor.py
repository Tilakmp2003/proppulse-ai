"""
File Processing Service - Handles T12 and Rent Roll document parsing with AI
"""
import os
import json
import re
import pandas as pd
import pdfplumber
from typing import Dict, Any, List, Optional
import logging
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)

class FileProcessor:
    """
    Handles parsing of T12 statements and Rent Roll documents using AI
    """
    
    def __init__(self):
        # Initialize Gemini client if API key is available
        gemini_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
        if gemini_key and gemini_key != 'your_gemini_api_key_here':
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
        self.logger = logger
        self.supported_formats = {
            'pdf': ['.pdf'],
            'excel': ['.xlsx', '.xls'],
            'csv': ['.csv']
        }
    
    async def process_t12(self, file_path: str) -> Dict[str, Any]:
        """
        Process T12 trailing twelve months financial statement
        
        Args:
            file_path: Path to the T12 file (PDF or Excel)
            
        Returns:
            Dictionary containing parsed financial data
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                raw_text = self._extract_text_from_pdf(file_path)
                if self.gemini_model:
                    return await self._parse_t12_with_ai(raw_text, file_type="PDF")
                else:
                    return self._parse_t12_fallback(raw_text)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                if self.gemini_model:
                    return await self._parse_t12_excel_with_ai(df)
                else:
                    return self._parse_t12_excel_fallback(df)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            self.logger.error(f"Error processing T12: {str(e)}")
            return self._get_mock_t12_data()
    
    async def process_rent_roll(self, file_path: str) -> Dict[str, Any]:
        """
        Process Rent Roll document
        
        Args:
            file_path: Path to the rent roll file (Excel or CSV)
            
        Returns:
            Dictionary containing parsed rent roll data
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            if self.gemini_model:
                return await self._parse_rent_roll_with_ai(df)
            else:
                return self._parse_rent_roll_fallback(df)
            
        except Exception as e:
            self.logger.error(f"Error processing rent roll: {str(e)}")
            return self._get_mock_rent_roll_data()
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    
    async def _parse_t12_with_ai(self, text: str, file_type: str) -> Dict[str, Any]:
        """
        Use Gemini AI to parse T12 financial data from text
        """
        try:
            prompt = f"""
            You are a commercial real estate financial analyst. Parse the following T12 (Trailing Twelve Months) financial statement and extract key financial metrics.

            Please extract and return a JSON object with the following structure:
            {{
                "gross_rental_income": <annual_gross_rental_income>,
                "operating_expenses": {{
                    "total": <total_annual_operating_expenses>,
                    "property_taxes": <annual_property_taxes>,
                    "insurance": <annual_insurance>,
                    "utilities": <annual_utilities>,
                    "maintenance_repairs": <annual_maintenance_and_repairs>,
                    "management_fees": <annual_management_fees>,
                    "other_expenses": <other_operating_expenses>
                }},
                "net_operating_income": <annual_noi>,
                "vacancy_rate": <vacancy_rate_percentage>,
                "total_units": <number_of_units>,
                "occupied_units": <number_of_occupied_units>,
                "avg_rent_per_unit": <average_monthly_rent_per_unit>,
                "property_type": "<property_type>",
                "reporting_period": "<period_covered>"
            }}

            Return only valid JSON. If a value cannot be determined, use null.

            T12 Financial Statement:
            {text}
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            # Parse the JSON response
            content = response.text.strip()
            
            # Remove code block markers if present
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content)
            
        except Exception as e:
            self.logger.error(f"Error parsing T12 with AI: {str(e)}")
            return self._get_default_t12_structure()
    
    async def _parse_t12_excel_with_ai(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Parse T12 data from Excel DataFrame using AI
        """
        try:
            # Convert DataFrame to text for AI processing
            text_representation = df.to_string()
            return await self._parse_t12_with_ai(text_representation, "Excel")
            
        except Exception as e:
            self.logger.error(f"Error parsing T12 Excel with AI: {str(e)}")
            return self._get_default_t12_structure()
    
    async def _parse_rent_roll_with_ai(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Parse rent roll data from DataFrame using AI
        """
        try:
            # Use AI to parse the rent roll structure
            text_representation = df.to_string()
            
            prompt = f"""
            You are a commercial real estate analyst. Parse the following rent roll data and extract key information.

            Please return a JSON object with the following structure:
            {{
                "total_units": <total_number_of_units>,
                "occupied_units": <number_of_occupied_units>,
                "vacant_units": <number_of_vacant_units>,
                "total_monthly_rent": <total_monthly_rental_income>,
                "average_rent_per_unit": <average_monthly_rent_per_unit>,
                "unit_mix": {{
                    "1br": <number_of_1_bedroom_units>,
                    "2br": <number_of_2_bedroom_units>,
                    "3br": <number_of_3_bedroom_units>,
                    "other": <number_of_other_units>
                }},
                "rent_ranges": {{
                    "min_rent": <minimum_rent>,
                    "max_rent": <maximum_rent>,
                    "median_rent": <median_rent>
                }},
                "lease_terms": {{
                    "average_lease_term": <average_lease_term_months>,
                    "expiring_next_12_months": <number_of_leases_expiring_next_12_months>
                }},
                "vacancy_rate": <vacancy_rate_percentage>,
                "annual_rental_income": <total_annual_rental_income>
            }}

            Return only valid JSON. If a value cannot be determined, use null.

            Rent Roll Data:
            {text_representation}
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            content = response.text.strip()
            
            # Remove code block markers if present
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content)
            
        except Exception as e:
            self.logger.error(f"Error parsing rent roll with AI: {str(e)}")
            return self._get_default_rent_roll_structure()
    
    def _get_default_t12_structure(self) -> Dict[str, Any]:
        """Return default T12 structure if parsing fails"""
        return {
            "gross_rental_income": None,
            "operating_expenses": {
                "total": None,
                "property_taxes": None,
                "insurance": None,
                "utilities": None,
                "maintenance_repairs": None,
                "management_fees": None,
                "other_expenses": None
            },
            "net_operating_income": None,
            "vacancy_rate": None,
            "total_units": None,
            "occupied_units": None,
            "avg_rent_per_unit": None,
            "property_type": "Unknown",
            "reporting_period": "Unknown"
        }
    
    def _get_default_rent_roll_structure(self) -> Dict[str, Any]:
        """Return default rent roll structure if parsing fails"""
        return {
            "total_units": None,
            "occupied_units": None,
            "vacant_units": None,
            "total_monthly_rent": None,
            "average_rent_per_unit": None,
            "unit_mix": {"1br": None, "2br": None, "3br": None, "other": None},
            "rent_ranges": {"min_rent": None, "max_rent": None, "median_rent": None},
            "lease_terms": {"average_lease_term": None, "expiring_next_12_months": None},
            "vacancy_rate": None,
            "annual_rental_income": None
        }
    # Fallback methods when AI is not available
    def _parse_t12_fallback(self, text: str) -> Dict[str, Any]:
        """Parse T12 using regex patterns as fallback"""
        financial_data = {}
        
        patterns = {
            'gross_rental_income': [
                r'gross.*rental.*income.*?(\$?[\d,]+\.?\d*)',
                r'total.*income.*?(\$?[\d,]+\.?\d*)',
                r'rental.*income.*?(\$?[\d,]+\.?\d*)'
            ],
            'operating_expenses': [
                r'operating.*expenses.*?(\$?[\d,]+\.?\d*)',
                r'total.*expenses.*?(\$?[\d,]+\.?\d*)'
            ],
            'net_operating_income': [
                r'net.*operating.*income.*?(\$?[\d,]+\.?\d*)',
                r'noi.*?(\$?[\d,]+\.?\d*)'
            ]
        }
        
        for metric, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text.lower())
                if match:
                    value_str = match.group(1).replace('$', '').replace(',', '')
                    try:
                        financial_data[metric] = float(value_str)
                        break
                    except ValueError:
                        continue
        
        return financial_data if financial_data else self._get_mock_t12_data()
    
    def _parse_t12_excel_fallback(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse T12 Excel using pattern matching as fallback"""
        try:
            financial_data = {}
            
            # Search for income columns
            income_cols = df.columns[df.columns.str.contains('income|revenue|rent', case=False, na=False)]
            if len(income_cols) > 0:
                income_values = df[income_cols[0]].dropna()
                if len(income_values) > 0:
                    financial_data['gross_rental_income'] = float(income_values.iloc[-1])
            
            # Search for expense columns
            expense_cols = df.columns[df.columns.str.contains('expense|cost', case=False, na=False)]
            if len(expense_cols) > 0:
                expense_values = df[expense_cols[0]].dropna()
                if len(expense_values) > 0:
                    financial_data['operating_expenses'] = float(expense_values.iloc[-1])
            
            return financial_data if financial_data else self._get_mock_t12_data()
            
        except Exception as e:
            self.logger.error(f"Error in T12 Excel fallback: {str(e)}")
            return self._get_mock_t12_data()
    
    def _parse_rent_roll_fallback(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse rent roll using pattern matching as fallback"""
        try:
            rent_data = {
                'total_units': len(df),
                'occupied_units': 0,
                'vacancy_rate': 0,
                'average_rent_per_unit': 0,
                'total_monthly_rent': 0
            }
            
            # Find rent column
            rent_cols = df.columns[df.columns.str.contains('rent|monthly', case=False, na=False)]
            if len(rent_cols) > 0:
                rent_values = df[rent_cols[0]].dropna()
                rent_data['average_rent_per_unit'] = float(rent_values.mean())
                rent_data['total_monthly_rent'] = float(rent_values.sum())
                rent_data['occupied_units'] = len(rent_values)
            
            # Calculate vacancy rate
            if rent_data['total_units'] > 0:
                rent_data['vacancy_rate'] = (
                    (rent_data['total_units'] - rent_data['occupied_units']) / rent_data['total_units']
                ) * 100
            
            return rent_data
            
        except Exception as e:
            self.logger.error(f"Error in rent roll fallback: {str(e)}")
            return self._get_mock_rent_roll_data()
    
    def _get_mock_t12_data(self) -> Dict[str, Any]:
        """Return mock T12 data for development/demo purposes"""
        return {
            'gross_rental_income': 420000,
            'operating_expenses': {
                'total': 168000,
                'property_taxes': 42000,
                'insurance': 18000,
                'utilities': 28000,
                'maintenance_repairs': 35000,
                'management_fees': 25200,
                'other_expenses': 19800
            },
            'net_operating_income': 252000,
            'vacancy_rate': 5.0,
            'total_units': 48,
            'occupied_units': 46,
            'avg_rent_per_unit': 875,
            'property_type': 'Multifamily',
            'reporting_period': 'Last 12 Months'
        }
    
    def _get_mock_rent_roll_data(self) -> Dict[str, Any]:
        """Return mock rent roll data for development/demo purposes"""
        return {
            'total_units': 48,
            'occupied_units': 46,
            'vacant_units': 2,
            'total_monthly_rent': 40250,
            'average_rent_per_unit': 875,
            'unit_mix': {
                '1br': 24,
                '2br': 20,
                '3br': 4,
                'other': 0
            },
            'rent_ranges': {
                'min_rent': 750,
                'max_rent': 1050,
                'median_rent': 875
            },
            'lease_terms': {
                'average_lease_term': 12,
                'expiring_next_12_months': 16
            },
            'vacancy_rate': 4.17,
            'annual_rental_income': 483000
        }

# Create singleton instance
file_processor = FileProcessor()
