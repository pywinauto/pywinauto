# Credits to: 
# https://github.com/originell/jpype/appveyor/runTestsuite.ps1
#
function xslt_transform($xml, $xsl, $output)
{
	trap [Exception]
	{
	    Write-Host $_.Exception
	}
	
	$xslt = New-Object System.Xml.Xsl.XslCompiledTransform
	$xslt.Load($xsl)
	$xslt.Transform($xml, $output)
}

function upload($file) {
    trap [Exception]
    {
        Write-Host $_.Exception
    }
    Write-Host "Uploading: " $file

    $wc = New-Object 'System.Net.WebClient'
    $wc.UploadFile("https://ci.appveyor.com/api/testresults/xunit/$($env:APPVEYOR_JOB_ID)", $file)

    $test_report_dir = ".\TestResultsReport"
    md -Force $test_report_dir | Out-Null
    $revid = $($env:APPVEYOR_REPO_COMMIT).Substring(0, 8)
    $rep_dest = "$test_report_dir\$($env:APPVEYOR_JOB_ID)-$revid-$($env:PYTHON_VERSION)-$($env:PYTHON_ARCH)-UIA$($env:UIA_SUPPORT)-result.xml"

    Write-Host "Copying test report to: " $rep_dest
    cp $file $rep_dest
    Push-AppveyorArtifact $rep_dest
}

function run {
    Write-Host $env:APPVEYOR_BUILD_FOLDER

    cd $env:APPVEYOR_BUILD_FOLDER
    $stylesheet =  "./ci/transform_xunit_to_appveyor.xsl"
    $input = "nosetests.xml"
    $output = "transformed.xml"
    
    # Show file extensions
    Set-ItemProperty -LiteralPath "HKCU:Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "HideFileExt" -Value "0" -Force
    Stop-Process -Name Explorer -Force
    Start-Sleep -Seconds 10

    #nosetests  --all-modules --with-xunit pywinauto/unittests
    # --traverse-namespace is required for python 3.8 https://stackoverflow.com/q/58556183
    $pyver = [System.Version]::new($env:PYTHON_VERSION)
    if ($pyver.Major -gt 3 -or ($pyver.Major -eq 3 -and $pyver.Minor -ge 9)) {
        coverage run --source=pywinauto -m nose2 --exclude=testall -vvv pywinauto.unittests
        coverage xml -o $input
    } else {
        nosetests --nologcapture --traverse-namespace --exclude=testall --with-xunit --with-coverage --cover-html --cover-html-dir=Coverage_report --cover-package=pywinauto --verbosity=3 pywinauto\unittests
    }
    $success = $?
    Write-Host "result code of nosetests:" $success

    xslt_transform $input $stylesheet $output

    upload $output

    # return exit code of testsuite
    if ( -not $success) {
        throw "testsuite not successful"
    }
}

run
