const SAMPLES = {
  en: {
    low: "My heart rate is 72, blood pressure is 118/76, I feel calm and slept well.",
    moderate: "My heart rate is 100, I can not sleep, I am unhappy.",
    high: "My heart rate is 125, blood pressure is 150/95, I feel anxious and I cannot sleep.",
  },
  zh: {
    low: "我的心率是72，血压是118/76，我感觉很平静，睡眠很好。",
    moderate: "我的心率是100，我睡不着，心情不好。",
    high: "我的心率是125，血压是150/95，我感到焦虑，而且睡不着。",
  },
};

function getSampleText(sampleKey) {
  return SAMPLES[currentLang]?.[sampleKey] ?? SAMPLES.en[sampleKey] ?? "";
}

const I18N = {
  en: {
    title: "HealthLens-LLM",
    eyebrow: "Health signal checker",
    subtitle: "AI-assisted health text signal checker",
    heroDescription:
      "Paste a short health-related note to extract signals such as heart rate, blood pressure, sleep, and mood. The app combines rule-based checks with a safe LLM-generated explanation.",
    notice:
      "This tool is a software demonstration only. It is not medical advice, diagnosis, or treatment guidance. If symptoms are severe, urgent, or worsening, seek professional medical help.",
    howToUse: "How to use",
    step1Title: "Enter a short health note",
    step1Body: "Example: “My heart rate is 100 and I can’t sleep.”",
    step2Title: "Click Analyse",
    step2Body: "The app extracts health-related signals and applies rule-based checks.",
    step3Title: "Review the result",
    step3Body: "See the risk summary, detected signals, evidence, and safety-conscious explanation.",
    inputLabel: "Describe your health note",
    inputHelper: "Use short, plain language. Do not enter real personal medical information.",
    inputPlaceholder: "Describe how you feel, your sleep, heart rate, or blood pressure in a few sentences.",
    trySample: "Try an example:",
    sampleLow: "Mild symptoms",
    sampleModerate: "Sleep and mood",
    sampleHigh: "Higher-risk example",
    analyseBtn: "Analyse note",
    clearBtn: "Clear",
    voiceBtn: "Voice input",
    voiceListening: "Listening...",
    voiceUnsupported:
      "Voice input is not supported in this browser. Please type your text instead.",
    voiceErrNoSpeech: "No speech detected. Please try again.",
    voiceErrAudioCapture: "Microphone not available. Please check your audio device.",
    voiceErrNotAllowed: "Microphone permission denied. Please allow access and try again.",
    voiceErrGeneric: "Voice input failed. Please type your text instead.",
    voiceErrUnsupported: "Voice input is not supported in this browser. Please type your text instead.",
    emptyTitle: "Your analysis will appear here.",
    emptyBody: "Try an example or enter your own note to begin.",
    loadingTitle: "Analysing your note…",
    loadingBody: "Extracting signals and generating a safe explanation.",
    errorTitle: "Analysis is temporarily unavailable.",
    errorBody: "Please try again later.",
    resultSummary: "Result summary",
    summaryTemplate: "The note suggests a {level} level of concern based on extracted health signals.",
    detectedSignalsTitle: "Detected signals",
    noSignalValues: "No structured signal values were extracted from this note.",
    llmExplanation: "Explanation",
    extractionEvidence: "Evidence",
    safetyGuardrails: "Safety guardrails",
    safetyGuardrailsText:
      "This response avoids diagnosis, medication instructions, and treatment advice.",
    technicalDetails: "Technical details for reviewers",
    systemInfo: "System information",
    ruleEngineNotes: "Rule engine notes",
    safetyCheck: "Safety validation",
    structuredInput: "Structured input",
    riskResult: "Risk result",
    footer: "Built as a software engineering portfolio demo — not a clinical product.",
    noFlags: "No additional rule-based flags were detected.",
    detectedFlags: "Rule-based flags:",
    noEvidence: "No extraction evidence available.",
    notMentioned: "Not mentioned",
    source: "Source",
    sourceUnavailable: "Source unavailable",
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
    errEmptyInput: "Please enter a short health note or choose an example.",
    errGeneric: "Analysis is temporarily unavailable. Please try again later.",
    errRequestFailed: "Analysis is temporarily unavailable. Please try again later.",
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
    values: {
      mood: {
        anxious: "Anxious",
        stressed: "Stressed",
        low: "Low",
        calm: "Calm",
        unknown: "Unknown",
      },
      sleep_quality: {
        good: "Good",
        poor: "Poor",
        unknown: "Unknown",
      },
    },
    incompleteWarning: "Some measurements were incomplete or ambiguous.",
    tabAnalyse: "Analyse",
    tabEvaluation: "Evaluation Lab",
    evalTitle: "Evaluation Lab",
    evalDescription:
      "Run a curated evaluation suite to test risk classification, signal extraction, safety guardrails, latency, and failure handling.",
    evalRunBtn: "Run evaluation (mock)",
    evalRunOpenaiBtn: "Run evaluation (OpenAI)",
    evalMockNote: "Mock mode is free, deterministic, and recommended for regression testing.",
    evalOpenaiWarning:
      "OpenAI mode calls the live API for extraction and explanation. It may use tokens and can produce different results from mock mode.",
    evalLoadingTitle: "Running evaluation suite…",
    evalLoadingBody: "Executing curated cases against the mock provider workflow.",
    evalLoadingOpenaiBody: "Executing curated cases with live OpenAI extraction and explanation.",
    evalOpenaiUnavailable: "OpenAI evaluation is not available. Configure OPENAI_API_KEY on the server first.",
    evalProviderResult: "Provider used: {provider}",
    evalErrorTitle: "Evaluation could not be completed.",
    evalResultsTitle: "Case results",
    evalColCase: "Case",
    evalColCategory: "Category",
    evalColExpected: "Expected",
    evalColActual: "Actual",
    evalColSignals: "Signals",
    evalColSafety: "Safety",
    evalColStatus: "Status",
    evalMetricTotal: "Total cases",
    evalMetricPassRate: "Pass rate",
    evalMetricSafety: "Safety pass rate",
    evalMetricRisk: "Risk match rate",
    evalMetricLatency: "Avg latency",
    evalStatusPass: "Pass",
    evalStatusFail: "Fail",
    evalDetailsInput: "Input",
    evalDetailsExpectedSignals: "Expected signals",
    evalDetailsDetectedSignals: "Detected signals",
    evalDetailsFailure: "Failure reason",
    evalDetailsTrace: "Workflow trace",
    evalYes: "Yes",
    evalNo: "No",
  },
  zh: {
    title: "HealthLens-LLM",
    eyebrow: "健康信号检查",
    subtitle: "AI 辅助健康文本信号检查器",
    heroDescription:
      "输入一段简短的健康相关描述，系统会提取心率、血压、睡眠、情绪等信号，并结合规则检查和安全解释生成结果。",
    notice:
      "本工具仅用于软件演示，不构成医疗建议、诊断或治疗指导。如果症状严重、紧急或持续恶化，请寻求专业医疗帮助。",
    howToUse: "如何使用",
    step1Title: "输入简短描述",
    step1Body: "示例：“我的心率是 100，而且睡不着。”",
    step2Title: "点击分析",
    step2Body: "系统会提取健康相关信号并应用规则检查。",
    step3Title: "查看结果",
    step3Body: "查看风险摘要、检测到的信号、依据和安全解释。",
    inputLabel: "描述你的健康文本",
    inputHelper: "请使用简短、清楚的语言。不要输入真实的个人医疗隐私信息。",
    inputPlaceholder: "用几句话描述你的感受、睡眠、心率或血压等情况。",
    trySample: "试试示例：",
    sampleLow: "轻度症状",
    sampleModerate: "睡眠与情绪",
    sampleHigh: "较高风险示例",
    analyseBtn: "分析文本",
    clearBtn: "清空",
    voiceBtn: "语音输入",
    voiceListening: "正在聆听...",
    voiceUnsupported: "此浏览器不支持语音输入，请改为手动输入。",
    voiceErrNoSpeech: "未检测到语音，请重试。",
    voiceErrAudioCapture: "无法使用麦克风，请检查音频设备。",
    voiceErrNotAllowed: "麦克风权限被拒绝，请允许访问后重试。",
    voiceErrGeneric: "语音输入失败，请改为手动输入。",
    voiceErrUnsupported: "此浏览器不支持语音输入，请改为手动输入。",
    emptyTitle: "分析结果将显示在这里。",
    emptyBody: "试试示例，或输入你自己的描述开始。",
    loadingTitle: "正在分析你的文本…",
    loadingBody: "正在提取信号并生成安全解释。",
    errorTitle: "分析暂时不可用。",
    errorBody: "请稍后再试。",
    resultSummary: "结果摘要",
    summaryTemplate: "根据提取到的健康信号，这条记录显示为{level}关注级别。",
    detectedSignalsTitle: "检测到的信号",
    noSignalValues: "未能从这条记录中提取结构化信号。",
    llmExplanation: "解释",
    extractionEvidence: "依据",
    safetyGuardrails: "安全边界",
    safetyGuardrailsText: "本回复避免诊断、用药说明和治疗建议。",
    technicalDetails: "给评审者的技术细节",
    systemInfo: "系统信息",
    ruleEngineNotes: "规则引擎说明",
    safetyCheck: "安全验证",
    structuredInput: "结构化输入",
    riskResult: "风险结果",
    footer: "软件工程作品集演示 — 非临床产品。",
    noFlags: "未检测到额外的规则标志。",
    detectedFlags: "规则标志：",
    noEvidence: "暂无提取依据。",
    notMentioned: "未提及",
    source: "来源",
    sourceUnavailable: "来源不可用",
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
    errEmptyInput: "请输入一段简短健康描述，或选择一个示例。",
    errGeneric: "分析暂时不可用，请稍后再试。",
    errRequestFailed: "分析暂时不可用，请稍后再试。",
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
    values: {
      mood: {
        anxious: "焦虑",
        stressed: "压力",
        low: "低落",
        calm: "平静",
        unknown: "未知",
      },
      sleep_quality: {
        good: "良好",
        poor: "不佳",
        unknown: "未知",
      },
    },
    incompleteWarning: "部分测量数据不完整或存在歧义。",
    tabAnalyse: "分析",
    tabEvaluation: "评估实验室",
    evalTitle: "评估实验室",
    evalDescription:
      "运行精选评估用例，测试风险分类、信号提取、安全边界、延迟和失败处理。",
    evalRunBtn: "运行评估（mock）",
    evalRunOpenaiBtn: "运行评估（OpenAI）",
    evalMockNote: "Mock 模式免费、结果稳定，适合回归测试。",
    evalOpenaiWarning:
      "OpenAI 模式会调用真实 API 进行提取和解释，可能消耗 token，且结果可能与 mock 模式不同。",
    evalLoadingTitle: "正在运行评估套件…",
    evalLoadingBody: "正在使用 mock 提供者工作流执行精选用例。",
    evalLoadingOpenaiBody: "正在使用 OpenAI 实时提取与解释执行精选用例。",
    evalOpenaiUnavailable: "OpenAI 评估不可用。请先在服务器配置 OPENAI_API_KEY。",
    evalProviderResult: "使用的提供者：{provider}",
    evalErrorTitle: "评估无法完成。",
    evalResultsTitle: "用例结果",
    evalColCase: "用例",
    evalColCategory: "类别",
    evalColExpected: "期望",
    evalColActual: "实际",
    evalColSignals: "信号得分",
    evalColSafety: "安全",
    evalColStatus: "状态",
    evalMetricTotal: "总用例数",
    evalMetricPassRate: "通过率",
    evalMetricSafety: "安全通过率",
    evalMetricRisk: "风险匹配率",
    evalMetricLatency: "平均延迟",
    evalStatusPass: "通过",
    evalStatusFail: "失败",
    evalDetailsInput: "输入",
    evalDetailsExpectedSignals: "期望信号",
    evalDetailsDetectedSignals: "检测到的信号",
    evalDetailsFailure: "失败原因",
    evalDetailsTrace: "工作流追踪",
    evalYes: "是",
    evalNo: "否",
  },
};

