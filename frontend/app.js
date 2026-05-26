const SAMPLES = {
  low: "My heart rate is 72, blood pressure is 118/76, I feel calm and slept well.",
  moderate: "My heart rate is 100, I can not sleep, I am unhappy.",
  high: "My heart rate is 125, blood pressure is 150/95, I feel anxious and I cannot sleep.",
  bp200: "My blood pressure is 200",
};

const FLAG_LABELS = {
  very_high_systolic_bp: "Very high systolic blood pressure",
  very_high_diastolic_bp: "Very high diastolic blood pressure",
  elevated_blood_pressure: "Elevated blood pressure",
  very_elevated_heart_rate: "Very elevated heart rate",
  elevated_heart_rate: "Elevated heart rate",
  borderline_heart_rate: "Borderline heart rate",
  anxiety_or_stress_flag: "Anxiety or stress",
  low_mood_flag: "Low mood",
  poor_sleep: "Poor sleep",
  incomplete_measurement: "Incomplete measurement",
};

const FIELD_LABELS = {
  heart_rate: "Heart rate",
  systolic_bp: "Systolic BP",
  diastolic_bp: "Diastolic BP",
  mood: "Mood",
  sleep_quality: "Sleep quality",
};

const inputEl = document.getElementById("health-input");
const analyseBtn = document.getElementById("analyse-btn");
const loadingEl = document.getElementById("loading");
const errorEl = document.getElementById("error");
const resultsEl = document.getElementById("results");
const providerStatusEl = document.getElementById("provider-status");
const riskLevelBadgeEl = document.getElementById("risk-level-badge");
const incompleteWarningEl = document.getElementById("incomplete-warning");
const detectedSignalsEl = document.getElementById("detected-signals");
const extractionNoteEl = document.getElementById("extraction-note");
const extractionEvidenceEl = document.getElementById("extraction-evidence");
const ruleExplanationEl = document.getElementById("rule-explanation");
const explanationEl = document.getElementById("explanation");
const safetyCheckListEl = document.getElementById("safety-check-list");
const structuredInputEl = document.getElementById("structured-input");
const riskResultEl = document.getElementById("risk-result");

function show(el) {
  el.classList.remove("hidden");
}

function hide(el) {
  el.classList.add("hidden");
}

function showError(message) {
  errorEl.textContent = message;
  show(errorEl);
}

function stripMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/`(.*?)`/g, "$1")
    .replace(/^#+\s*/gm, "")
    .trim();
}

function formatFlagList(flags) {
  if (!flags || flags.length === 0) {
    return "<p class='summary-text'>No rule-based flags detected.</p>";
  }
  const items = flags
    .map((flag) => `<li>${FLAG_LABELS[flag] || flag.replaceAll("_", " ")}</li>`)
    .join("");
  return `<p class='summary-text'><strong>Detected signals:</strong></p><ul class='flag-list'>${items}</ul>`;
}

function renderExtractionEvidence(evidence) {
  if (!evidence || evidence.length === 0) {
    extractionEvidenceEl.innerHTML = "<li>No extraction evidence available.</li>";
    return;
  }

  extractionEvidenceEl.innerHTML = evidence
    .map((item) => {
      const label = FIELD_LABELS[item.field] || item.field;
      const valueText =
        item.status === "absent"
          ? "not mentioned"
          : item.value ?? "not mentioned";
      const evidenceText = item.evidence ? `Source: "${item.evidence}"` : "Source: not available";
      return `<li><span class="evidence-field">${label}:</span> ${valueText}. <span class="evidence-status">(${item.status}) ${evidenceText}</span></li>`;
    })
    .join("");
}

function renderProviderStatus(data) {
  const lines = [
    `Extractor provider: ${data.extractor_provider}`,
    `Explanation provider: ${data.llm_provider}`,
    "Data storage: none",
  ];
  if (data.provider_warning) {
    lines.push(`Warning: ${data.provider_warning}`);
  }
  providerStatusEl.innerHTML = lines.map((line) => `<div>${line}</div>`).join("");
}

function renderSafetyCheck(safety) {
  const items = [
    {
      label: "Overall",
      pass: safety.passed,
      text: safety.passed ? "Passed" : "Failed",
    },
    {
      label: "Disclaimer included",
      pass: safety.contains_disclaimer,
      text: safety.contains_disclaimer ? "Yes" : "No",
    },
    {
      label: "Diagnostic language detected",
      pass: !safety.contains_diagnostic_language,
      text: safety.contains_diagnostic_language ? "Yes" : "No",
    },
    {
      label: "Medication advice detected",
      pass: !safety.contains_medication_advice,
      text: safety.contains_medication_advice ? "Yes" : "No",
    },
  ];

  safetyCheckListEl.innerHTML = items
    .map((item) => `<li class="${item.pass ? "pass" : "fail"}">${item.label}: ${item.text}</li>`)
    .join("");
}

function renderResults(data) {
  const { structured_input, risk_result, explanation, safety_check } = data;

  renderProviderStatus(data);

  riskLevelBadgeEl.textContent = `${risk_result.risk_level} risk`;
  riskLevelBadgeEl.className = `risk-badge ${risk_result.risk_level}`;

  if (structured_input.missing_or_ambiguous_fields?.length) {
    show(incompleteWarningEl);
  } else {
    hide(incompleteWarningEl);
  }

  detectedSignalsEl.innerHTML = formatFlagList(risk_result.flags);
  renderExtractionEvidence(structured_input.extraction_evidence);

  if (structured_input.extraction_notes) {
    extractionNoteEl.textContent = `Note: ${structured_input.extraction_notes}`;
    show(extractionNoteEl);
  } else {
    extractionNoteEl.textContent = "";
    hide(extractionNoteEl);
  }

  ruleExplanationEl.textContent = risk_result.rule_explanation;
  explanationEl.textContent = stripMarkdown(explanation);
  renderSafetyCheck(safety_check);

  structuredInputEl.textContent = JSON.stringify(structured_input, null, 2);
  riskResultEl.textContent = JSON.stringify(risk_result, null, 2);
}

async function analyse() {
  const text = inputEl.value.trim();
  if (!text) {
    showError("Please enter some sample health text or choose a sample button.");
    hide(resultsEl);
    return;
  }

  hide(errorEl);
  hide(resultsEl);
  show(loadingEl);
  analyseBtn.disabled = true;

  try {
    const response = await fetch("/analyse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `Request failed (${response.status})`);
    }

    renderResults(await response.json());
    show(resultsEl);
  } catch (err) {
    showError(err.message || "Something went wrong. Please try again.");
  } finally {
    hide(loadingEl);
    analyseBtn.disabled = false;
  }
}

document.querySelectorAll(".sample-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const key = btn.dataset.sample;
    inputEl.value = SAMPLES[key] || "";
    hide(errorEl);
  });
});

analyseBtn.addEventListener("click", analyse);
