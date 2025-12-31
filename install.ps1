# AnomReceipt Windows Installer
# Professional, bulletproof installation script
# Supports interactive and silent modes

param(
    [switch]$Silent = $false,
    [switch]$Help = $false
)

# Configuration
$ErrorActionPreference = "Stop"
$MinPythonVersion = [version]"3.8.0"
$LogFile = "anomreceipt_install.log"
$VenvPath = "venv"
$RequirementsFile = "requirements.txt"

# Colors for output
$ColorSuccess = "Green"
$ColorError = "Red"
$ColorWarning = "Yellow"
$ColorInfo = "Cyan"

# Initialize logging
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $LogMessage
    
    if (-not $Silent) {
        switch ($Level) {
            "ERROR" { Write-Host $Message -ForegroundColor $ColorError }
            "WARNING" { Write-Host $Message -ForegroundColor $ColorWarning }
            "SUCCESS" { Write-Host $Message -ForegroundColor $ColorSuccess }
            "INFO" { Write-Host $Message -ForegroundColor $ColorInfo }
            default { Write-Host $Message }
        }
    }
}

function Show-Help {
    Write-Host ""
    Write-Host "AnomReceipt Windows Installer" -ForegroundColor $ColorInfo
    Write-Host "=============================" -ForegroundColor $ColorInfo
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor $ColorInfo
    Write-Host "  .\install.ps1              # Interactive installation"
    Write-Host "  .\install.ps1 -Silent      # Silent installation"
    Write-Host "  .\install.ps1 -Help        # Show this help"
    Write-Host ""
    Write-Host "Requirements:" -ForegroundColor $ColorInfo
    Write-Host "  - Python 3.8 or higher"
    Write-Host "  - pip (Python package installer)"
    Write-Host "  - venv module (Python virtual environment)"
    Write-Host ""
    exit 0
}

function Test-PythonInstalled {
    Write-Log "Checking for Python installation..." "INFO"
    
    try {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCmd) {
            $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
        }
        
        if (-not $pythonCmd) {
            Write-Log "Python is not installed or not in PATH" "ERROR"
            Write-Log "Please install Python 3.8 or higher from https://www.python.org/downloads/" "ERROR"
            Write-Log "Make sure to check 'Add Python to PATH' during installation" "ERROR"
            return $null
        }
        
        return $pythonCmd.Source
    }
    catch {
        Write-Log "Error detecting Python: $_" "ERROR"
        return $null
    }
}

function Get-PythonVersion {
    param([string]$PythonPath)
    
    try {
        $versionOutput = & $PythonPath --version 2>&1
        if ($versionOutput -match "Python (\d+\.\d+\.\d+)") {
            return [version]$matches[1]
        }
        return $null
    }
    catch {
        Write-Log "Error getting Python version: $_" "ERROR"
        return $null
    }
}

function Test-PipAvailable {
    param([string]$PythonPath)
    
    Write-Log "Checking for pip..." "INFO"
    
    try {
        $pipCheck = & $PythonPath -m pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "pip is available: $pipCheck" "SUCCESS"
            return $true
        }
        else {
            Write-Log "pip is not available" "ERROR"
            Write-Log "Attempting to install pip..." "INFO"
            
            # Try to install pip
            $ensurepip = & $PythonPath -m ensurepip --default-pip 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Log "pip installed successfully" "SUCCESS"
                return $true
            }
            else {
                Write-Log "Failed to install pip: $ensurepip" "ERROR"
                return $false
            }
        }
    }
    catch {
        Write-Log "Error checking pip: $_" "ERROR"
        return $false
    }
}

function Test-VenvAvailable {
    param([string]$PythonPath)
    
    Write-Log "Checking for venv module..." "INFO"
    
    try {
        $venvCheck = & $PythonPath -m venv --help 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "venv module is available" "SUCCESS"
            return $true
        }
        else {
            Write-Log "venv module is not available" "ERROR"
            Write-Log "Please install python3-venv package" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Error checking venv: $_" "ERROR"
        return $false
    }
}

