# ProductDNA — Intelligent Product Resolution & Semantic Enrichment

> Enterprise-Grade Product Knowledge Pipeline for Automated Catalog Standardization, Evidence Extraction, and 252-Column Unilog Schema Delivery.

---

## 🌟 Overview

**ProductDNA** is an autonomous AI-driven product intelligence platform that transforms raw, unstructured, multi-source product data (CSVs, technical PDFs, manufacturer datasheets, web pages) into verified, canonical product catalog records mapped directly to the enterprise 252-column Unilog delivery schema.

Built with a modular microservice-style FastAPI backend and a high-performance React + Tailwind glassmorphism frontend, ProductDNA combines deterministic SKU resolution with LLM-powered semantic interpretation.

---

## 🏗️ 8-Module Architecture Pipeline

ProductDNA strictly follows an 8-module pipeline architecture to guarantee data integrity, traceability, and confidence:

```text
       ┌─────────────────────────────────────────────────────────┐
       │     Module 1: Product Input / Standardization           │
       │     (Ingests CSV, PDF; yields StandardProductInput)     │
       └──────────────────────────┬──────────────────────────────┘
                                  │
       ┌──────────────────────────▼──────────────────────────────┐
       │     Module 2: Evidence Collection                        │
       │     (Collects datasheets, web URLs, manuals, notes)     │
       └──────────────────────────┬──────────────────────────────┘
                                  │
       ┌──────────────────────────▼──────────────────────────────┐
       │     Module 3: Evidence Extraction                        │
       │     (Parses text & PDFs to extract raw attributes)       │
       └──────────────────────────┬──────────────────────────────┘
                                  │
       ┌──────────────────────────▼──────────────────────────────┐
       │     Module 4: Product Resolution Engine                 │
       │     (Matches candidate SKUs against Org Registry)       │
       └──────────────────────────┬──────────────────────────────┘
                                  │
       ┌──────────────────────────▼──────────────────────────────┐
       │     Module 5: LLM / Semantic Interpretation             │
       │     (Gemini AI infers missing fields & 252-col schema)   │
       └──────────────────────────┬──────────────────────────────┘
                                  │
       ┌──────────────────────────▼──────────────────────────────┐
       │     Module 6: Validation Layer                           │
       │     (Calculates confidence & verifies claims)           │
       └──────────────────────────┬──────────────────────────────┘
                                  │
       ┌──────────────────────────▼──────────────────────────────┐
       │     Module 7: ProductDNA Builder                         │
       │     (Assembles canonical product knowledge graph)       │
       └──────────────────────────┬──────────────────────────────┘
                                  │
       ┌──────────────────────────▼──────────────────────────────┐
       │     Module 8: Delivery / Output Mapper                  │
       │     (Exports final 252-column CSV schema delivery)      │
       └─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Key Features

- 📄 **Multi-Source Ingestion (Module 1)**: Supports single/batch CSV uploads, PDF technical spec sheets, and manual entry.
- 📁 **Evidence Storage & Management (Module 2 & 3)**: Attach datasheets, web links, and unstructured text to products with full lineage tracking.
- 🎯 **Product Resolution Engine (Module 4)**: Deduplicates and resolves candidate products against organizational inventory registry.
- 🤖 **LLM Semantic Interpretation (Module 5)**: Uses Google Gemini AI via LangChain to infer missing attributes, standardize units, and generate field provenance metadata.
- 📊 **252-Column Unilog Schema Delivery (Module 8)**: Preview and download full 252-column delivery CSV records with one click.
- 🩺 **Health & Uptime Monitoring**: Embedded `/health`, `/ping`, and `/api/health` endpoints optimized for UptimeRobot monitoring.

---

## 💻 Tech Stack

### Frontend
- **Framework**: React 18 (Vite)
- **Styling**: TailwindCSS, Glassmorphism dark mode
- **Icons**: Lucide React
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **LLM Engine**: Google Gemini API (`gemini-2.5-flash`), LangChain
- **PDF & Data Parsing**: PyMuPDF, Pandas, BeautifulSoup4
- **Schema Validation**: Pydantic v2

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API Key

---

### 1. Backend Setup

```bash
# Navigate to Backend folder
cd Backend

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Gemini API Key
echo GEMINI_API_KEY=your_gemini_api_key_here > .env
echo LLM_MODEL=gemini-2.5-flash >> .env

# Run FastAPI server
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend server will be running at: `http://127.0.0.1:8000`  
Swagger API Docs available at: `http://127.0.0.1:8000/docs`

---

### 2. Frontend Setup

```bash
# Open a new terminal and navigate to Frontend folder
cd Frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

The frontend application will open at `http://localhost:5173`.

---

## 🌐 Production Deployment

- **Frontend**: Deployed on [Vercel](https://product-dna-topaz.vercel.app/)
- **Backend**: Deployed on [Render.com](https://render.com) (or tunneled via `ngrok`)
- **Uptime Monitoring**: Integrated with [UptimeRobot](https://uptimerobot.com) targeting `GET /health`

---

## 📑 License

Built for **UniHack Hackathon**. Distributed under the MIT License.
