# CVP Lite - Complete Career Vision Program Implementation

##  Overview

CVP Lite is a comprehensive Career Vision Program that provides AI-powered career guidance through a structured 10-step assessment process. This implementation includes all the components mentioned in the documentation:

- **10-Step Assessment Program** with progressive scoring
- **AI Mentor Intelligence** system for personalized guidance
- **Progressive Scoring Logic** for career matching
- **Comprehensive Career Assessment Engine**
- **Report Generation** capabilities
- **Multi-language Support**
- **Tier-based System** (Basic, Premium, Enterprise)

## Features

### Core Program Features
- **Step 0**: Candidate Profile Setup
- **Step 1**: Interest & Strengths Discovery
- **Step 2**: Values & Preferences Discovery
- **Step 3**: Learning Style & Personality Assessment
- **Step 4**: Passion & Career Fit Analysis
- **Step 5**: Cognitive Thinking Scenario Assessment
- **Step 6**: Emotional & Ethical Intelligence
- **Step 7**: Career Summary & Direction Bridge
- **Step 8**: Education Pathways & College Strategy
- **Step 9**: Personal Action Plan Framework
- **Step 10**: Program Completion & Report Generation

### Technical Features
- **FastAPI Backend** with comprehensive API documentation
- **MongoDB Integration** for data persistence
- **OpenAI GPT-4 Integration** for AI mentor capabilities
- **Pinecone Vector Database** for knowledge management
- **API Key Authentication** for security
- **Comprehensive Error Handling** and logging
- **Async/await Support** throughout the system
- **Progressive Scoring Engine** for career matching
- **Multi-language Support** (EN, ES, FR, DE, ZH, JA)

## Quick Start

### Prerequisites
- Python 3.8+
- MongoDB 
- OpenAI API key
- Pinecone API key 

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd cvp_lite
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Create .env file
export OPENAI_API_KEY="your_openai_api_key_here"
export PINECONE_API_KEY="your_pinecone_api_key_here"
export PINECONE_ENVIRONMENT="us-west1-gcp"
export MONGO_URI="your_mongodb_connection_string"
```

4. **Run the application**
```bash
uvicorn app_main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the API**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Documentation & Testing

### Swagger UI - Interactive API Documentation
The primary way to explore and test the CVP Lite API is through the **Swagger UI**:

- **URL**: `http://localhost:8000/docs`
- **Features**: 
  - Interactive API testing directly from the browser
  - Complete request/response schemas
  - All available parameters and data models
  - Real-time API testing interface

### Alternative Documentation
- **ReDoc**: `http://localhost:8000/redoc` - Cleaner, more readable format
- **Root Endpoint**: `http://localhost:8000/` - Basic API information
- **Health Check**: `http://localhost:8000/health` - System status

### API Key Authentication
When accessing the Swagger UI:
1. Click the **"Authorize"** button (🔒) in the top-right corner
2. Enter your API key in the `X-API-KEY` field
3. Click **"Authorize"**
4. Now you can test all protected endpoints

### What You'll Find in the Documentation
The Swagger UI provides access to all **15+ API endpoints** including:

#### **Session Management:**
- `POST /api/start_session` - Start new CVP Lite session
- `POST /api/step` - Process program step
- `POST /api/session` - Get complete session info
- `GET /api/sessions` - List all sessions

#### **Progress & Reporting:**
- `POST /api/progress` - Get session progress
- `POST /api/report` - Generate comprehensive report
- `GET /api/stats` - Database statistics

#### **Program Information:**
- `GET /api/steps` - Get all program steps
- `GET /api/career-domains` - Get career domains
- `GET /api/learning-pathways` - Get learning pathways

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4` |
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `PINECONE_ENVIRONMENT` | Pinecone environment | `us-west1-gcp` |
| `MONGO_URI` | MongoDB connection string | Required |
| `MONGO_DB_NAME` | MongoDB database name | `cvp_lite_db` |

### API Configuration

The system supports three tiers:
- **Basic**: Core assessment features
- **Premium**: Advanced AI insights and career matching
- **Enterprise**: Full feature set with custom integrations

## API Endpoints

### Core Endpoints

#### Session Management
- `POST /api/start_session` - Start new CVP Lite session
- `POST /api/step` - Process program step
- `POST /api/session` - Get complete session info
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{session_id}` - Get session by ID
- `DELETE /api/sessions/{session_id}` - Delete session

