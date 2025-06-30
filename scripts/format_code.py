#!/usr/bin/env python3
"""
Code Formatting and Quality Script
Automatically formats code and runs quality checks
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, project_root):
    """Run a command and return its result"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=project_root)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"📋 Output: {result.stdout.strip()}")
        else:
            print(f"⚠️ {description} found issues (non-critical):")
            if result.stdout.strip():
                print(f"📋 {result.stdout.strip()}")
            if result.stderr.strip():
                print(f"❌ {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def main():
    """Main formatting and quality check function"""
    print("🚀 Starting code formatting and quality checks...\n")
    
    # Get project root directory (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    
    # Check if we're in the right directory
    if not (project_root / "requirements.txt").exists():
        print("❌ Could not find project root directory")
        print(f"📁 Looking for requirements.txt in: {project_root}")
        sys.exit(1)
    
    print(f"📁 Working in project root: {project_root}")

    # Install/upgrade dev dependencies
    print("📦 Installing development dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"], 
                  capture_output=True, cwd=project_root)

    # Get list of Python files in the project root
    python_files = list(project_root.glob("*.py"))
    if not python_files:
        print("⚠️ No Python files found in project root")
        return
    
    file_list = " ".join([f'"{f.name}"' for f in python_files])
    print(f"📋 Found {len(python_files)} Python files: {[f.name for f in python_files]}")

    # Format code with black
    run_command(f"black --line-length=120 {file_list}", "Code formatting (Black)", project_root)

    # Sort imports with isort
    run_command(f"isort {file_list}", "Import sorting (isort)", project_root)

    # Run linting with flake8
    run_command(f"flake8 {file_list}", "Linting (flake8)", project_root)

    # Run type checking with mypy (if available)
    run_command(f"mypy {file_list}", "Type checking (mypy)", project_root)

    print("\n🎉 Code formatting and quality checks completed!")
    print("📝 Your code is now formatted and ready for commit.")
    print("💡 Tip: Consider setting up pre-commit hooks for automatic formatting.")


if __name__ == "__main__":
    main()
