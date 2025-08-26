import asyncio
import uvicorn
from app.main import app
from app.utils.seed_data import seed_all_data

async def main():
    print("Vehicle Management System - Backend Server")
    print("=========================================")
    
    # Optionally seed data on startup
    try:
        print("Seeding initial data...")
        await seed_all_data()
        print("Data seeding completed successfully!")
    except Exception as e:
        print(f"Data seeding failed (this is normal if data already exists): {e}")
    
    print("\nStarting FastAPI server...")
    print("API Documentation: http://localhost:8000/docs")
    print("API Base URL: http://localhost:8000/api/v1")
    print("Press CTRL+C to stop the server")
    
    # Run the server
    config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())