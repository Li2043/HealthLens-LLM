const evalRunBtn = document.getElementById("run-eval-btn");
const evalRunOpenaiBtn = document.getElementById("run-eval-openai-btn");
const evalLoadingEl = document.getElementById("eval-loading");
const evalLoadingTitleEl = document.getElementById("eval-loading-title");
const evalLoadingBodyEl = document.getElementById("eval-loading-body");
const evalErrorEl = document.getElementById("eval-error");
const evalErrorMessageEl = document.getElementById("eval-error-message");
const evalResultsEl = document.getElementById("eval-results");
const evalProviderBannerEl = document.getElementById("eval-provider-banner");
const evalSummaryEl = document.getElementById("eval-summary");
const evalResultsBodyEl = document.getElementById("eval-results-body");
const evalCaseDetailsEl = document.getElementById("eval-case-details");

function showEval(el) {
  el.classList.remove("hidden");
}

function hideEval(el) {
  el.classList.add("hidden");
}

function evalT(key) {
  return window.HealthLens?.t(key) ?? key;
}

function formatPercent(value) {
  return `${Math.round(value * 100)}%`;
}

function setEvalButtonsDisabled(disabled) {
  evalRunBtn.disabled = disabled;
  evalRunOpenaiBtn.disabled = disabled;
}

function renderEvalSummary(summary, provider) {
  const cards = [
    { label: evalT("evalMetricTotal"), value: summary.total_cases },
    { label: evalT("evalMetricPassRate"), value: formatPercent(summary.pass_rate) },
    { label: evalT("evalMetricSafety"), value: formatPercent(summary.safety_pass_rate) },
    { label: evalT("evalMetricRisk"), value: formatPercent(summary.risk_match_rate) },
    { label: evalT("evalMetricLatency"), value: `${summary.average_latency_ms} ms` },
  ];

  evalSummaryEl.innerHTML = cards
    .map(
      (card) => `
        <article class="metric-card">
          <span class="metric-label">${card.label}</span>
          <strong class="metric-value">${card.value}</strong>
        </article>
      `
    )
    .join("");

  evalProviderBannerEl.textContent = evalT("evalProviderResult").replace("{provider}", provider);
  evalProviderBannerEl.classList.toggle("openai", provider === "openai");
  showEval(evalProviderBannerEl);
}

function renderEvalResults(data) {
  evalResultsBodyEl.innerHTML = data.results
    .map((result) => {
      const statusClass = result.pass ? "pass" : "fail";
      const statusLabel = result.pass ? evalT("evalStatusPass") : evalT("evalStatusFail");
      return `
        <tr>
          <td>${result.name}</td>
          <td>${result.category}</td>
          <td>${result.expected_risk_level}</td>
          <td>${result.actual_risk_level ?? "—"}</td>
          <td>${Math.round(result.signal_match_score * 100)}%</td>
          <td>${result.safety_passed ? evalT("evalYes") : evalT("evalNo")}</td>
          <td><span class="status-pill ${statusClass}">${statusLabel}</span></td>
        </tr>
      `;
    })
    .join("");

  evalCaseDetailsEl.innerHTML = data.results
    .map((result) => {
      const traceItems = (result.workflow_trace || [])
        .map(
          (step) =>
            `<li><strong>${step.step}</strong> — ${step.status} (${step.duration_ms} ms)${
              step.note ? `: ${step.note}` : ""
            }</li>`
        )
        .join("");

      return `
        <details class="result-card eval-case-detail">
          <summary>${result.name} · ${result.pass ? evalT("evalStatusPass") : evalT("evalStatusFail")}</summary>
          <p><strong>${evalT("evalDetailsInput")}:</strong> ${escapeHtml(getCaseInput(result.case_id))}</p>
          <p><strong>${evalT("evalDetailsExpectedSignals")}:</strong> ${result.expected_signals.join(", ")}</p>
          <p><strong>${evalT("evalDetailsDetectedSignals")}:</strong> ${result.detected_signals.join(", ") || "—"}</p>
          ${
            result.failure_reason
              ? `<p><strong>${evalT("evalDetailsFailure")}:</strong> ${escapeHtml(result.failure_reason)}</p>`
              : ""
          }
          <p><strong>${evalT("evalDetailsTrace")}:</strong></p>
          <ul class="trace-list">${traceItems}</ul>
        </details>
      `;
    })
    .join("");
}

let cachedCases = null;

async function loadCases() {
  if (cachedCases) return cachedCases;
  const response = await fetch("/evaluation/cases");
  cachedCases = await response.json();
  return cachedCases;
}

function getCaseInput(caseId) {
  const match = cachedCases?.find((item) => item.id === caseId);
  if (!match) return "";
  if (match.id === "long_input_guardrail") {
    return `[${match.input_text.length} characters — truncated for display]`;
  }
  return match.input_text;
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function setLoadingCopy(provider) {
  evalLoadingTitleEl.textContent = evalT("evalLoadingTitle");
  evalLoadingBodyEl.textContent =
    provider === "openai" ? evalT("evalLoadingOpenaiBody") : evalT("evalLoadingBody");
}

async function runEvaluationSuite(provider = "mock") {
  hideEval(evalErrorEl);
  hideEval(evalResultsEl);
  hideEval(evalProviderBannerEl);
  setLoadingCopy(provider);
  showEval(evalLoadingEl);
  setEvalButtonsDisabled(true);

  try {
    await loadCases();
    const response = await fetch(`/evaluation/run?provider=${encodeURIComponent(provider)}`, {
      method: "POST",
    });
    const payload = await response.json();

    if (!response.ok) {
      const message = payload?.error?.message || evalT("evalErrorTitle");
      if (provider === "openai" && payload?.error?.code === "INVALID_PROVIDER") {
        throw new Error(evalT("evalOpenaiUnavailable"));
      }
      throw new Error(message);
    }

    renderEvalSummary(payload.summary, payload.provider);
    renderEvalResults(payload);
    showEval(evalResultsEl);
  } catch (err) {
    evalErrorMessageEl.textContent = err.message || evalT("evalErrorTitle");
    showEval(evalErrorEl);
  } finally {
    hideEval(evalLoadingEl);
    setEvalButtonsDisabled(false);
  }
}

evalRunBtn.addEventListener("click", () => runEvaluationSuite("mock"));
evalRunOpenaiBtn.addEventListener("click", () => runEvaluationSuite("openai"));
