const SAMPLES = {
  low: "My heart rate is 72, blood pressure is 118/76, I feel calm and slept well.",
  moderate: "My heart rate is 100, I can not sleep, I am unhappy.",
  high: "My heart rate is 125, blood pressure is 150/95, I feel anxious and I cannot sleep.",
  bp200: "My blood pressure is 200",
};

const I18N = {
  en: {
    title: "HealthLens-LLM",
    subtitle:
      "Python workflow prototype for LLM-assisted extraction, rule-based checks, and LLM safety testing.",
    notice: "Prototype only. Not medical advice. No personal health data is stored.",
    inputLabel: "Sample health input (demo only)",
    inputPlaceholder: "Try a sample below or enter your own demo text.",
    trySample: "Try a sample:",
    sampleLow: "Low risk",
    sampleModerate: "Moderate risk",
    sampleHigh: "High risk",
    sampleBp200: "Single BP (200)",
    analyseBtn: "Analyse",
    voiceBtn: "Voice input",
    voiceListening: "Listening...",
    voiceUnsupported:
      "Voice input is not supported in this browser. Please type your text instead.",
    voiceErrNoSpeech: "No speech detected. Please try again.",
    voiceErrAudioCapture: "Microphone not available. Please check your audio device.",
    voiceErrNotAllowed: "Microphone permission denied. Please allow access and try again.",
    voiceErrGeneric: "Voice input failed. Please type your text instead.",
    voiceErrUnsupported: "Voice input is not supported in this browser. Please type your text instead.",
    loading: "Analysing...",
    riskSummary: "Risk Summary",
    incompleteWarning: "Some measurements were incomplete or ambiguous.",
    extractionEvidence: "Extraction Evidence",
    llmExplanation: "LLM Explanation",
    safetyCheck: "Safety Check",
    technicalDetails: "Technical Details",
    structuredInput: "Structured Input",
    riskResult: "Risk Result",
    footer: "Software engineering prototype — not a real health risk assessment tool.",
    noFlags: "No rule-based flags detected.",
    detectedSignals: "Detected signals:",
    noEvidence: "No extraction evidence available.",
    notMentioned: "not mentioned",
    source: "Source",
    sourceUnavailable: "Source: not available",
    notePrefix: "Note:",
    riskLevel: { low: "low", moderate: "moderate", high: "high" },
    riskBadge: "{level} risk",
    extractorProvider: "Extractor provider",
    explanationProvider: "Explanation provider",
    dataStorage: "Data storage: none",
    warningPrefix: "Warning:",
    overall: "Overall",
    passed: "Passed",
    failed: "Failed",
    disclaimerIncluded: "Disclaimer included",
    diagnosticLanguage: "Diagnostic language detected",
    medicationAdvice: "Medication advice detected",
    yes: "Yes",
    no: "No",
    errEmptyInput: "Please enter some sample health text or choose a sample button.",
    errGeneric: "Something went wrong. Please try again.",
    errRequestFailed: "Request failed ({status})",
    flags: {
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
    },
    fields: {
      heart_rate: "Heart rate",
      systolic_bp: "Systolic BP",
      diastolic_bp: "Diastolic BP",
      mood: "Mood",
      sleep_quality: "Sleep quality",
    },
    status: {
      absent: "absent",
      partial: "partial",
      complete: "complete",
      ambiguous: "ambiguous",
    },
  },
  zh: {
    title: "HealthLens-LLM",
    subtitle: "Python 工作流原型：LLM 辅助结构化提取、规则引擎检查与 LLM 安全测试。",
    notice: "仅供原型演示，非医疗建议。不存储任何个人健康数据。",
    inputLabel: "示例健康输入（仅供演示）",
    inputPlaceholder: "点击下方样例，或输入你自己的演示文本。",
    trySample: "试试样例：",
    sampleLow: "低风险",
    sampleModerate: "中风险",
    sampleHigh: "高风险",
    sampleBp200: "单项血压 (200)",
    analyseBtn: "分析",
    voiceBtn: "语音输入",
    voiceListening: "正在聆听...",
    voiceUnsupported: "此浏览器不支持语音输入，请改为手动输入。",
    voiceErrNoSpeech: "未检测到语音，请重试。",
    voiceErrAudioCapture: "无法使用麦克风，请检查音频设备。",
    voiceErrNotAllowed: "麦克风权限被拒绝，请允许访问后重试。",
    voiceErrGeneric: "语音输入失败，请改为手动输入。",
    voiceErrUnsupported: "此浏览器不支持语音输入，请改为手动输入。",
    loading: "分析中...",
    riskSummary: "风险摘要",
    incompleteWarning: "部分测量数据不完整或存在歧义。",
    extractionEvidence: "提取依据",
    llmExplanation: "LLM 解释",
    safetyCheck: "安全检查",
    technicalDetails: "技术详情",
    structuredInput: "结构化输入",
    riskResult: "风险结果",
    footer: "软件工程原型 — 非真实健康风险评估工具。",
    noFlags: "未检测到规则标志。",
    detectedSignals: "检测到的信号：",
    noEvidence: "暂无提取依据。",
    notMentioned: "未提及",
    source: "来源",
    sourceUnavailable: "来源：不可用",
    notePrefix: "说明：",
    riskLevel: { low: "低", moderate: "中", high: "高" },
    riskBadge: "{level}风险",
    extractorProvider: "提取提供者",
    explanationProvider: "解释提供者",
    dataStorage: "数据存储：无",
    warningPrefix: "警告：",
    overall: "总体",
    passed: "通过",
    failed: "未通过",
    disclaimerIncluded: "包含免责声明",
    diagnosticLanguage: "检测到诊断性语言",
    medicationAdvice: "检测到用药建议",
    yes: "是",
    no: "否",
    errEmptyInput: "请输入示例健康文本，或选择一个样例按钮。",
    errGeneric: "出现错误，请重试。",
    errRequestFailed: "请求失败 ({status})",
    flags: {
      very_high_systolic_bp: "收缩压非常高",
      very_high_diastolic_bp: "舒张压非常高",
      elevated_blood_pressure: "血压升高",
      very_elevated_heart_rate: "心率明显偏高",
      elevated_heart_rate: "心率偏高",
      borderline_heart_rate: "心率临界偏高",
      anxiety_or_stress_flag: "焦虑或压力",
      low_mood_flag: "情绪低落",
      poor_sleep: "睡眠不佳",
      incomplete_measurement: "测量不完整",
    },
    fields: {
      heart_rate: "心率",
      systolic_bp: "收缩压",
      diastolic_bp: "舒张压",
      mood: "情绪",
      sleep_quality: "睡眠质量",
    },
    status: {
      absent: "未提及",
      partial: "部分",
      complete: "完整",
      ambiguous: "歧义",
    },
  },
};

