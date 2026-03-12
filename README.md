# FastAPI Starter Scaffold

A modern FastAPI project scaffold with built-in environment variable management, logging system, and middleware configuration for rapid server development.

## 📋 Features

- **FastAPI Framework** - Modern async web framework with automatic OpenAPI documentation generation
- **Environment Variable Management** - Centralized configuration via `.env` files
- **Logging System** - Support for console output and JSON-formatted file logging
- **CORS Middleware** - Out-of-the-box cross-origin resource sharing configuration
- **Global Exception Handling** - Unified error response format
- **Hot Reload Support** - Automatic code reloading in debug mode
- **Quick Start** - Built-in health check endpoints and example routes

## 🚀 Getting Started

### Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Install Dependencies

Using uv:
```bash
uv sync
```

Using pip:
```bash
pip install -r requirements.txt
```

### Run the Server

```bash
python main.py
```

The service will start at `http://localhost:8000`

### View API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 Project Structure

```
fastapi-starter-uv/
├── main.py                    # Application entry point
├── pyproject.toml             # Project dependencies (uv)
├── .env                       # Environment variables
├── .env.example               # Environment variables example
├── README.md                  # Project documentation
└── src/
    ├── app.py                 # FastAPI app and route definitions
    ├── config.py              # App configuration and middleware setup
    ├── common/
    │   ├── env.py             # Environment configuration manager
    │   └── log.py             # Logging system
    └── router/
        └── models/
            └── response_dto.py # Unified response data model
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Debug mode (true/false)
DEBUG=true

# Log level (DEBUG|INFO|WARNING|ERROR|CRITICAL)
LOG_LEVEL=DEBUG

# Log output directory (if empty, logs only to console)
LOG_DIR=./logs
```

**Configuration Details:**

- `DEBUG`: When enabled, the API supports hot reload and error responses include detailed information
- `LOG_LEVEL`: Controls the logging output level
- `LOG_DIR`: Specifies the log file output directory; logs are saved in JSON format

### Environment Variable Management

The project uses Pydantic's `BaseSettings` for centralized configuration management:

```python
from src.common.env import config

# Access configuration
print(config.debug)      # True/False
print(config.log_level)  # DEBUG/INFO/...
print(config.log_dir)    # ./logs
```

### Logging System

The logging system supports two output methods:

1. **Console Output** - Real-time log viewing
2. **File Output** - JSON format for easy log analysis

Using the logger:

```python
from src.common.log import get_logger

log = get_logger(__name__)

log.debug("Debug message")
log.info("Info message")
log.warning("Warning message")
log.error("Error message")
log.critical("Critical error")
```

Example log output (JSON format):

```json
{
  "timestamp": "2024-03-12T10:30:45.123456",
  "level": "INFO",
  "module": "src.app",
  "message": "Application started",
  "pathname": "/Users/hans/repo/fastapi-starter-uv/src/app.py",
  "lineno": 25,
  "funcName": "root"
}
```

## 🔌 API Examples

### Health Check

**Request:**
```bash
GET /health HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "err_code": 0,
  "err_msg": "ok",
  "data": {
    "status": "healthy",
    "version": "1.0.0"
  }
}
```

### Root Route

**Request:**
```bash
GET / HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "err_code": 0,
  "err_msg": "Perfect! miremo service is running",
  "data": null
}
```

## 📝 Development Guide

### Creating New Routes

1. Create a new route file in `src/router/`, for example `users.py`:

```python
from fastapi import APIRouter
from src.router.models.response_dto import ResponseDto

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=ResponseDto[dict])
async def get_user(user_id: int) -> ResponseDto[dict]:
    """Get user information"""
    return ResponseDto(
        err_code=0,
        err_msg="ok",
        data={"id": user_id, "name": "John Doe"}
    )
```

2. Register the route in `src/config.py`:

```python
from src.router.users import router as users_router

def create_app() -> FastAPI:
    app = FastAPI(...)
    
    # Register routes
    app.include_router(users_router)
    
    return app
```

### Adding Configuration Items

Add fields to the `EnvConfig` class in `src/common/env.py`:

```python
class EnvConfig(BaseSettings):
    debug: bool = Field(default=True)
    log_level: str = Field(default="DEBUG")
    log_dir: str | None = Field(default="")
    
    # New configuration item
    database_url: str = Field(
        default="sqlite:///./test.db",
        description="Database connection URL"
    )
    
    model_config = SettingsConfigDict(...)
```

### Response Data Model

All API responses use the unified `ResponseDto` format:

```python
class ResponseDto(BaseModel, Generic[T]):
    """Unified API response format"""
    err_code: int          # Error code (0 for success)
    err_msg: str           # Error or success message
    data: T | None = None  # Actual data
```

## 🧪 Testing

Run tests:

```bash
pytest
```

Run specific test files:

```bash
pytest tests/test_app.py -v
```

## 🌐 Middleware Configuration

The project includes the following middleware:

- **CORS** - Cross-origin resource sharing, allows requests from all origins
- **Exception Handling** - Global HTTP exception and validation error handling
- **Logging** - Request/response logging

**Production Environment Recommendations:**
- Set specific `allow_origins` instead of `["*"]`
- Enable HTTPS
- Configure appropriate log levels
- Disable debug mode

## 📦 Dependency Management

Use uv to manage dependencies, which is faster and more reliable than pip:

```bash
# Add dependency
uv pip install <package-name>

# Remove dependency
uv pip uninstall <package-name>

# Update dependency
uv pip install --upgrade <package-name>

# Sync dependencies
uv sync
```

## 🔧 Troubleshooting

### 1. Port Already in Use

If port 8000 is already in use, modify the port in `main.py`:

```python
if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8001,  # Change to another port
        ...
    )
```

### 2. Environment Variables Not Loading

- Ensure the `.env` file is in the project root directory
- Check that the `.env` file encoding is UTF-8
- Restart the service for changes to take effect

### 3. Log Files Not Generated

- Ensure the `LOG_DIR` directory exists and has write permissions
- Check that `LOG_LEVEL` is set correctly

## 📄 License

MIT License

## 👥 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Quick Links:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Pydantic Documentation](https://docs.pydantic.dev/)
- [uv Project](https://github.com/astral-sh/uv)
