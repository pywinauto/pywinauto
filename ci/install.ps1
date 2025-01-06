function InstallComtypes ($python_home, $python_version) {
    $pip_path = $python_home + "\Scripts\pip.exe"
    $pip_args = "install comtypes"
    if ($python_version -match "2.7" -or $python_version -match "3.5" -or $python_version -match "3.6") {
        $pip_args = "install comtypes<=1.2.1"
    }
    Start-Process -FilePath "$pip_path" -ArgumentList $pip_args -Wait -Passthru
}

function main () {
    try {
        $CurrentResolution = Get-DisplayResolution
        Write-Output "Current resolution: $CurrentResolution"
    }
    Catch [Exception]{
        Write-Output "Can't print current resolution. Get-DisplayResolution cmd is not available"
    }

    Write-Output "PYTHON=$env:PYTHON"
    Write-Output "PYTHON_VERSION=$env:PYTHON_VERSION"
    Write-Output "PYTHON_ARCH=$env:PYTHON_ARCH"
    Write-Output "UIA_SUPPORT=$env:UIA_SUPPORT"

    if ($env:UIA_SUPPORT -eq "YES") {
        InstallComtypes $env:PYTHON $env:PYTHON_VERSION
    }
}

main
