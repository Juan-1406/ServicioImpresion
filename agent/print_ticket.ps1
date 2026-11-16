$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$image = $null
$document = $null
try {
    $image = [System.Drawing.Image]::FromFile($env:EVENTPASS_PNG)
    $document = New-Object System.Drawing.Printing.PrintDocument
    $document.PrinterSettings.PrinterName = $env:EVENTPASS_PRINTER
    if (-not $document.PrinterSettings.IsValid) {
        throw 'La impresora configurada no esta instalada o no es valida.'
    }
    $document.DocumentName = 'EventPass - Ticket'
    $document.PrintController = New-Object System.Drawing.Printing.StandardPrintController
    $document.DefaultPageSettings.Margins = New-Object System.Drawing.Printing.Margins(0, 0, 0, 0)
    $document.add_PrintPage({
        param($sender, $eventArgs)
        $bounds = $eventArgs.PageSettings.PrintableArea
        $scale = [Math]::Min($bounds.Width / $image.Width, $bounds.Height / $image.Height)
        $width = [single]($image.Width * $scale)
        $height = [single]($image.Height * $scale)
        $x = [single]([Math]::Max(0, $bounds.X - $eventArgs.PageSettings.HardMarginX))
        $y = [single]([Math]::Max(0, $bounds.Y - $eventArgs.PageSettings.HardMarginY))
        $rectangle = New-Object System.Drawing.RectangleF($x, $y, $width, $height)
        $eventArgs.Graphics.DrawImage($image, $rectangle)
        $eventArgs.HasMorePages = $false
    })
    $document.Print()
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
} finally {
    if ($null -ne $document) { $document.Dispose() }
    if ($null -ne $image) { $image.Dispose() }
}