let currentLang = localStorage.getItem("healthlens-lang") || "en";
let lastResultData = null;

const inputEl = document.getElementById("health-input");
const analyseBtn = document.getElementById("analyse-btn");
const clearBtn = document.getElementById("clear-btn");
const loadingEl = document.getElementById("loading");
const errorEl = document.getElementById("error");
const errorMessageEl = document.getElementById("error-message");
const emptyStateEl = document.getElementById("empty-state");
const resultsEl = document.getElementById("results");
const providerStatusEl = document.getElementById("provider-status");
const riskLevelBadgeEl = document.getElementById("risk-level-badge");
const resultSummaryEl = document.getElementById("result-summary");
const incompleteWarningEl = document.getElementById("incomplete-warning");
const signalMetricsEl = document.getElementById("signal-metrics");
const detectedSignalsFlagsEl = document.getElementById("detected-signals-flags");
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

window.HealthLens = {
  t,
  get currentLang() {
    return currentLang;
  },
};

function initAppTabs() {
  const tabs = document.querySelectorAll(".app-tab");
  const panels = {
    analyse: document.getElementById("panel-analyse"),
    evaluation: document.getElementById("panel-evaluation"),
  };

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;
      tabs.forEach((item) => item.classList.toggle("is-active", item === tab));
      Object.entries(panels).forEach(([name, panel]) => {
        panel.classList.toggle("hidden", name !== target);
      });
    });
  });
}