let currentLang = localStorage.getItem("healthlens-lang") || "en";
let lastResultData = null;

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
const langToggleBtn = document.getElementById("lang-toggle");
const voiceBtn = document.getElementById("voice-btn");
const voiceBtnText = document.getElementById("voice-btn-text");
const voiceUnsupportedEl = document.getElementById("voice-unsupported");
const voiceStatusEl = document.getElementById("voice-status");

let speechRecognition = null;
let isListening = false;
let voiceBaseText = "";

function t(key) {
  const parts = key.split(".");
  let value = I18N[currentLang];
  for (const part of parts) {
    value = value?.[part];
  }
  if (value === undefined) {
    value = I18N.en;
    for (const part of parts) {
      value = value?.[part];
    }
  }
  return value ?? key;
}

function show(el) {
  el.classList.remove("hidden");
}

function hide(el) {
  el.classList.add("hidden");
}

function applyStaticTranslations() {
  document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";
  document.title = t("title");

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });

  langToggleBtn.classList.toggle("zh", currentLang === "zh");
  langToggleBtn.setAttribute("aria-pressed", currentLang === "zh" ? "true" : "false");

  if (!isListening && voiceBtn && !voiceBtn.classList.contains("hidden")) {
    voiceBtnText.textContent = t("voiceBtn");
    voiceBtn.setAttribute("aria-label", t("voiceBtn"));
  }
}

