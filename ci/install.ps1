$PYTHON_URL = "https://www.python.org/ftp/python/"
# https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe
# https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
# https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
# https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe
# https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe

function DownloadPython ($python_version, $platform_suffix) {
    $webclient = New-Object System.Net.WebClient
    $filename = ""
    if ($python_version -match "3.9") {
        $filename = "3.9.13/python-3.9.13" + $platform_suffix + ".exe"
    } else {
        if ($python_version -match "3.10") {
            $filename = "3.10.11/python-3.10.11" + $platform_suffix + ".exe"
        } else {
            if ($python_version -match "3.11") {
                $filename = "3.11.9/python-3.11.9" + $platform_suffix + ".exe"
            } else {
                if ($python_version -match "3.12") {
                    $filename = "3.12.9/python-3.12.9" + $platform_suffix + ".exe"
                } else {
                    if ($python_version -match "3.13") {
                        $filename = "3.13.2/python-3.13.2" + $platform_suffix + ".exe"
                    } else {
                        return "" # unknown version
                    }
                }
            }
        }
    }
    $url = $PYTHON_URL + $filename

    $basedir = $pwd.Path + "\"
    $filename = "$filename" -replace "/", "-"
    $filepath = $basedir + $filename
    if (Test-Path $filename) {
        Write-Host "Reusing $filepath"
        return $filepath
    }

    # Download and retry up to 3 times in case of network transient errors.
    Write-Host "Downloading $filename from $url ..."
    $retry_attempts = 2
    for($i=0; $i -lt $retry_attempts; $i++){
        try {
            $webclient.DownloadFile($url, $filepath)
            break
        }
        Catch [Exception]{
            Start-Sleep 1
        }
   }
   if (Test-Path $filepath) {
       Write-Host "File saved at $filepath"
   } else {
       # Retry once to get the error message if any at the last try
       $webclient.DownloadFile($url, $filepath)
   }
   return $filepath
}

function InstallPython ($python_version, $architecture, $python_home) {
    Write-Output "Installing Python $python_version for $architecture bit architecture to $python_home ..."
    if (Test-Path $python_home) {
        Write-Output "$python_home already exists, skipping."
        return $false
    }
    if ($architecture -match "32") {
        $platform_suffix = ""
    } else {
        $platform_suffix = "-amd64"
    }

    $filepath = DownloadPython $python_version $platform_suffix
    if ($filepath -eq "") {
        Write-Output "Unknown Python version: $python_version"
        Exit 1
    }
    Write-Output "Installing $filepath to $python_home ..."
    $install_log = $python_home + ".log"
    $args = "/quiet InstallAllUsers=1 PrependPath=1 DefaultAllUsersTargetDir=$python_home Include_doc=0 Include_dev=0 Include_launcher=0 Include_test=0"
    Write-Output "$filepath $args"
    Start-Process -FilePath $filepath -ArgumentList $args -Wait -Passthru
    if (Test-Path $python_home) {
        Write-Output "Python $python_version ($architecture) installation complete"
    } else {
        Write-Output "Failed to install Python in $python_home"
        Get-Content -Path $install_log
        Exit 1
    }
}

function InstallComtypes ($python_home, $python_version) {
    $pip_path = "$python_home\Scripts\pip.exe"
    Write-Output "pip_path = $pip_path"
    $pip_args = "install https://github.com/junkmd/comtypes/archive/refs/heads/cpython-gh-100926.zip"
    Start-Process -FilePath $pip_path -ArgumentList $pip_args -Wait -Passthru
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
    
    InstallPython $env:PYTHON_VERSION $env:PYTHON_ARCH $env:PYTHON

    if ($env:UIA_SUPPORT -eq "YES") {
        InstallComtypes $env:PYTHON $env:PYTHON_VERSION
    }
}

main
