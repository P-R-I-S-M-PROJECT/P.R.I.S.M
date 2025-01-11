param(
    [Parameter(Mandatory=$false)]
    [string]$RenderPath = "",
    [Parameter(Mandatory=$false)]
    [string]$Metadata = "{}"
)

# Configuration
$processingPath = "C:\Program Files\processing-4.3\processing-java.exe"
$projectRoot = Split-Path -Parent $PSScriptRoot
$sketchPath = Join-Path $projectRoot "auto.pde"
$ffmpegPath = Join-Path $PSScriptRoot "ffmpeg.exe"
$maxExecutionTime = 180  # 3 minutes timeout

# Create renders directory and snapshots subdirectory if they don't exist
$rendersDir = Join-Path $projectRoot "renders"
$snapshotsDir = Join-Path $rendersDir "snapshots"
if (-not (Test-Path $rendersDir)) {
    New-Item -ItemType Directory -Path $rendersDir | Out-Null
}
if (-not (Test-Path $snapshotsDir)) {
    New-Item -ItemType Directory -Path $snapshotsDir | Out-Null
}

# Modify RenderPath to be inside renders directory
$renderVersion = [regex]::Match($RenderPath, 'render_v(\d+)$').Groups[1].Value
if ($renderVersion) {
    $RenderPath = Join-Path $rendersDir "render_v$renderVersion"
    # Create render version directory if it doesn't exist
    if (-not (Test-Path $RenderPath)) {
        New-Item -ItemType Directory -Path $RenderPath | Out-Null
    }
}

# Create render directory if it doesn't exist
if (-not (Test-Path $RenderPath)) {
    New-Item -ItemType Directory -Path $RenderPath | Out-Null
}

# Copy auto.pde to render directory
$sketchCopy = Join-Path $RenderPath "render_v$renderVersion.pde"
try {
    if (-not (Test-Path $sketchPath)) {
        Write-Error "Source sketch file not found: $sketchPath"
        return $false
    }
    Copy-Item -Path $sketchPath -Destination $sketchCopy -Force
    if (-not (Test-Path $sketchCopy)) {
        Write-Error "Failed to copy sketch to: $sketchCopy"
        return $false
    }
    Write-Host "Successfully copied sketch to: $sketchCopy"
} catch {
    Write-Error "Error copying sketch file: $_"
    return $false
}

Write-Host "Starting with RenderPath: $RenderPath"
Write-Host "Using sketch path: $sketchPath"

# Create web videos directory
$webVideosDir = Join-Path $projectRoot "web\public\videos"
if (-not (Test-Path $webVideosDir)) {
    New-Item -ItemType Directory -Path $webVideosDir -Force | Out-Null
}

# Kill any existing Processing instances first
Get-Process | Where-Object { $_.ProcessName -like "*processing-java*" -or $_.ProcessName -like "*java*" } | 
    ForEach-Object {
        try {
            Write-Host "Killing existing process: $($_.ProcessName) (PID: $($_.Id))"
            $_ | Stop-Process -Force -ErrorAction Stop
        } catch {
            Write-Host "Process already terminated: $($_.ProcessName) (PID: $($_.Id))"
        }
    }

# Wait to ensure processes are killed
Start-Sleep -Seconds 2

