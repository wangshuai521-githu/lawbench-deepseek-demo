param(
    [string]$RepoRoot = "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench\legalbench-main",
    [string]$DashboardRoot = "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench\dashboard"
)

$ErrorActionPreference = "Stop"

$outputsDir = Join-Path $RepoRoot "outputs"
if (-not (Test-Path -LiteralPath $outputsDir)) {
    throw "Outputs directory not found: $outputsDir"
}

if (-not (Test-Path -LiteralPath $DashboardRoot)) {
    New-Item -ItemType Directory -Path $DashboardRoot | Out-Null
}

$jsonFiles = Get-ChildItem -LiteralPath $outputsDir -Filter "*.json" | Sort-Object LastWriteTime
$runs = New-Object System.Collections.Generic.List[object]

foreach ($file in $jsonFiles) {
    $run = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
    $runs.Add($run)
}

$dashboardData = [pscustomobject]@{
    generated_at = (Get-Date).ToString("s")
    run_count    = $runs.Count
    runs         = $runs
}

$dataPath = Join-Path $DashboardRoot "data.json"
$dashboardData | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $dataPath -Encoding UTF8

$embeddedJson = $dashboardData | ConvertTo-Json -Depth 10 -Compress

$html = @'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LegalBench DeepSeek Dashboard</title>
  <style>
    :root {
      --bg: #f5efe2;
      --panel: #fffaf1;
      --ink: #1f2933;
      --muted: #52606d;
      --accent: #0f766e;
      --accent-2: #f59e0b;
      --border: #e7dcc8;
      --good: #166534;
      --bad: #b91c1c;
      --shadow: 0 18px 50px rgba(31, 41, 51, 0.08);
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background:
        radial-gradient(circle at top left, rgba(245, 158, 11, 0.18), transparent 30%),
        radial-gradient(circle at top right, rgba(15, 118, 110, 0.16), transparent 28%),
        linear-gradient(180deg, #fbf7ef 0%, var(--bg) 100%);
      color: var(--ink);
    }

    .wrap {
      max-width: 1180px;
      margin: 0 auto;
      padding: 40px 20px 80px;
    }

    .hero {
      display: grid;
      gap: 20px;
      margin-bottom: 24px;
    }

    .eyebrow {
      letter-spacing: 0.16em;
      text-transform: uppercase;
      font-size: 12px;
      color: var(--accent);
      font-weight: 700;
    }

    h1 {
      margin: 0;
      font-size: clamp(32px, 6vw, 62px);
      line-height: 0.95;
    }

    .lede {
      max-width: 760px;
      font-size: 18px;
      line-height: 1.6;
      color: var(--muted);
      margin: 0;
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin: 28px 0 34px;
    }

    .card, .panel {
      background: rgba(255, 250, 241, 0.92);
      border: 1px solid var(--border);
      border-radius: 22px;
      box-shadow: var(--shadow);
    }

    .card {
      padding: 20px 22px;
    }

    .card .label {
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 10px;
    }

    .card .value {
      font-size: 34px;
      font-weight: 700;
    }

    .panel {
      overflow: hidden;
      margin-bottom: 22px;
    }

    .panel-head {
      padding: 18px 22px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }

    .panel-head h2 {
      margin: 0;
      font-size: 24px;
    }

    .panel-body {
      padding: 0 22px 22px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-family: "Segoe UI", sans-serif;
      font-size: 14px;
    }

    th, td {
      text-align: left;
      padding: 14px 8px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }

    th {
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .pill {
      display: inline-block;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      font-weight: 700;
      background: #e6fffb;
      color: var(--accent);
    }

    .ok { color: var(--good); font-weight: 700; }
    .bad { color: var(--bad); font-weight: 700; }

    details {
      border-top: 1px solid var(--border);
      padding: 16px 0;
    }

    summary {
      cursor: pointer;
      font-family: "Segoe UI", sans-serif;
      font-weight: 700;
    }

    .detail-grid {
      display: grid;
      gap: 12px;
      margin-top: 12px;
      font-family: "Segoe UI", sans-serif;
    }

    .detail-grid pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      background: #fff;
      padding: 14px;
      border-radius: 14px;
      border: 1px solid var(--border);
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="eyebrow">Legal NLP Benchmark Demo</div>
      <h1>LegalBench x DeepSeek</h1>
      <p class="lede">
        A lightweight benchmark workflow built on top of the open-source LegalBench dataset.
        This dashboard shows benchmark runs, task-level accuracy, and per-sample predictions.
      </p>
    </section>

    <section class="stats" id="stats"></section>
    <section class="panel">
      <div class="panel-head">
        <h2>Benchmark Runs</h2>
        <span class="pill" id="generatedAt"></span>
      </div>
      <div class="panel-body">
        <table>
          <thead>
            <tr>
              <th>Task</th>
              <th>Split</th>
              <th>Model</th>
              <th>Samples</th>
              <th>Accuracy</th>
              <th>Run ID</th>
            </tr>
          </thead>
          <tbody id="runsTable"></tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>Prediction Details</h2>
        <span class="pill">Expand a run to inspect rows</span>
      </div>
      <div class="panel-body" id="details"></div>
    </section>
  </div>

  <script>
    const DASHBOARD_DATA = __DASHBOARD_DATA__;

    function main() {
      const data = DASHBOARD_DATA;
      document.getElementById('generatedAt').textContent = 'Generated: ' + data.generated_at;

      const sampleTotal = data.runs.reduce((sum, run) => sum + (run.sample_count || 0), 0);
      const stats = [
        ['Runs', data.run_count],
        ['Samples', sampleTotal],
        ['Tasks', new Set(data.runs.map(run => run.task)).size],
        ['Best Accuracy', data.runs.length ? Math.max(...data.runs.map(run => run.accuracy || 0)) : 0]
      ];

      document.getElementById('stats').innerHTML = stats.map(([label, value]) => `
        <article class="card">
          <div class="label">${label}</div>
          <div class="value">${value}</div>
        </article>
      `).join('');

      document.getElementById('runsTable').innerHTML = data.runs.map(run => `
        <tr>
          <td>${run.task}</td>
          <td>${run.split}</td>
          <td>${run.model}</td>
          <td>${run.sample_count}</td>
          <td class="${(run.accuracy || 0) >= 0.5 ? 'ok' : 'bad'}">${run.accuracy}</td>
          <td>${run.run_id}</td>
        </tr>
      `).join('');

      document.getElementById('details').innerHTML = data.runs.slice().reverse().map(run => `
        <details>
          <summary>${run.task} / ${run.split} / ${run.model} / accuracy=${run.accuracy}</summary>
          <div class="detail-grid">
            ${run.results.map(item => `
              <article>
                <p><strong>Index:</strong> ${item.index} |
                <strong>Gold:</strong> ${item.gold} |
                <strong>Prediction:</strong> ${item.prediction} |
                <strong class="${item.correct ? 'ok' : 'bad'}">${item.correct ? 'Correct' : 'Wrong'}</strong></p>
                <pre>${item.raw_output}</pre>
              </article>
            `).join('')}
          </div>
        </details>
      `).join('');
    }

    main();
  </script>
</body>
</html>
'@

$htmlPath = Join-Path $DashboardRoot "index.html"
$html = $html.Replace("__DASHBOARD_DATA__", $embeddedJson)
Set-Content -LiteralPath $htmlPath -Value $html -Encoding UTF8

Write-Host "Dashboard data: $dataPath"
Write-Host "Dashboard page: $htmlPath"
