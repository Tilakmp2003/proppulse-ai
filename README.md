# PropPulse AI 🏠

**AI-Powered Real Estate Investment Analysis Platform**

PropPulse AI is a comprehensive real estate investment analysis platform that leverages artificial intelligence to provide data-driven insights for property investment decisions. The platform offers automated document processing, market analysis, financial projections, and comparative property analysis.

## 🚀 Features

### Core Functionality
- **Document Upload & Processing**: Upload and analyze rent rolls, financial statements, and property documents
- **AI-Powered Analysis**: Advanced AI analysis using Google Gemini for property insights
- **Financial Projections**: Comprehensive financial modeling and ROI calculations
- **Market Comparison**: Compare properties across different markets and criteria
- **Interactive Dashboard**: Real-time analytics and performance tracking

### Key Capabilities
- **Multi-Format Support**: PDF, CSV, Excel file processing
- **Real Estate APIs**: Integration with multiple property data sources
- **Automated Reporting**: Generate detailed investment analysis reports
- **User Authentication**: Secure user management with Supabase
- **Responsive Design**: Modern, mobile-friendly interface

## 🛠 Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database (production)
- **SQLite**: Development database
- **Google Gemini AI**: Advanced AI analysis
- **Supabase**: Authentication and database hosting

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and state management
- **Supabase Auth**: Authentication integration

### DevOps & Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Railway**: Backend deployment platform
- **Vercel**: Frontend deployment platform

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Docker and Docker Compose
- Git

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Tilakmp2003/proppulse-ai.git
   cd proppulse-ai
   ```

2. **Set up environment variables**
   ```bash
   # Backend environment
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys

   # Frontend environment
   cp frontend/.env.example frontend/.env.local
   # Edit frontend/.env.local with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv backend_env
   source backend_env/bin/activate  # On Windows: backend_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the backend**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Run the frontend**
   ```bash
   npm run dev
   ```

## 🔧 Configuration

### Required Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=sqlite:///./proppulse_ai.db

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# API Keys
GEMINI_API_KEY=your_gemini_api_key
RAPIDAPI_KEY=your_rapidapi_key

# JWT
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=50000000
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📁 Project Structure

```
proppulse-ai/
├── backend/
│   ├── services/           # Business logic services
│   │   ├── property_analyzer.py
│   │   ├── file_processor.py
│   │   └── external_api.py
│   ├── models.py          # Database models
│   ├── database.py        # Database configuration
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration settings
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js app directory
│   │   ├── components/   # React components
│   │   └── lib/         # Utility functions
│   ├── public/          # Static assets
│   └── package.json     # Node.js dependencies
├── docker-compose.yml   # Docker orchestration
└── README.md           # Project documentation
```

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### File Upload & Analysis
- `POST /upload/documents` - Upload property documents
- `GET /analysis/results` - Get analysis results
- `GET /analysis/results/{id}` - Get specific analysis

### Property Data
- `POST /property/analyze` - Analyze property data
- `POST /property/compare` - Compare multiple properties
- `GET /property/market-data` - Get market data

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Key Features Explained

### Document Processing
- **Multi-format Support**: PDF, CSV, Excel files
- **OCR Capabilities**: Extract text from scanned documents
- **Data Validation**: Ensure data integrity and accuracy

### AI Analysis
- **Market Analysis**: Property market trends and insights
- **Financial Projections**: ROI, cash flow, and profitability analysis
- **Risk Assessment**: Investment risk evaluation
- **Comparable Analysis**: Similar property comparison

### Real Estate APIs
- **Property Data**: Access to comprehensive property databases
- **Market Trends**: Real-time market information
- **Neighborhood Analytics**: Area demographics and statistics

## 🚀 Deployment

### Production Deployment

#### Backend (Railway)
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

#### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Environment-Specific Configurations
- **Development**: SQLite database, local file storage
- **Production**: PostgreSQL database, cloud storage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Write comprehensive tests
- Update documentation for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Live Demo**: [Coming Soon]
- **API Documentation**: http://localhost:8000/docs (when running locally)
- **Issues**: https://github.com/Tilakmp2003/proppulse-ai/issues

## 👥 Team

- **Tilak MP** - Full Stack Developer & AI Engineer

## 📞 Support

For support and questions:
- Email: rxtilak3@gmail.com
- GitHub Issues: [Create an issue](https://github.com/Tilakmp2003/proppulse-ai/issues)

## 🔮 Roadmap

- [ ] Advanced ML models for property valuation
- [ ] Real-time market data integration
- [ ] Mobile application (React Native)
- [ ] Investment portfolio tracking
- [ ] Multi-language support
- [ ] Advanced reporting and analytics

---

**PropPulse AI** - Empowering Smart Real Estate Investment Decisions with AI
