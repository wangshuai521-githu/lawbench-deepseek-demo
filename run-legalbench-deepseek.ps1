param(
    [string]$RepoRoot = "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench\legalbench-main",
    [string]$TaskName = "hearsay",
    [ValidateSet("train", "test")]
    [string]$Split = "test",
    [string]$PromptFile = "base_prompt.txt",
    [string]$Model = "deepseek-v4-flash",
    [string]$ApiBase = "https://api.deepseek.com",
    [int]$MaxSamples = 10,
    [int]$TimeoutSec = 120,
    [switch]$SavePredictions,
    [switch]$StrictLabels
)

$ErrorActionPreference = "Stop"

function Normalize-Label {
    param(
        [string]$Text,
        [switch]$StrictMode
    )

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return ""
    }

    $value = $Text.Trim()

    if (-not $StrictMode) {
        if ($value -match '(?i)\byes\b') {
            return "Yes"
        }
        if ($value -match '(?i)\bno\b') {
            return "No"
        }
        if ($value -match '(?i)\btrue\b') {
            return "True"
        }
        if ($value -match '(?i)\bfalse\b') {
            return "False"
        }
        if ($value -match '(?i)\boption\s*([A-D])\b') {
            return $matches[1].ToUpper()
        }
        if ($value -match '(?i)\banswer\s*(?:is|:)?\s*["'']?([A-D])["'']?\b') {
            return $matches[1].ToUpper()
        }
        if ($value -match '(?i)\bcorrect answer\s*(?:is|:)?\s*["'']?([A-D])["'']?\b') {
            return $matches[1].ToUpper()
        }
        if ($value -match '(?i)\bthe answer\s*(?:is|:)?\s*["'']?([A-D])["'']?\b') {
            return $matches[1].ToUpper()
        }
        if ($value -match '(?i)\bchoose\s*["'']?([A-D])["'']?\b') {
            return $matches[1].ToUpper()
        }
    }

    if ($value -match '(?i)^\s*["'']?([A-D])["'']?\s*$') {
        return $matches[1].ToUpper()
    }

    return $value
}

function Get-PlaceholderNames {
    param([string]$Template)

    $matches = [regex]::Matches($Template, '\{\{([^}]+)\}\}')
    $names = New-Object System.Collections.Generic.List[string]
    foreach ($match in $matches) {
        $name = $match.Groups[1].Value.Trim()
        if (-not $names.Contains($name)) {
            $names.Add($name)
        }
    }
    return $names
}

function Render-Prompt {
    param(
        [string]$Template,
        [psobject]$Row
    )

    $output = $Template
    $placeholders = Get-PlaceholderNames -Template $Template

    foreach ($name in $placeholders) {
        $replacement = ""
        if ($Row.PSObject.Properties.Name -contains $name) {
            $replacement = [string]$Row.$name
        }
        $output = $output.Replace(("{{{0}}}" -f $name), $replacement)
    }

    return $output
}

function Sanitize-TextForJson {
    param([string]$Text)

    if ($null -eq $Text) {
        return ""
    }

    $value = [string]$Text

    $replacements = @{
        [char]0x2018 = "'"
        [char]0x2019 = "'"
        [char]0x201C = '"'
        [char]0x201D = '"'
        [char]0x2013 = "-"
        [char]0x2014 = "-"
        [char]0x2026 = "..."
        [char]0x00A0 = " "
    }

    foreach ($key in $replacements.Keys) {
        $value = $value.Replace([string]$key, $replacements[$key])
    }

    # Remove ASCII control chars except tab, CR, and LF.
    $value = [regex]::Replace($value, '[\x00-\x08\x0B\x0C\x0E-\x1F]', ' ')

    # Remove isolated Unicode surrogate code points which can break JSON serialization/parsing.
    $value = [regex]::Replace($value, '[\uD800-\uDFFF]', '')

    return $value
}

