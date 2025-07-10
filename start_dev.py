#!/usr/bin/env python3
"""
Development Startup Script
AquaTrak - AI-GIS Water Risk Monitoring Platform

This script starts both the backend API server and frontend development server
for local development.
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✅ Python dependencies OK")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} OK")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 16+")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()} OK")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found. Please install npm")
        return False
    
    return True

def check_database():
    """Check database connection and initialize if needed"""
    print("🗄️ Checking database...")
    
    try:
        # Add src to Python path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from config.database import check_db_connection, init_db
        from config.settings import get_settings
        
        settings = get_settings()
        
        if check_db_connection():
            print("✅ Database connection OK")
            
            # Check if database has data
            from sqlalchemy.orm import Session
            from config.database import get_db
            from models.system import User
            
            db = next(get_db())
            user_count = db.query(User).count()
            db.close()
            
            if user_count == 0:
                print("📊 Database is empty, initializing sample data...")
                subprocess.run([sys.executable, 'scripts/init_sample_data.py'], check=True)
                print("✅ Sample data initialized")
            else:
                print(f"✅ Database has {user_count} users")
        else:
            print("❌ Database connection failed")
            print("Please ensure PostgreSQL is running and configured correctly")
            return False
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False
    
    return True

def start_backend():
    """Start the backend API server"""
    print("🚀 Starting backend API server...")
    
    try:
        # Change to src directory
        os.chdir('src')
        
        # Start the backend server
        process = subprocess.Popen([
            sys.executable, 'main.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Backend server started on http://localhost:8000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Backend server failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend development server"""
    print("🌐 Starting frontend development server...")
    
    try:
        # Change to frontend directory
        os.chdir('src/frontend')
        
        # Install dependencies if needed
        if not os.path.exists('node_modules'):
            print("📦 Installing frontend dependencies...")
            subprocess.run(['npm', 'install'], check=True)
        
        # Start the frontend server
        process = subprocess.Popen([
            'npm', 'start'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for server to start
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Frontend server started on http://localhost:3000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Frontend server failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def monitor_processes(backend_process, frontend_process):
    """Monitor running processes and handle shutdown"""
    try:
        while True:
            # Check if processes are still running
            if backend_process and backend_process.poll() is not None:
                print("❌ Backend server stopped unexpectedly")
                break
                
            if frontend_process and frontend_process.poll() is not None:
                print("❌ Frontend server stopped unexpectedly")
                break
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
            print("✅ Backend server stopped")
            
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
            print("✅ Frontend server stopped")

def main():
    """Main function"""
    print("🚀 AquaTrak Development Environment")
    print("=" * 50)
    
    # Store original directory
    original_dir = os.getcwd()
    
    try:
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Check database
        if not check_database():
            sys.exit(1)
        
        print("\n🎯 Starting development servers...")
        print("-" * 50)
        
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            sys.exit(1)
        
        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            backend_process.terminate()
            sys.exit(1)
        
        print("\n🎉 Development environment is ready!")
        print("=" * 50)
        print("📊 Backend API: http://localhost:8000")
        print("🌐 Frontend App: http://localhost:3000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\n👤 Sample Users:")
        print("   Admin: admin@aquatrak.com / admin123")
        print("   Manager: manager@aquatrak.com / manager123")
        print("   Analyst: analyst@aquatrak.com / analyst123")
        print("   Viewer: viewer@aquatrak.com / viewer123")
        print("\n💡 Press Ctrl+C to stop all servers")
        print("=" * 50)
        
        # Monitor processes
        monitor_processes(backend_process, frontend_process)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Return to original directory
        os.chdir(original_dir)
        print("\n👋 Development environment stopped")

if __name__ == "__main__":
    main() 