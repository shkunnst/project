#!/bin/bash
set -e

# Run database initialization and seeding
python -c "import asyncio; from gateway import main; asyncio.run(main())"

# Start the FastAPI application
exec uvicorn gateway:app --host 0.0.0.0 --port 8000 --reload