function setVoiceStatus(message, isError = false) {
  if (!message) {
    hide(voiceStatusEl);
    voiceStatusEl.textContent = "";
    voiceStatusEl.classList.remove("error");
    return;
  }
  voiceStatusEl.textContent = message;
  voiceStatusEl.classList.toggle("error", isError);
  show(voiceStatusEl);
}

function setListeningState(listening) {
  isListening = listening;
  voiceBtn.classList.toggle("listening", listening);
  voiceBtn.setAttribute("aria-pressed", listening ? "true" : "false");
  voiceBtnText.textContent = listening ? t("voiceListening") : t("voiceBtn");
  if (listening) {
    setVoiceStatus(t("voiceListening"));
  }
}

function appendTranscriptToTextarea(finalTranscript, interimTranscript = "") {
  const prefix = voiceBaseText ? `${voiceBaseText} ` : "";
  const combined = `${prefix}${finalTranscript}${interimTranscript}`.trim();
  inputEl.value = combined;
}

function handleSpeechError(errorCode) {
  const errorMessages = {
    "no-speech": t("voiceErrNoSpeech"),
    "audio-capture": t("voiceErrAudioCapture"),
    "not-allowed": t("voiceErrNotAllowed"),
  };
  setVoiceStatus(errorMessages[errorCode] || t("voiceErrGeneric"), true);
}

function getSpeechRecognitionLang() {
  return currentLang === "zh" ? "zh-CN" : "en-GB";
}

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    hide(voiceBtn);
    show(voiceUnsupportedEl);
    return;
  }

  hide(voiceUnsupportedEl);
  show(voiceBtn);

  speechRecognition = new SpeechRecognition();
  speechRecognition.lang = getSpeechRecognitionLang();
  speechRecognition.interimResults = true;
  speechRecognition.continuous = false;

  speechRecognition.onstart = () => {
    setListeningState(true);
  };

  speechRecognition.onend = () => {
    setListeningState(false);
    if (!voiceStatusEl.classList.contains("error")) {
      setVoiceStatus("");
    }
  };

  speechRecognition.onerror = (event) => {
    if (event.error === "aborted") {
      return;
    }
    handleSpeechError(event.error);
    setListeningState(false);
  };

  speechRecognition.onresult = (event) => {
    let finalTranscript = "";
    let interimTranscript = "";

    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      const result = event.results[i];
      const transcript = result[0].transcript;
      if (result.isFinal) {
        finalTranscript += transcript;
      } else {
        interimTranscript += transcript;
      }
    }

    if (finalTranscript) {
      voiceBaseText = voiceBaseText
        ? `${voiceBaseText} ${finalTranscript.trim()}`
        : finalTranscript.trim();
    }

    appendTranscriptToTextarea("", interimTranscript);
  };

  voiceBtn.addEventListener("click", () => {
    if (isListening) {
      speechRecognition.stop();
      return;
    }

    hide(errorEl);
    voiceBaseText = inputEl.value.trim();
    speechRecognition.lang = getSpeechRecognitionLang();
    setVoiceStatus("");

    try {
      speechRecognition.start();
    } catch (err) {
      setVoiceStatus(t("voiceErrUnsupported"), true);
    }
  });
}

function setLanguage(lang) {
  if (lang !== "en" && lang !== "zh") return;
  currentLang = lang;
  localStorage.setItem("healthlens-lang", lang);
  applyStaticTranslations();
  if (lastResultData) {
    renderResults(lastResultData);
  }
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
    return `<p class='summary-text'>${t("noFlags")}</p>`;
  }
  const items = flags
    .map((flag) => `<li>${t(`flags.${flag}`) || flag.replaceAll("_", " ")}</li>`)
    .join("");
  return `<p class='summary-text'><strong>${t("detectedSignals")}</strong></p><ul class='flag-list'>${items}</ul>`;
}

