# CVP Lite Backend

## Features
- FastAPI backend with Swagger UI and ReDoc documentation
- API Key authentication to protect endpoints
- Async MongoDB integration for storing session data
- Session start and step APIs with data persistence

## Setup and Run

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Replace API key**

Update `security/api_key_auth.py` with your actual API key value.

3. **Run the app**

```bash
uvicorn app_main:app --reload
```

4. **Test the API**

- Open Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Click **Authorize** button on top-right and enter your API key with header name `X-API-KEY`.
- Use `/api/start_session` to create a session.
- Use `/api/step` to process steps by passing returned `session_id`.

## MongoDB

- The app connects to MongoDB using the provided URI.
- Session data is stored in the `cvp_lite_db` database, `sessions` collection.

## OpenAI and Pinecone Integration

### Environment Variables

Set your OpenAI and Pinecone API keys as environment variables before running the app:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export PINECONE_API_KEY="your_pinecone_api_key_here"
```

(On Windows PowerShell, use `setx` or `$Env:OPENAI_API_KEY = "your_openai_api_key_here"`)

### Usage

- OpenAI client example is in `services/openai_client.py` as `generate_completion` async function.  
- Pinecone client initialization and index helpers are in `services/pinecone_client.py`.

You can import and use these services in your controllers or wherever needed.