function New-VirtualEnvironment {
    param([string]$PythonPath)
    
    Write-Log "Creating virtual environment in '$VenvPath'..." "INFO"
    
    try {
        if (Test-Path $VenvPath) {
            Write-Log "Removing existing virtual environment..." "WARNING"
            Remove-Item -Path $VenvPath -Recurse -Force
        }
        
        & $PythonPath -m venv $VenvPath
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to create virtual environment" "ERROR"
            return $false
        }
        
        Write-Log "Virtual environment created successfully" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Error creating virtual environment: $_" "ERROR"
        return $false
    }
}

function Get-VenvPython {
    return Join-Path $VenvPath "Scripts\python.exe"
}

function Get-VenvPip {
    return Join-Path $VenvPath "Scripts\pip.exe"
}

function Install-Requirements {
    $venvPython = Get-VenvPython
    $venvPip = Get-VenvPip
    
    Write-Log "Upgrading pip in virtual environment..." "INFO"
    
    try {
        & $venvPython -m pip install --upgrade pip 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Warning: Could not upgrade pip" "WARNING"
        }
    }
    catch {
        Write-Log "Warning: Error upgrading pip: $_" "WARNING"
    }
    
    Write-Log "Installing requirements from '$RequirementsFile'..." "INFO"
    
    if (-not (Test-Path $RequirementsFile)) {
        Write-Log "Requirements file not found: $RequirementsFile" "ERROR"
        return $false
    }
    
    try {
        $installOutput = & $venvPip install -r $RequirementsFile 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to install requirements" "ERROR"
            Write-Log "Output: $installOutput" "ERROR"
            return $false
        }
        
        Write-Log "Requirements installed successfully" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Error installing requirements: $_" "ERROR"
        return $false
    }
}

function Test-AllImports {
    $venvPython = Get-VenvPython
    
    Write-Log "Verifying all packages are importable..." "INFO"
    
    $requiredPackages = @(
        "PySide6",
        "yaml",
        "escpos",
        "PIL",
        "usb",
        "requests",
        "bs4",
        "pytesseract",
        "cv2",
        "numpy"
    )
    
    $allSuccess = $true
    
    foreach ($package in $requiredPackages) {
        try {
            $importTest = & $venvPython -c "import $package" 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Log "  ✓ $package" "SUCCESS"
            }
            else {
                Write-Log "  ✗ $package - Failed to import" "ERROR"
                $allSuccess = $false
            }
        }
        catch {
            Write-Log "  ✗ $package - Error: $_" "ERROR"
            $allSuccess = $false
        }
    }
    
    if ($allSuccess) {
        Write-Log "All packages verified successfully" "SUCCESS"
        return $true
    }
    else {
        Write-Log "Some packages failed to import" "ERROR"
        return $false
    }
}

function Test-TesseractInstalled {
    Write-Log "Checking for Tesseract OCR..." "INFO"
    
    try {
        $tesseractCmd = Get-Command tesseract -ErrorAction SilentlyContinue
        
        if ($tesseractCmd) {
            Write-Log "Tesseract OCR is installed" "SUCCESS"
            return $true
        }
        else {
            Write-Log "Tesseract OCR is not installed" "WARNING"
            Write-Log "The OCR feature requires Tesseract OCR" "WARNING"
            Write-Log "Download from: https://github.com/UB-Mannheim/tesseract/wiki" "INFO"
            Write-Log "Application will work but OCR features will be disabled" "WARNING"
            return $false
        }
    }
    catch {
        Write-Log "Error checking Tesseract: $_" "WARNING"
        return $false
    }
}