function renderExtractionEvidence(evidence) {
  if (!evidence || evidence.length === 0) {
    extractionEvidenceEl.innerHTML = `<li>${t("noEvidence")}</li>`;
    return;
  }

  extractionEvidenceEl.innerHTML = evidence
    .map((item) => {
      const label = t(`fields.${item.field}`) || item.field;
      const valueText = item.status === "absent" ? t("notMentioned") : item.value ?? t("notMentioned");
      const statusText = t(`status.${item.status}`) || item.status;
      const evidenceText = item.evidence
        ? `${t("source")}: "${item.evidence}"`
        : t("sourceUnavailable");
      return `<li><span class="evidence-field">${label}:</span> ${valueText}. <span class="evidence-status">(${statusText}) ${evidenceText}</span></li>`;
    })
    .join("");
}

function renderProviderStatus(data) {
  const lines = [
    `${t("extractorProvider")}: ${data.extractor_provider}`,
    `${t("explanationProvider")}: ${data.llm_provider}`,
    t("dataStorage"),
  ];
  if (data.provider_warning) {
    lines.push(`${t("warningPrefix")} ${data.provider_warning}`);
  }
  providerStatusEl.innerHTML = lines.map((line) => `<div>${line}</div>`).join("");
}

function renderSafetyCheck(safety) {
  const items = [
    {
      label: t("overall"),
      pass: safety.passed,
      text: safety.passed ? t("passed") : t("failed"),
    },
    {
      label: t("disclaimerIncluded"),
      pass: safety.contains_disclaimer,
      text: safety.contains_disclaimer ? t("yes") : t("no"),
    },
    {
      label: t("diagnosticLanguage"),
      pass: !safety.contains_diagnostic_language,
      text: safety.contains_diagnostic_language ? t("yes") : t("no"),
    },
    {
      label: t("medicationAdvice"),
      pass: !safety.contains_medication_advice,
      text: safety.contains_medication_advice ? t("yes") : t("no"),
    },
  ];

  safetyCheckListEl.innerHTML = items
    .map((item) => `<li class="${item.pass ? "pass" : "fail"}">${item.label}: ${item.text}</li>`)
    .join("");
}

function renderResults(data) {
  lastResultData = data;
  const { structured_input, risk_result, explanation, safety_check } = data;

  renderProviderStatus(data);

  const levelLabel = t(`riskLevel.${risk_result.risk_level}`);
  riskLevelBadgeEl.textContent = t("riskBadge").replace("{level}", levelLabel);
  riskLevelBadgeEl.className = `risk-badge ${risk_result.risk_level}`;

  if (structured_input.missing_or_ambiguous_fields?.length) {
    show(incompleteWarningEl);
  } else {
    hide(incompleteWarningEl);
  }

  detectedSignalsEl.innerHTML = formatFlagList(risk_result.flags);
  renderExtractionEvidence(structured_input.extraction_evidence);

  if (structured_input.extraction_notes) {
    extractionNoteEl.textContent = `${t("notePrefix")} ${structured_input.extraction_notes}`;
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
    showError(t("errEmptyInput"));
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
      throw new Error(detail || t("errRequestFailed").replace("{status}", response.status));
    }

    renderResults(await response.json());
    show(resultsEl);
  } catch (err) {
    showError(err.message || t("errGeneric"));
  } finally {
    hide(loadingEl);
    analyseBtn.disabled = false;
  }
}

document.querySelectorAll(".sample-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    inputEl.value = SAMPLES[btn.dataset.sample] || "";
    hide(errorEl);
  });
});

function toggleLanguage() {
  setLanguage(currentLang === "en" ? "zh" : "en");
}

langToggleBtn.addEventListener("click", toggleLanguage);
analyseBtn.addEventListener("click", analyse);

applyStaticTranslations();
initSpeechRecognition();
