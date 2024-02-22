param(
    [string]$PythonPath = "C:\Python34-x64",
    [string]$PythonVersion = "3.4",
    [int]$PythonArch = 64,
    [string]$UIASupport = "NO"
)

$MinicondaUrl = "http://repo.continuum.io/miniconda/"

function DownloadMiniconda($pythonVersion, $platformSuffix) {
    $webClient = New-Object System.Net.WebClient
    $filename = if ($pythonVersion -match "3.4") { "Miniconda3-3.8.3-Windows-$platformSuffix.exe" } else { "Miniconda-3.8.3-Windows-$platformSuffix.exe" }
    $url = "$MinicondaUrl$filename"

    $basePath = Join-Path $pwd.Path ""
    $filePath = Join-Path $basePath $filename

    if (Test-Path $filePath) {
        Write-Host "Reusing $filePath"
        return $filePath
    }

    # Download and retry up to 3 times in case of network transient errors.
    Write-Host "Downloading $filename from $url"
    $retryAttempts = 2
    for ($i = 0; $i -lt $retryAttempts; $i++) {
        try {
            $webClient.DownloadFile($url, $filePath)
            break
        } Catch [Exception] {
            Start-Sleep 1
        }
    }
    if (Test-Path $filePath) {
        Write-Host "File saved at $filePath"
    } else {
        # Retry once to get the error message if any at the last try
        $webClient.DownloadFile($url, $filePath)
    }
    return $filePath
}

function InstallMiniconda($pythonVersion, $architecture, $pythonHome) {
    Write-Host "Installing Python $pythonVersion for $architecture-bit architecture to $pythonHome"
    if (Test-Path $pythonHome) {
        Write-Host "$pythonHome already exists, skipping."
        return $false
    }
    $platformSuffix = if ($architecture -eq 32) { "x86" } else { "x86_64" }
    $filePath = DownloadMiniconda $pythonVersion $platformSuffix
    Write-Host "Installing $filePath to $pythonHome"
    $installLog = Join-Path $pythonHome ".log"
    $args = "/S /D=$pythonHome"
    Write-Host "$filePath $args"
    Start-Process -FilePath $filePath -ArgumentList $args -Wait -Passthru
    if (Test-Path $pythonHome) {
        Write-Host "Python $pythonVersion ($architecture-bit) installation complete"
    } else {
        Write-Host "Failed to install Python in $pythonHome"
        Get-Content -Path $installLog
        Exit 1
    }
}

function InstallCondaPackages($pythonHome, $spec) {
    $condaPath = Join-Path $pythonHome "Scripts\conda.exe"
    $args = "install --yes $spec"
    Write-Host ("conda " + $args)
    Start-Process -FilePath "$condaPath" -ArgumentList $args -Wait -Passthru
}

function UpdateConda($pythonHome) {
    $condaPath = Join-Path $pythonHome "Scripts\conda.exe"
    Write-Host "Updating conda..."
    $args = "update --yes conda"
    Write-Host "$condaPath $args"
    Start-Process -FilePath "$condaPath" -ArgumentList $args -Wait -Passthru
}

function InstallComtypes($pythonHome) {
    $pipPath = Join-Path $pythonHome "Scripts\pip.exe"
    $args = "install comtypes"
    Start-Process -FilePath "$pipPath" -ArgumentList $args -Wait -Passthru
}

function main() {
    try {
        $currentResolution = Get-DisplayResolution
        Write-Host "Current resolution: $currentResolution"
    } Catch [Exception] {
        Write-Host "Can't print current resolution. Get-DisplayResolution cmd is not available"
    }

    Write-Host "PYTHON=$PythonPath"
    Write-Host "PYTHON_VERSION=$PythonVersion"
    Write-Host "PYTHON_ARCH=$PythonArch"

    if ($UIASupport -eq "YES") {
        InstallComtypes $PythonPath
    }
    # InstallMiniconda $PythonVersion $PythonArch $PythonPath
    # UpdateConda $PythonPath
    # InstallCondaPackages $PythonPath "pywin32 Pillow coverage nose"
}

main