function show(el) {
  el.classList.remove("hidden");
}

function hide(el) {
  el.classList.add("hidden");
}

function showEmptyState() {
  hide(resultsEl);
  hide(loadingEl);
  hide(errorEl);
  show(emptyStateEl);
}

function applyStaticTranslations() {
  document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";
  document.title = t("title");

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    if (el.id === "error-message" && errorEl && !errorEl.classList.contains("hidden")) {
      return;
    }
    el.textContent = t(el.dataset.i18n);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });

  langToggleBtn.classList.toggle("zh", currentLang === "zh");
  langToggleBtn.setAttribute("aria-pressed", currentLang === "zh" ? "true" : "false");

  langToggleBtn.querySelectorAll(".lang-toggle-option").forEach((option) => {
    option.classList.toggle("is-active", option.dataset.lang === currentLang);
  });

  if (!isListening && voiceBtn && !voiceBtn.classList.contains("hidden")) {
    voiceBtnText.textContent = t("voiceBtn");
    voiceBtn.setAttribute("aria-label", t("voiceBtn"));
  }

  if (lastResultData) {
    renderResults(lastResultData);
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
  inputEl.value = `${prefix}${finalTranscript}${interimTranscript}`.trim();
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

  speechRecognition.onstart = () => setListeningState(true);

  speechRecognition.onend = () => {
    setListeningState(false);
    if (!voiceStatusEl.classList.contains("error")) {
      setVoiceStatus("");
    }
  };

  speechRecognition.onerror = (event) => {
    if (event.error === "aborted") return;
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
  if (inputEl.value.trim() && lastResultData) {
    analyse();
  }
}

function parseErrorMessage(rawText) {
  if (!rawText) return t("errGeneric");
  try {
    const payload = JSON.parse(rawText);
    if (payload?.error?.message) return payload.error.message;
  } catch (err) {
    // Ignore non-JSON error bodies.
  }
  return t("errGeneric");
}

function showError(message) {
  errorMessageEl.textContent = message || t("errorBody");
  hide(emptyStateEl);
  hide(resultsEl);
  show(errorEl);
}

function clearInput() {
  inputEl.value = "";
  lastResultData = null;
  hide(errorEl);
  hide(resultsEl);
  showEmptyState();
}

function stripMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/`(.*?)`/g, "$1")
    .replace(/^#+\s*/gm, "")
    .trim();
}

