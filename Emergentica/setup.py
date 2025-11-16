"""
Setup script for Emergentica project.
Creates virtual environment and installs dependencies.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, description: str):
    """Run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    
    print(f"✅ {description} completed successfully")
    return True


def main():
    """Main setup function."""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        Emergentica - Setup Script                       ║
    ║        The Great Agent Hack 2025                        ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Check Python version
    python_version = sys.version_info
    print(f"\n✓ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 11):
        print("❌ Python 3.11+ is required!")
        sys.exit(1)
    
    # Create virtual environment
    venv_path = project_root / "venv"
    
    if not venv_path.exists():
        if not run_command(
            f"{sys.executable} -m venv venv",
            "Creating virtual environment"
        ):
            sys.exit(1)
    else:
        print(f"\n✓ Virtual environment already exists at {venv_path}")
    
    # Determine pip path based on OS
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Upgrade pip (using python -m pip to avoid Windows issues)
    if not run_command(
        f'"{python_path}" -m pip install --upgrade pip',
        "Upgrading pip"
    ):
        print("\n⚠️  Pip upgrade failed, but continuing with installation...")
        # Don't exit - pip upgrade failure is not critical
    
    # Install dependencies
    if not run_command(
        f'"{pip_path}" install -r requirements.txt',
        "Installing dependencies"
    ):
        sys.exit(1)
    
    # Check .env file
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists():
        print(f"\n⚠️  .env file not found!")
        if env_example.exists():
            print(f"📋 Please copy .env.example to .env and fill in your API keys:")
            print(f"   cp .env.example .env")
        else:
            print(f"📋 Please create a .env file with your API keys")
    else:
        print(f"\n✓ .env file exists")
    
    # Final instructions
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        Setup Complete! 🎉                                ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    
    Next steps:
    
    1. Activate the virtual environment:
       Windows: .\\venv\\Scripts\\activate
       Linux/Mac: source venv/bin/activate
    
    2. Verify configuration:
       python config.py
    
    3. Prepare the dataset (Phase 0.2):
       python scripts/preprocess_data.py
    
    4. Start building agents! (Phase 1)
       See README.md for detailed instructions
    
    Happy hacking! 🚀
    """)


if __name__ == "__main__":
    main()