try {
    Write-Host "Running Processing sketch from auto.pde"
    
    $processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processStartInfo.FileName = $processingPath
    $processStartInfo.Arguments = "--sketch=$projectRoot --output=$RenderPath --force --no-java --run"
    $processStartInfo.UseShellExecute = $false
    $processStartInfo.RedirectStandardOutput = $true
    $processStartInfo.RedirectStandardError = $true
    $processStartInfo.CreateNoWindow = $true
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $processStartInfo
    
    # Capture output using script blocks
    $outputBuilder = New-Object System.Text.StringBuilder
    $errorBuilder = New-Object System.Text.StringBuilder
    
    $outputScriptBlock = {
        if ($EventArgs.Data) {
            $outputBuilder.AppendLine($EventArgs.Data)
            Write-Host $EventArgs.Data
        }
    }
    
    $errorScriptBlock = {
        if ($EventArgs.Data) {
            $errorBuilder.AppendLine($EventArgs.Data)
            Write-Host "Error: $($EventArgs.Data)" -ForegroundColor Red
        }
    }
    
    # Register event handlers
    $outputEvent = Register-ObjectEvent -InputObject $process -EventName OutputDataReceived -Action $outputScriptBlock
    $errorEvent = Register-ObjectEvent -InputObject $process -EventName ErrorDataReceived -Action $errorScriptBlock
    
    $startTime = Get-Date
    $process.Start() | Out-Null
    $processId = $process.Id
    
    # Begin async output reading
    $process.BeginOutputReadLine()
    $process.BeginErrorReadLine()
    
    # Wait for frames to be generated
    $framesComplete = $false
    $lastFrameCount = 0
    while (-not $framesComplete) {
        Start-Sleep -Seconds 2
        
        # Check if process is still running
        try {
            $null = Get-Process -Id $processId -ErrorAction Stop
        } catch {
            # Process ended - check if we have an error
            if ($errorBuilder.Length -gt 0) {
                Write-Host "Processing Error: $($errorBuilder.ToString())"
                return $false
            }
            # No error but process ended - check frame count
            $frameCount = (Get-ChildItem -Path $RenderPath -Filter "frame-*.png" -ErrorAction SilentlyContinue).Count
            if ($frameCount -lt 360) {
                Write-Host "Process terminated before generating all frames. Generated: $frameCount"
                return $false
            }
        }
        
        # Check frame count
        $frameCount = (Get-ChildItem -Path $RenderPath -Filter "frame-*.png" -ErrorAction SilentlyContinue).Count
        
        # Check if we have all frames
        if ($frameCount -ge 360) {
            Write-Host "All frames generated successfully"
            $framesComplete = $true
            break
        }
        
        # Check timeout
        $runTime = ((Get-Date) - $startTime).TotalSeconds
        if ($runTime -gt $maxExecutionTime) {
            Write-Host "Error: Process exceeded maximum execution time of $maxExecutionTime seconds"
            return $false
        }
    }
    
    # Process video if frames exist
    $frames = Get-ChildItem -Path $RenderPath -Filter "frame-*.png"
    if ($frames.Count -ge 360) {
        # Clean up compiled files but preserve PDE
        Write-Host "Cleaning up compiled files (preserving PDE)..."
        Remove-Item -Path "$RenderPath\source" -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -Path "$RenderPath\*.class" -Force -ErrorAction SilentlyContinue
        
        # Re-copy PDE file to ensure it exists
        Write-Host "Re-copying PDE file to ensure preservation..."
        Copy-Item -Path $sketchPath -Destination $sketchCopy -Force
        
        $outputFile = Join-Path $RenderPath "output.mp4"
        $version = $RenderPath -replace '.*_v(\d+)$','$1'
        $timestamp = [int64](Get-Date -UFormat %s) * 1000
        $finalFile = Join-Path $webVideosDir "animation_v$version-$timestamp.mp4"
        
        # Create metadata file
        $metadataFile = Join-Path $webVideosDir "animation_v$version-$timestamp.json"
        $Metadata | Out-File -FilePath $metadataFile -Encoding UTF8
        
        & $ffmpegPath -framerate 60 -i "$RenderPath\frame-%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 17 $outputFile
        
        if (Test-Path $outputFile) {
            Move-Item $outputFile $finalFile -Force
            Write-Host "Video saved as: $finalFile"
            Write-Host "Metadata saved as: $metadataFile"
            return $true
        }
    }
    
    return $false
    
} catch {
    Write-Error "Error: $_"
    return $false
} finally {
    # Cleanup event handlers
    if ($outputEvent) { Unregister-Event -SourceIdentifier $outputEvent.Name }
    if ($errorEvent) { Unregister-Event -SourceIdentifier $errorEvent.Name }
    
    # Clean up compiled files
    Write-Host "Cleaning up compiled files..."
    Remove-Item -Path "$RenderPath\source" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$RenderPath\*.class" -Force -ErrorAction SilentlyContinue
    
    # Final cleanup of processes
    Get-Process | Where-Object { $_.ProcessName -like "*processing-java*" -or $_.ProcessName -like "*java*" } | 
        ForEach-Object {
            try {
                Write-Host "Cleaning up process: $($_.ProcessName) (PID: $($_.Id))"
                $_ | Stop-Process -Force -ErrorAction Stop
            } catch {
                Write-Host "Process already terminated: $($_.ProcessName)"
            }
        }
        
    # Save PDE snapshot after all cleanup is done
    $sketchCopy = Join-Path $RenderPath "render_v$renderVersion.pde"
    Write-Host "Saving PDE snapshot..."
    Copy-Item -Path $sketchPath -Destination $sketchCopy -Force
}
  