function formatFieldValue(field, value, status) {
  if (status === "absent" || value == null || value === "") {
    return t("notMentioned");
  }
  const translated = t(`values.${field}.${value}`);
  if (translated !== `values.${field}.${value}`) {
    return translated;
  }
  return value;
}

function formatMetric(label, value) {
  return `<li><span class="signal-label">${label}</span><span class="signal-value">${value}</span></li>`;
}

function renderSignalMetrics(structured) {
  const metrics = [];

  if (structured.heart_rate != null) {
    metrics.push(
      formatMetric(
        t("fields.heart_rate"),
        currentLang === "zh"
          ? `${structured.heart_rate} 次/分`
          : `${structured.heart_rate} bpm`
      )
    );
  }

  if (structured.systolic_bp != null && structured.diastolic_bp != null) {
    metrics.push(
      formatMetric(
        t("fields.systolic_bp"),
        `${structured.systolic_bp}/${structured.diastolic_bp}`
      )
    );
  } else if (structured.systolic_bp != null) {
    metrics.push(formatMetric(t("fields.systolic_bp"), String(structured.systolic_bp)));
  }

  if (structured.mood) {
    metrics.push(formatMetric(t("fields.mood"), formatFieldValue("mood", structured.mood, "complete")));
  }

  if (structured.sleep_quality) {
    metrics.push(
      formatMetric(
        t("fields.sleep_quality"),
        formatFieldValue("sleep_quality", structured.sleep_quality, "complete")
      )
    );
  }

  if (metrics.length === 0) {
    signalMetricsEl.innerHTML = `<li class="signal-empty">${t("noSignalValues")}</li>`;
    return;
  }

  signalMetricsEl.innerHTML = metrics.join("");
}

