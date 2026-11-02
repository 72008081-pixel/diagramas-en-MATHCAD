try {
    $asm = [System.Reflection.Assembly]::LoadFrom("C:\Program Files\PTC\Mathcad Prime 11.0.0.0\Ptc.Controls.Core.dll")
    Write-Host "Loaded Ptc.Controls.Core.dll"
    $t = $asm.GetType("Ptc.Controls.Core.Serialization.McdxDeserializer")
    if ($t) {
        Write-Host "Found: " $t.FullName
    }
} catch {
    Write-Host "Error: " $_.Exception.Message
}