#### Progress & Reports
- `POST /api/progress` - Get session progress
- `POST /api/report` - Generate comprehensive report
- `GET /api/stats` - Database statistics

#### Program Information
- `GET /api/steps` - Get all program steps
- `GET /api/career-domains` - Get career domains
- `GET /api/learning-pathways` - Get learning pathways

### Authentication

All API endpoints (except `/health` and `/`) require API key authentication via the `X-API-KEY` header.

## Architecture

### System Components

```
CVP Lite System
├── FastAPI Application (app_main.py)
├── Session Management (controllers/session_controller.py)
├── Assessment Engine (services/cvp_step_content.py)
├── Scoring System (services/scoring_engine.py)
├── AI Mentor (services/ai_mentor.py)
├── OpenAI Integration (services/openai_client.py)
├── Vector Database (services/pinecone_client.py)
├── Data Models (models/session_models.py)
├── Database Layer (db/mongo_client.py)
├── API Routes (routes/session_routes.py)
└── Security (security/api_key_auth.py)
```

### Data Flow

1. **Session Creation**: Student starts CVP Lite program
2. **Step Processing**: Student completes assessments step by step
3. **AI Analysis**: OpenAI processes responses for insights
4. **Scoring**: Progressive scoring engine calculates career matches
5. **Recommendations**: AI generates personalized career guidance
6. **Report Generation**: Comprehensive report with action items

## AI Features

### OpenAI Integration
- **GPT-4 Model** for intelligent responses
- **Assessment Analysis** for personalized feedback
- **Career Recommendations** based on responses
- **Conversational AI** for mentor-like guidance

### Progressive Scoring
- **Multi-factor Assessment** scoring
- **Career Domain Matching** algorithms
- **Confidence Level** calculations
- **Personalized Insights** generation

##  Database Schema

### Collections

#### Sessions
```json
{
  "session_id": "uuid",
  "student_id": "string",
  "language": "en",
  "tier": "basic",
  "current_step": "profile_setup",
  "step_number": 1,
  "created_at": "datetime",
  "last_updated": "datetime",
  "status": "active"
}
```

#### Assessments
```json
{
  "session_id": "uuid",
  "step_type": "profile_setup",
  "step_number": 1,
  "questions": [...],
  "responses": [...],
  "total_score": 85.5,
  "completion_percentage": 100,
  "is_completed": true
}
```

#### Career Domains
```json
{
  "domain_id": "tech_software",
  "title": "Software Development",
  "description": "Creating applications and software solutions",
  "required_skills": ["Programming", "Problem Solving"],
  "growth_potential": "High",
  "salary_range": "$60,000 - $150,000+"
}
```

##  Security

### API Key Authentication
- All endpoints require valid API key
- Configured via `X-API-KEY` header
- Secure session management

### Data Protection
- MongoDB connection security
- Input validation and sanitization
- Error handling without data exposure

##  Testing

### Manual Testing
1. Start a session using `/api/start_session`
2. Process steps using `/api/step`
3. Check progress with `/api/progress`
4. Generate report with `/api/report`

### API Testing
- Use Swagger UI for interactive testing
- Import OpenAPI spec to Postman/Insomnia
- Test with sample data provided in models

### System Testing
Run the comprehensive test suite to verify all components:
```bash
python test_system.py
```

##  Monitoring & Logging

### Logging
- Comprehensive logging throughout the system
- Log file: `cvp_lite.log`
- Structured logging with timestamps

### Health Checks
- `/health` endpoint for service monitoring
- Database connection status
- External service availability

##  Deployment

### Production Considerations
1. **Environment Variables**: Secure configuration management
2. **Database**: Production MongoDB cluster
3. **API Keys**: Secure storage and rotation
4. **Monitoring**: Application performance monitoring
5. **Scaling**: Load balancing and horizontal scaling

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app_main:app", "--host", "0.0.0.0", "--port", "8000"]
```

##  Support

### Common Issues
1. **MongoDB Connection**: Check connection string and network access
2. **OpenAI API**: Verify API key and quota limits
3. **Pinecone**: Ensure proper environment configuration


---

**CVP Lite** - Empowering students to discover their career path through intelligent assessment and AI-powered guidance.