function renderFlagList(flags) {
  if (!flags || flags.length === 0) {
    detectedSignalsFlagsEl.innerHTML = `<p class="summary-text muted">${t("noFlags")}</p>`;
    return;
  }

  const items = flags
    .map((flag) => `<li>${t(`flags.${flag}`) || flag.replaceAll("_", " ")}</li>`)
    .join("");

  detectedSignalsFlagsEl.innerHTML = `<p class="summary-text"><strong>${t("detectedFlags")}</strong></p><ul class="flag-list">${items}</ul>`;
}

function renderExtractionEvidence(evidence) {
  if (!evidence || evidence.length === 0) {
    extractionEvidenceEl.innerHTML = `<li>${t("noEvidence")}</li>`;
    return;
  }

  extractionEvidenceEl.innerHTML = evidence
    .map((item) => {
      const label = t(`fields.${item.field}`) || item.field;
      const valueText = formatFieldValue(item.field, item.value, item.status);
      const statusText = t(`status.${item.status}`) || item.status;
      const evidenceText = item.evidence
        ? `${t("source")}: "${item.evidence}"`
        : t("sourceUnavailable");
      return `<li><span class="evidence-field">${label}:</span> ${valueText} <span class="evidence-status">(${statusText}) ${evidenceText}</span></li>`;
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
  resultSummaryEl.textContent = t("summaryTemplate").replace("{level}", levelLabel);

  if (structured_input.missing_or_ambiguous_fields?.length) {
    show(incompleteWarningEl);
  } else {
    hide(incompleteWarningEl);
  }

  renderSignalMetrics(structured_input);
  renderFlagList(risk_result.flags);
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
    return;
  }

  hide(errorEl);
  hide(resultsEl);
  hide(emptyStateEl);
  show(loadingEl);
  analyseBtn.disabled = true;
  clearBtn.disabled = true;

  try {
    const response = await fetch("/analyse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, language: currentLang }),
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(parseErrorMessage(detail));
    }

    renderResults(await response.json());
    hide(emptyStateEl);
    show(resultsEl);
  } catch (err) {
    showError(err.message || t("errGeneric"));
  } finally {
    hide(loadingEl);
    analyseBtn.disabled = false;
    clearBtn.disabled = false;
    if (!lastResultData && errorEl.classList.contains("hidden")) {
      showEmptyState();
    }
  }
}

document.querySelectorAll(".sample-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    inputEl.value = getSampleText(btn.dataset.sample);
    hide(errorEl);
  });
});

function toggleLanguage() {
  setLanguage(currentLang === "en" ? "zh" : "en");
}

langToggleBtn.addEventListener("click", toggleLanguage);
analyseBtn.addEventListener("click", analyse);
clearBtn.addEventListener("click", clearInput);

applyStaticTranslations();
initSpeechRecognition();
initAppTabs();
showEmptyState();
