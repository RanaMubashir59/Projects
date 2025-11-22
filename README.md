<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Eigenvalue Calculator — User Guide</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap">
  <style>
    :root{--bg:#0f1724;--card:#0b1220;--muted:#9aa4b2;--accent:#2563eb;--glass: rgba(255,255,255,0.03)}
    body{font-family:Inter,system-ui,Arial; margin:0; background:linear-gradient(180deg,#071025 0%, #07182b 100%); color:#e6eef6}
    .container{max-width:900px;margin:48px auto;padding:28px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));border-radius:12px;box-shadow:0 8px 30px rgba(2,6,23,0.6)}
    h1{font-size:1.6rem;margin:0 0 8px}
    p.lead{color:var(--muted);margin:0 0 18px}
    section{background:var(--glass);padding:18px;border-radius:10px;margin-top:16px}
    dl{display:grid;grid-template-columns:160px 1fr;gap:8px 18px;align-items:start}
    dt{font-weight:600;color:#cfe3ff}
    dd{margin:0;color:var(--muted)}
    .code{background:#071827;padding:12px;border-radius:8px;font-family:SFMono-Regular,Menlo,monospace;color:#c8e1ff}
    .example{margin-top:12px}
    .footer{margin-top:20px;color:var(--muted);font-size:0.9rem}
    .kbd{background:#051225;padding:3px 8px;border-radius:6px;border:1px solid rgba(255,255,255,0.03)}
    .note{background:rgba(37,99,235,0.08);border-left:3px solid var(--accent);padding:10px;border-radius:6px;color:#cfe3ff}
    @media (max-width:640px){dl{grid-template-columns:1fr}}
  </style>
  <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
  <main class="container">
    <header>
      <h1>🧮 Eigenvalue Calculator — User Guide</h1>
      <p class="lead">How to use the interactive 2×2 Matrix Eigenvalue Calculator (<span class="kbd">eigen_calculator.html</span>) and interpret its results.</p>
    </header>

    <section aria-labelledby="using">
      <h2 id="using">1. Using the Calculator</h2>
      <p>Open <span class="kbd">eigen_calculator.html</span>. The app solves eigenvalues for a 2×2 matrix <em>A</em>:</p>
      <div class="code">\[\mathbf{A} = \begin{pmatrix} a & b \\ c & d \end{pmatrix}\]</div>

      <ol>
        <li><strong>Enter Matrix Values</strong>: Type numerical values for <code>a</code>, <code>b</code>, <code>c</code>, and <code>d</code> into the four input boxes.</li>
        <li><strong>Calculate</strong>: Click the blue <em>Calculate Eigenvalues &amp; Properties</em> button.</li>
        <li><strong>View Results</strong>: The Results section displays the computed properties and eigenvalues beneath the form.</li>
      </ol>
    </section>

    <section aria-labelledby="core">
      <h2 id="core">2. Interpreting the Core Properties</h2>
      <p>The calculator computes three fundamental properties derived from <em>A</em>:</p>
      <dl>
        <dt>Determinant (det)</dt>
        <dd><span class="code">det(A) = ad - bc</span>
            <div class="note" style="margin-top:8px">If <code>det(A) = 0</code>, the matrix is non-invertible (singular) and the linear transformation collapses volume in the plane.</div>
        </dd>

        <dt>Trace (Tr)</dt>
        <dd><span class="code">Tr(A) = a + d</span>
            <div class="note" style="margin-top:8px">Appears in the characteristic polynomial: \(\lambda^2 - \text{Tr}(A)\lambda + \det(A) = 0\).</div>
        </dd>

        <dt>Discriminant (\(\Delta\))</dt>
        <dd><span class="code">\(\Delta = (\text{Tr})^2 - 4\cdot\det\)</span>
            <div class="note" style="margin-top:8px">Determines the nature of the eigenvalues (real distinct, repeated, or complex).</div>
        </dd>
      </dl>
    </section>

    <section aria-labelledby="eigen">
      <h2 id="eigen">3. Understanding the Eigenvalues (\(\lambda\))</h2>
      <p>The eigenvalues are solutions to the characteristic polynomial using the quadratic formula. The solution type depends on the discriminant \(\Delta\):</p>

      <table style="width:100%;border-collapse:collapse;margin-top:8px">
        <thead>
          <tr style="text-align:left;color:#cfe3ff">
            <th style="padding:8px">\(\Delta\)</th>
            <th style="padding:8px">Solution Type</th>
            <th style="padding:8px">Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="padding:8px">\(\Delta > 0\)</td>
            <td style="padding:8px">Two distinct real eigenvalues</td>
            <td style="padding:8px">Stretching/shrinking along two real directions.</td>
          </tr>
          <tr>
            <td style="padding:8px">\(\Delta = 0\)</td>
            <td style="padding:8px">One repeated real eigenvalue</td>
            <td style="padding:8px">A shear or uniform scaling; geometric multiplicity may be 1 or 2 depending on matrix.</td>
          </tr>
          <tr>
            <td style="padding:8px">\(\Delta < 0\)</td>
            <td style="padding:8px">Complex conjugate eigenvalues</td>
            <td style="padding:8px">Rotational behaviour: no real eigenvectors. Values shown as \(x+yi\) and \(x-yi\).</td>
          </tr>
        </tbody>
      </table>

      <p class="example">When complex eigenvalues are returned they will be shown in the form <code>x + yi</code> and <code>x - yi</code>.</p>
    </section>

    <section aria-labelledby="test">
      <h2 id="test">4. Test Case Example</h2>
      <p>Enter the following to confirm a real, distinct solution:</p>
      <div class="code">a = 2 &nbsp;&nbsp; b = 1 &nbsp;&nbsp; c = 1 &nbsp;&nbsp; d = 2</div>

      <p style="margin-top:8px"><strong>Expected Results</strong></p>
      <dl>
        <dt>Determinant</dt>
        <dd>3</dd>
        <dt>Trace</dt>
        <dd>4</dd>
        <dt>Discriminant (\(\Delta\))</dt>
        <dd>8</dd>
        <dt>Eigenvalues</dt>
        <dd>\(\lambda_1 = 3\), \(\lambda_2 = 1\)</dd>
        <dt>Solution Type</dt>
        <dd>Two distinct real eigenvalues (\(\Delta > 0\))</dd>
      </dl>
    </section>

    <section aria-labelledby="notes">
      <h2 id="notes">Notes & Tips</h2>
      <ul>
        <li>Inputs accept decimal numbers and negatives. Avoid leaving fields blank.</li>
        <li>If the calculator shows tiny imaginary parts like <code>1e-16i</code>, treat them as numerical round-off — they are effectively zero.</li>
        <li>For learning, try matrices with known behaviours: rotation matrices (complex eigenvalues), diagonal matrices (eigenvalues = diagonal entries), and singular matrices (<code>det = 0</code>).</li>
      </ul>
    </section>

    <footer class="footer">
      Created for the <strong>2×2 Matrix Eigenvalue Calculator</strong>. Save this file as <span class="kbd">eigen_calculator_user_guide.html</span> or paste into your app's documentation panel.
    </footer>
  </main>
</body>
</html>
