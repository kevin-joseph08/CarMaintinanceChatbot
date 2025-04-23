# Car Maintenance Chatbot

An intelligent chatbot assistant that helps with car maintenance, repairs, and diagnostics.

## Features

- Car Diagnosis Assistant
- Maintenance Scheduler
- Parts and Tools Guide
- Repair Instructions
- Cost Estimator
- Vehicle Information Management

## Tech Stack

- Backend: Python FastAPI
- Frontend: React.js
- Databases: PostgreSQL, MongoDB
- AI: LangChain, OpenAI GPT
- Cache: Redis

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and configuration

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

```
car-maintenance-chatbot/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── services/
│   └── main.py
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── tests/
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 