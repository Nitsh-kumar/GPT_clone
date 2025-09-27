# ChatGPT Clone

A full-stack ChatGPT clone built with Streamlit frontend and FastAPI backend, featuring user authentication and MySQL database integration.

## Features

- 🔐 User Authentication (Login/Register)
- 💬 Real-time Chat Interface
- 🗄️ MySQL Database Integration
- 🎨 Modern UI with Responsive Design
- 🔒 Session Management
- 📱 Mobile-Friendly Interface

## Tech Stack

### Frontend
- **Streamlit** - Web application framework
- **streamlit-authenticator** - Authentication management
- **Custom CSS** - Modern styling and responsive design

### Backend
- **FastAPI** - High-performance web framework
- **SQLAlchemy** - ORM for database operations
- **MySQL** - Database
- **Pydantic** - Data validation
- **bcrypt** - Password hashing

## Project Structure

```
├── frontend/
│   └── main.py              # Streamlit application
├── Backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── core/
│   │   │   ├── config.py    # Configuration settings
│   │   │   └── auth.py      # Authentication utilities
│   │   ├── models/
│   │   │   ├── db.py        # Database connection
│   │   │   ├── orm_models.py # SQLAlchemy models
│   │   │   └── schemas.py   # Pydantic schemas
│   │   └── api/v1/endpoints/
│   │       ├── auth.py      # Authentication endpoints
│   │       └── chat.py      # Chat endpoints
│   ├── .env                 # Environment variables
│   └── requirements.txt     # Python dependencies
├── start_backend.sh         # Backend startup script
├── start_frontend.sh        # Frontend startup script
└── Requirement.txt          # Additional requirements
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL Server
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/[your-username]/Chatgpt_clone.git
   cd Chatgpt_clone
   ```

2. **Set up the Backend**
   ```bash
   cd Backend
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the Backend directory:
   ```env
   DATABASE_URL=mysql+pymysql://username:password@localhost/chatgpt_clone
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Set up MySQL Database**
   ```sql
   CREATE DATABASE chatgpt_clone;
   ```

5. **Install Frontend Dependencies**
   ```bash
   pip install -r Requirement.txt
   ```

### Running the Application

1. **Start the Backend Server**
   ```bash
   ./start_backend.sh
   ```
   Or manually:
   ```bash
   cd Backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Frontend Application**
   ```bash
   ./start_frontend.sh
   ```
   Or manually:
   ```bash
   streamlit run frontend/main.py
   ```

3. **Access the Application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Features Overview

### Authentication System
- User registration with email validation
- Secure login with password hashing
- Session management with JWT tokens
- Automatic user initialization

### Chat Interface
- Modern, responsive design
- Real-time message display
- User-friendly input interface
- Message history storage

### Database Integration
- User management
- Conversation tracking
- Message storage
- Automatic table creation

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Chat
- `POST /chat/message` - Send message
- `GET /chat/conversations` - Get user conversations
- `GET /chat/messages/{conversation_id}` - Get conversation messages

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for inspiration
- Streamlit team for the amazing framework
- FastAPI team for the high-performance backend framework