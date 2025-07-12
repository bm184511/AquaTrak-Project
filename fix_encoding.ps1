# Fix encoding script for AquaTrak Project
# Re-encodes all .py files as UTF-8 (no BOM)

Write-Host "Starting encoding fix for all Python files..." -ForegroundColor Green

# Get all Python files recursively
$pythonFiles = Get-ChildItem -Recurse -Filter "*.py" | Where-Object { $_.FullName -notlike "*__pycache__*" }

$totalFiles = $pythonFiles.Count
$processedFiles = 0
$fixedFiles = 0

Write-Host "Found $totalFiles Python files to process..." -ForegroundColor Yellow

foreach ($file in $pythonFiles) {
    $processedFiles++
    Write-Progress -Activity "Fixing file encoding" -Status "Processing $($file.Name)" -PercentComplete (($processedFiles / $totalFiles) * 100)
    
    try {
        # Read the file content
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        
        # Check if file has BOM by reading as bytes
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        $hasBOM = $false
        
        if ($bytes.Length -ge 3) {
            if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
                $hasBOM = $true
                Write-Host "BOM detected in: $($file.FullName)" -ForegroundColor Red
            }
        }
        
        # Check for 0xFF byte at position 0
        if ($bytes.Length -ge 1 -and $bytes[0] -eq 0xFF) {
            Write-Host "0xFF byte detected at position 0 in: $($file.FullName)" -ForegroundColor Red
            $hasBOM = $true
        }
        
        # Re-save as UTF-8 without BOM
        $utf8NoBOM = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($file.FullName, $content, $utf8NoBOM)
        
        if ($hasBOM) {
            $fixedFiles++
            Write-Host "Fixed encoding for: $($file.FullName)" -ForegroundColor Green
        }
        
    } catch {
        Write-Host "Error processing $($file.FullName): $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Progress -Activity "Fixing file encoding" -Completed

Write-Host "`nEncoding fix completed!" -ForegroundColor Green
Write-Host "Total files processed: $processedFiles" -ForegroundColor Cyan
Write-Host "Files with encoding issues fixed: $fixedFiles" -ForegroundColor Cyan

if ($fixedFiles -gt 0) {
    Write-Host "`nPlease commit and push these changes to resolve the CI encoding issues." -ForegroundColor Yellow
} else {
    Write-Host "`nNo encoding issues found. The problem may be elsewhere." -ForegroundColor Yellow
} 