function Invoke-DeepSeekChat {
    param(
        [string]$Prompt,
        [string]$ApiKey,
        [string]$BaseUrl,
        [string]$ModelName,
        [int]$RequestTimeoutSec
    )

    $uri = $BaseUrl.TrimEnd("/") + "/chat/completions"
    $headers = @{
        "Authorization" = "Bearer $ApiKey"
    }
    $safePrompt = Sanitize-TextForJson -Text $Prompt
    $body = @{
        model = $ModelName
        temperature = 0
        messages = @(
            @{
                role = "user"
                content = $safePrompt
            }
        )
    } | ConvertTo-Json -Depth 6 -Compress

    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)

    $response = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -ContentType "application/json; charset=utf-8" -Body $bodyBytes -TimeoutSec $RequestTimeoutSec
    return [string]$response.choices[0].message.content
}

function Get-Accuracy {
    param([System.Collections.Generic.List[object]]$Results)

    if ($Results.Count -eq 0) {
        return 0
    }

    $correct = ($Results | Where-Object { $_.correct }).Count
    return [math]::Round(($correct / $Results.Count), 4)
}

if (-not $env:DEEPSEEK_API_KEY) {
    throw "Missing DEEPSEEK_API_KEY environment variable."
}

$taskDir = Join-Path $RepoRoot ("tasks\" + $TaskName)
$promptPath = Join-Path $taskDir $PromptFile
$dataPath = Join-Path $taskDir ("{0}.tsv" -f $Split)

if (-not (Test-Path -LiteralPath $taskDir)) {
    throw "Task directory not found: $taskDir"
}
if (-not (Test-Path -LiteralPath $promptPath)) {
    throw "Prompt file not found: $promptPath"
}
if (-not (Test-Path -LiteralPath $dataPath)) {
    throw "Dataset file not found: $dataPath"
}

$promptTemplate = Get-Content -LiteralPath $promptPath -Raw
$rows = Import-Csv -LiteralPath $dataPath -Delimiter "`t"

if ($MaxSamples -gt 0) {
    $rows = $rows | Select-Object -First $MaxSamples
}

$results = New-Object System.Collections.Generic.List[object]

foreach ($row in $rows) {
    $prompt = Render-Prompt -Template $promptTemplate -Row $row
    $rawOutput = Invoke-DeepSeekChat -Prompt $prompt -ApiKey $env:DEEPSEEK_API_KEY -BaseUrl $ApiBase -ModelName $Model -RequestTimeoutSec $TimeoutSec
    $prediction = Normalize-Label -Text $rawOutput -StrictMode:$StrictLabels
    $gold = Normalize-Label -Text ([string]$row.answer) -StrictMode:$StrictLabels
    $isCorrect = $prediction -eq $gold

    $results.Add([pscustomobject]@{
        task       = $TaskName
        split      = $Split
        index      = $row.index
        gold       = $gold
        prediction = $prediction
        correct    = $isCorrect
        raw_output = $rawOutput.Trim()
        prompt     = $prompt
    })
}

$accuracy = Get-Accuracy -Results $results

Write-Host ""
Write-Host "Task: $TaskName"
Write-Host "Split: $Split"
Write-Host "Model: $Model"
Write-Host "Samples: $($results.Count)"
Write-Host "Accuracy: $accuracy"
Write-Host ""

$results | Format-Table index, gold, prediction, correct -AutoSize

if ($SavePredictions) {
    $outDir = Join-Path $RepoRoot "outputs"
    if (-not (Test-Path -LiteralPath $outDir)) {
        New-Item -ItemType Directory -Path $outDir | Out-Null
    }

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $runId = "{0}-{1}-{2}-{3}" -f $TaskName, $Split, $Model.Replace("/", "-"), $timestamp
    $resultPath = Join-Path $outDir ($runId + ".json")

    $payload = [pscustomobject]@{
        run_id      = $runId
        task        = $TaskName
        split       = $Split
        prompt_file = $PromptFile
        model       = $Model
        api_base    = $ApiBase
        sample_count = $results.Count
        accuracy    = $accuracy
        created_at  = (Get-Date).ToString("s")
        results     = $results
    }

    $payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resultPath -Encoding UTF8
    Write-Host ""
    Write-Host "Saved predictions to: $resultPath"
}
