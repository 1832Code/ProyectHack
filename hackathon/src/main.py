"""
Main entry point for Google Cloud Run
Starts the FastAPI REST API server
Author: Mauricio J. @synaw_w
"""

import os
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (Cloud Run sets this)
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Run the API server
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        log_level="info"
    )

