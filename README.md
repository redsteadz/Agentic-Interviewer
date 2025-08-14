# 🤖 Agentic Interviewer

A comprehensive AI-powered call interviewer system that conducts professional phone interviews using advanced voice AI technology. The system includes campaign management, scheduled calling, real-time transcription, website analysis, and comprehensive reporting.

## ✨ Features

### 🎯 Core Interview System
- **Professional AI Interviewer**: Conduct natural, human-like phone interviews
- **Campaign Management**: Organize interviews by campaigns for better tracking
- **Real-time Call Management**: Monitor active calls and view detailed transcripts
- **Scheduled Calling**: Plan interviews in advance with timezone support

### 📊 Advanced Analytics
- **Website Analysis**: Automatically analyze business websites to generate interview topics and keywords
- **Transcript Management**: Search, filter, and view all call transcripts
- **Call Reporting**: Comprehensive call status tracking and detailed reports
- **Knowledge Base Integration**: AI-powered and manual knowledge base management

### 🔧 Technical Features
- **Multi-provider Support**: Twilio for phone numbers, Vapi for AI voice, OpenAI for analysis
- **RESTful API**: Complete Django REST Framework backend
- **Modern UI**: React frontend with Tailwind CSS and shadcn/ui components
- **Real-time Updates**: Live call status and transcript updates

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or pnpm
- Twilio Account
- Vapi Account
- OpenAI API Key

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Agentic-Interviewer.git
cd Agentic-Interviewer
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Start development server
npm run dev
# or
pnpm dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## ⚙️ Configuration

### API Keys Setup

1. **Register/Login** to the application
2. **Navigate to Interview Dashboard** 
3. **Configure API Settings** in the Configuration tab:

#### Required API Keys:
- **Twilio Account SID**: Your Twilio account identifier
- **Twilio Auth Token**: Your Twilio authentication token  
- **Vapi API Key**: Your Vapi voice AI API key
- **OpenAI API Key**: For website analysis (configured in code)

### Phone Number Setup

1. **Get Twilio Phone Numbers**: Purchase or use existing Twilio numbers
2. **Register Numbers**: Link Twilio numbers with Vapi assistants
3. **Test Configuration**: Verify all connections work properly

## 📱 Usage Guide

### Creating an Interview Campaign

1. **Login** to your account
2. **Create Campaign**: Name and organize your interview project
3. **Configure Assistant**: Set up AI interviewer with custom knowledge base
4. **Add Phone Numbers**: Register Twilio numbers for the campaign

### Conducting Interviews

#### Immediate Calls
1. **Navigate to Call Management** tab
2. **Enter customer phone number**
3. **Select assistant and phone number**
4. **Click "Make Call"** to start immediately

#### Scheduled Calls
1. **Go to Scheduled Calls** tab
2. **Fill in call details**:
   - Customer phone number
   - Date and time
   - Timezone
   - Call name and notes
3. **Schedule the call** for automatic execution

### Website Analysis

1. **Navigate to Assistant Configuration**
2. **Enter website URL** in the Website Analysis section
3. **Click "Analyze Website"** to generate:
   - Business summary
   - Company details (name, industry, location)
   - Article topics for interview questions
   - Relevant keywords
4. **Review and add** topics/keywords to AI Knowledge Base

### Managing Transcripts

1. **Access Transcripts** tab
2. **Search and filter** by:
   - Customer number
   - Call status
   - Content keywords
   - Assistant name
3. **View detailed transcripts** with conversation flow
4. **Export or analyze** call data

## 🛠️ API Endpoints

### Authentication
- `POST /api/register/` - User registration
- `POST /api/token/` - Login and get JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Campaign Management
- `GET /api/campaign/` - List campaigns
- `POST /api/campaign/` - Create campaign

### Interview System
- `GET /api/config/` - Get API configuration
- `POST /api/config/` - Update API configuration
- `POST /api/create-assistant/` - Create interview assistant
- `GET /api/assistants/` - List assistants

### Call Management
- `POST /api/make-call/` - Make immediate call
- `POST /api/schedule-call/` - Schedule future call
- `GET /api/calls/` - List all calls
- `GET /api/call/<call_id>/` - Get call details

### Website Analysis
- `POST /api/analyze-website/` - Analyze website URL

## 🔧 Development

### Running Tests
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

### Environment Variables

Create `.env` file in backend directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
```

### Database

The system uses SQLite by default. For production, configure PostgreSQL or MySQL in `settings.py`.

## 📦 Deployment

### Backend Deployment
1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up static files serving
4. Use gunicorn or similar WSGI server

### Frontend Deployment
```bash
cd frontend
npm run build
# Serve the dist/ directory
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.8+ required)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Run migrations: `python manage.py migrate`

**Frontend won't start:**
- Check Node.js version (16+ required)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check for port conflicts (default: 5173)

**API calls failing:**
- Verify all API keys are configured correctly
- Check network connectivity
- Review Django logs for detailed errors

**Calls not connecting:**
- Confirm Twilio account has sufficient credits
- Verify phone numbers are properly formatted
- Check Vapi assistant configuration

### Support

For issues and questions:
1. Check the [Issues](https://github.com/your-username/Agentic-Interviewer/issues) page
2. Review the troubleshooting section above
3. Create a new issue with detailed information

---

**Built with ❤️ using Django, React, Twilio, Vapi, and OpenAI**