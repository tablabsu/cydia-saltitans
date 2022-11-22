$experiment=$args[0]
$experiment_path = "..\experiments\" + $experiment
$tgrabs_args = ""
$trex_args = ""

Invoke-Expression "conda activate tracking"

Write-Output $experiment_path # debug 
Invoke-Expression "tgrabs --help"

Invoke-Expression "conda deactivate"