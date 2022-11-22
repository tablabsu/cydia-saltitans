$script = $args[0]
if ($args.length -gt 1) {
    $params = $args[1..($args.length-1)] -join " "
}

Invoke-Expression ".\venv\Scripts\Activate.ps1"
Write-Output "Starting script $script..."
Set-Location -Path ".\scripts"
try {
    if (Test-Path -Path "$script.py" -PathType Leaf) {
        Invoke-Expression "python $script.py $params"
    } elseif (Test-Path -Path "$script.ps1" -PathType Leaf) {
        Invoke-Expression "./$script.ps1 $params"
    } else {
        Write-Output "No script found!"
    }
} finally {
    Set-Location -Path ".." 
    Invoke-Expression "deactivate"    
}

