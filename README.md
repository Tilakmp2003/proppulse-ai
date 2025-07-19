# PropPulse AI - Commercial Real Estate Underwriting Platform

AI-powered commercial real estate underwriting platform that automates property deal analysis, reducing analysis time from hours to under 30 seconds.

## Features

- 🔐 User Authentication & Authorization
- 📄 Document Upload & Parsing (T12, Rent Roll)
- 🏢 Automated Property Data Integration (CoStar, Zillow, NeighborhoodScout)
- 📊 Multifamily Underwriting Engine
- ⚙️ Customizable Investment Criteria ("Buy Box")
- 📈 Results Dashboard with Pass/Fail Analysis
- 📋 PDF & Excel Export Functionality

## Tech Stack

### Frontend

- Next.js 14 with App Router
- TypeScript
- Tailwind CSS
- React Query (TanStack Query)
- Supabase Auth

### Backend

- Python FastAPI
- PostgreSQL (Supabase)
- File Processing (pdfplumber, pandas)
- External API Integrations
- OpenAI GPT-4 API

### Deployment

- Frontend: Vercel
- Backend: Railway
- Database: Supabase

## Project Structure

```
proppulse-ai/
├── frontend/           # Next.js frontend
├── backend/           # FastAPI backend
├── docs/             # Documentation
└── README.md
```

## Quick Start

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Environment Variables

See `.env.example` files in frontend and backend directories.

## License

MIT License
