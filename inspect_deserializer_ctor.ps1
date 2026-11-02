$asm = [System.Reflection.Assembly]::LoadFrom("C:\Program Files\PTC\Mathcad Prime 11.0.0.0\Ptc.Controls.Core.dll")
$t = $asm.GetType("Ptc.Controls.Core.Serialization.McdxDeserializer")
$t.GetConstructors() | ForEach-Object { 
    Write-Host "CTOR: " ($_.GetParameters() | ForEach-Object { $_.ParameterType.Name + " " + $_.Name })
}
