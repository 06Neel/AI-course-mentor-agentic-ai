# Setup script for AI Course Mentor virtual environment

Write-Host "=== Setting up Python Virtual Environment (.venv) ===" -ForegroundColor Cyan

# 1. Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python is not installed or not in your system PATH. Please install Python 3.8+ and try again."
    Exit 1
}

# 2. Create the virtual environment if it doesn't exist
if (-not (Test-Path -Path ".venv")) {
    Write-Host "Creating virtual environment in .venv..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment."
        Exit 1
    }
    Write-Host "Virtual environment created successfully." -ForegroundColor Green
} else {
    Write-Host "Virtual environment (.venv) already exists." -ForegroundColor Green
}

# 3. Upgrade pip and install requirements
Write-Host "Upgrading pip and installing requirements from requirements.txt..." -ForegroundColor Yellow
& .venv\Scripts\python.exe -m pip install --upgrade pip
& .venv\Scripts\pip.exe install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies."
    Exit 1
}

Write-Host "`n=== Setup Completed Successfully! ===" -ForegroundColor Green
Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "To start the Streamlit application, run:" -ForegroundColor Cyan
Write-Host "  streamlit run app.py" -ForegroundColor Yellow