function New-LaunchScript {
    Write-Log "Creating launch script..." "INFO"
    
    $venvPython = Get-VenvPython
    
    $launchScriptContent = @"
@echo off
echo Starting AnomReceipt...
"$venvPython" main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error: Application failed to start
    echo Check anomreceipt.log for details
    pause
)
"@
    
    try {
        $launchScriptContent | Out-File -FilePath "launch.bat" -Encoding ASCII
        Write-Log "Launch script created: launch.bat" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Error creating launch script: $_" "ERROR"
        return $false
    }
}

function Show-CompletionMessage {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor $ColorSuccess
    Write-Host "  AnomReceipt Installation Complete!" -ForegroundColor $ColorSuccess
    Write-Host "============================================" -ForegroundColor $ColorSuccess
    Write-Host ""
    Write-Host "To start the application:" -ForegroundColor $ColorInfo
    Write-Host "  1. Double-click 'launch.bat'" -ForegroundColor White
    Write-Host "  OR" -ForegroundColor $ColorInfo
    Write-Host "  2. Run: .\venv\Scripts\python.exe main.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Installation log: $LogFile" -ForegroundColor $ColorInfo
    Write-Host ""
}

# Main installation flow
function Start-Installation {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor $ColorInfo
    Write-Host "  AnomReceipt Windows Installer" -ForegroundColor $ColorInfo
    Write-Host "============================================" -ForegroundColor $ColorInfo
    Write-Host ""
    
    Write-Log "Starting installation..." "INFO"
    Write-Log "PowerShell version: $($PSVersionTable.PSVersion)" "INFO"
    Write-Log "OS: $env:OS" "INFO"
    
    # Check Python
    $pythonPath = Test-PythonInstalled
    if (-not $pythonPath) {
        Write-Log "Installation failed: Python not found" "ERROR"
        exit 1
    }
    
    Write-Log "Python found: $pythonPath" "SUCCESS"
    
    # Check Python version
    $pythonVersion = Get-PythonVersion -PythonPath $pythonPath
    if (-not $pythonVersion) {
        Write-Log "Installation failed: Could not determine Python version" "ERROR"
        exit 1
    }
    
    Write-Log "Python version: $pythonVersion" "INFO"
    
    if ($pythonVersion -lt $MinPythonVersion) {
        Write-Log "Python version $pythonVersion is below minimum required version $MinPythonVersion" "ERROR"
        Write-Log "Please upgrade Python from https://www.python.org/downloads/" "ERROR"
        exit 1
    }
    
    Write-Log "Python version is sufficient" "SUCCESS"
    
    # Check pip
    if (-not (Test-PipAvailable -PythonPath $pythonPath)) {
        Write-Log "Installation failed: pip is not available" "ERROR"
        exit 1
    }
    
    # Check venv
    if (-not (Test-VenvAvailable -PythonPath $pythonPath)) {
        Write-Log "Installation failed: venv module is not available" "ERROR"
        exit 1
    }
    
    # Create virtual environment
    if (-not (New-VirtualEnvironment -PythonPath $pythonPath)) {
        Write-Log "Installation failed: Could not create virtual environment" "ERROR"
        exit 1
    }
    
    # Install requirements
    if (-not (Install-Requirements)) {
        Write-Log "Installation failed: Could not install requirements" "ERROR"
        exit 1
    }
    
    # Verify all imports
    if (-not (Test-AllImports)) {
        Write-Log "Installation failed: Package verification failed" "ERROR"
        Write-Log "Some packages could not be imported" "ERROR"
        exit 1
    }
    
    # Check Tesseract (optional)
    Test-TesseractInstalled | Out-Null
    
    # Create launch script
    New-LaunchScript | Out-Null
    
    Write-Log "Installation completed successfully" "SUCCESS"
    
    if (-not $Silent) {
        Show-CompletionMessage
    }
    
    exit 0
}

# Entry point
try {
    if ($Help) {
        Show-Help
        exit 0
    }
    
    Start-Installation
}
catch {
    Write-Log "Fatal error during installation: $_" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    exit 1
}
