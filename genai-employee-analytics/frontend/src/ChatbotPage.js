import { useEffect, useRef, useState } from "react";

import "./App.css";

const API_BASE =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const PIE_COLORS = [
  "#38bdf8",
  "#f97316",
  "#22c55e",
  "#a855f7",
  "#facc15",
  "#06b6d4",
  "#ef4444",
];

const PRESET_SECTIONS = [
  {
    title: "Section 1: Employee Performance & Skill Analytics",
    buttons: [
      { label: "Performance Insights (AI)", query: "Analyze differences between high-performing and low-performing employees." },
      { label: "Skill Importance Model (AI)", query: "Analyze the importance of different skills in determining employee performance." },
      { label: "Skill vs Project Mismatch (AI)", query: "Find cases where highly skilled employees are associated with failed projects." },
      { label: "High Performance Low Leadership (AI)", query: "Identify employees with high performance but low leadership potential." },
      { label: "Advanced Ideal Employee (AI)", query: "Define an ideal employee profile based on top composite skill scores." },
    ],
  },
  {
    title: "Section 2: Training, Mentorship & Development",
    buttons: [
      { label: "Training Analysis (AI)", query: "Analyze how training impacts employee performance and promotions." },
      { label: "Training Correlation (AI)", query: "Show correlation between training hours, performance, and promotions." },
      { label: "Mentorship Analysis (AI)", query: "Analyze mentorship impact on performance and conversion." },
      { label: "Training Programs (AI)", query: "Compare training programs and their impact on performance and growth." },
      { label: "Training Gap (AI)", query: "Identify employees with high training hours but low performance improvement." },
      { label: "Training Recommendation (AI)", query: "Recommend who should receive advanced training and why." },
    ],
  },
  {
    title: "Section 3: Behavioral & Soft Skills Intelligence",
    buttons: [
      { label: "Soft Skills Analysis (AI)", query: "Analyze soft skill patterns and clusters among employees." },
      { label: "Soft Skill Clusters (AI)", query: "Cluster employees by leadership, teamwork, adaptability, and creativity." },
      { label: "Conflict vs Teamwork (AI)", query: "Find employees with high conflict resolution but low teamwork." },
      { label: "Engagement vs Satisfaction (AI)", query: "Analyze how engagement impacts satisfaction and retention." },
      { label: "Initiative vs Innovation (AI)", query: "Identify employees with high initiative but low innovation." },
    ],
  },
  {
    title: "Section 4: Project & Work Performance Analysis",
    buttons: [
      { label: "Project Analysis (AI)", query: "Analyze project success patterns based on complexity and roles." },
      { label: "Project Complexity & Size (AI)", query: "Analyze how project complexity and size influence outcomes." },
      { label: "Project Success vs Failure (AI)", query: "Compare patterns between successful and failed projects." },
      { label: "Project Success Model (AI)", query: "Derive a reasoning-based model for project success." },
      { label: "Project Role Comparison (AI)", query: "Compare performance across different project roles." },
    ],
  },
  {
    title: "Section 5: Attrition & Retention Intelligence",
    buttons: [
      { label: "Attrition Insights (AI)", query: "Analyze employees at risk of leaving the organization." },
      { label: "Attrition Risk Score (AI)", query: "Identify employees at high risk of resignation and key drivers." },
      { label: "Resignation Analysis (AI)", query: "Analyze factors contributing to employee resignation." },
      { label: "Work-Life vs Retention (AI)", query: "Compare work-life balance, engagement, and overtime by retention status." },
    ],
  },
  {
    title: "Section 6: Compensation & Benefits Analysis",
    buttons: [
      { label: "Compensation Analysis (AI)", query: "Analyze compensation fairness and performance relationship." },
      { label: "Compensation + Bonus Analysis (AI)", query: "Analyze relationships between salary increase, bonus, and performance." },
      { label: "Underpaid Insights (AI)", query: "Find employees who may be underpaid based on performance and salary growth." },
      { label: "Benefits Impact (AI)", query: "Analyze how benefits influence satisfaction and retention." },
    ],
  },
  {
    title: "Section 7: Recruitment & Hiring Effectiveness",
    buttons: [
      { label: "Hiring Analysis (AI)", query: "Analyze effectiveness of hiring sources and recruitment process." },
      { label: "Hiring Intelligence (AI)", query: "Analyze hiring sources by time, cost, performance, retention, and satisfaction." },
    ],
  },
];

function formatInsight(text) {
  const renderBold = (content) => {
    const parts = content.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
    return parts.map((part, idx) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={`bold-${idx}`}>{part.slice(2, -2)}</strong>;
      }
      return <span key={`text-${idx}`}>{part}</span>;
    });
  };

  return text
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line, index) => {
      const normalized = line.replace(/^[-*]\s+/, "");
      if (normalized.endsWith(":")) {
        return (
          <p key={`insight-${index}`} className="text-sm font-semibold text-slate-100">
            {renderBold(normalized)}
          </p>
        );
      }
      return (
        <p key={`insight-${index}`} className="text-sm text-slate-200">
          {renderBold(normalized)}
        </p>
      );
    });
}

function drawChart(canvas, chart) {
  if (!canvas || !chart) {
    return;
  }
  const ctx = canvas.getContext("2d");
  const displayWidth = canvas.clientWidth || 640;
  const displayHeight = canvas.clientHeight || 320;
  if (canvas.width !== displayWidth) {
    canvas.width = displayWidth;
  }
  if (canvas.height !== displayHeight) {
    canvas.height = displayHeight;
  }
  const width = canvas.width;
  const height = canvas.height;
  ctx.clearRect(0, 0, width, height);

  const labels = chart.labels || [];
  const values = (chart.values || []).map((val) => Number(val));
  if (labels.length === 0 || values.length === 0) {
    return;
  }

  const rawType = String(chart.type || "bar").toLowerCase();
  const type = rawType === "histogram" ? "bar" : rawType;
  const padding = 36;

  if (type === "pie") {
    const total = values.reduce((acc, val) => acc + Number(val), 0) || 1;
    let startAngle = 0;
    values.forEach((value, index) => {
      const sliceAngle = (Number(value) / total) * Math.PI * 2;
      ctx.beginPath();
      ctx.moveTo(width / 2, height / 2);
      ctx.arc(width / 2, height / 2, Math.min(width, height) / 2 - 16, startAngle, startAngle + sliceAngle);
      ctx.closePath();
      ctx.fillStyle = PIE_COLORS[index % PIE_COLORS.length];
      ctx.fill();
      startAngle += sliceAngle;
    });
    return;
  }

  const maxValue = Math.max(...values, 1);
  ctx.strokeStyle = "#334155";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.lineTo(width - padding, padding);
  ctx.stroke();

  if (type === "line") {
    const stepX = (width - padding * 2) / Math.max(values.length - 1, 1);
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 2;
    ctx.beginPath();
    values.forEach((value, index) => {
      const x = padding + index * stepX;
      const y = height - padding - (Number(value) / maxValue) * (height - padding * 2);
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();
    return;
  }

  const barWidth = (width - padding * 2) / values.length;
  values.forEach((value, index) => {
    const barHeight = (Number(value) / maxValue) * (height - padding * 2);
    const x = padding + index * barWidth + 4;
    const y = height - padding - barHeight;
    ctx.fillStyle = PIE_COLORS[index % PIE_COLORS.length];
    ctx.fillRect(x, y, Math.max(barWidth - 8, 8), barHeight);
  });
}

function ChartCanvas({ chart }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (canvasRef.current && chart) {
      drawChart(canvasRef.current, chart);
    }
  }, [chart]);

  return <canvas ref={canvasRef} className="chat-canvas" />;
}

function ChatbotPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const autoQueryRef = useRef(false);
  const endRef = useRef(null);

  useEffect(() => {
    if (autoQueryRef.current) {
      return;
    }
    const params = new URLSearchParams(window.location.search);
    const query = params.get("query");
    if (query) {
      autoQueryRef.current = true;
      submitQuery(query);
    }
  }, []);

  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading]);

  async function submitQuery(query) {
    setMessages((prev) => [...prev, { role: "user", text: query }]);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chatbot/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });
      const payload = await response.json();
      if (payload.status !== "success") {
        setMessages((prev) => [
          ...prev,
          { role: "bot", text: payload.message || "Unable to generate response." },
        ]);
        setLoading(false);
        return;
      }

      const insight = payload.data.insight || "No response generated.";
      const nextSummary = payload.data.summary || null;
      const nextChart = nextSummary?.chart || null;
      const chartTitle = nextChart?.title || "Insight Chart";
      const chartDescription = nextSummary?.chart_description || "";
      const groundingColumns = nextSummary?.grounding_columns || [];
      const groundingRowCount = nextSummary?.grounding_row_count ?? null;

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: insight,
          chart: nextChart,
          chartTitle,
          chartDescription,
          groundingColumns,
          groundingRowCount,
          sourceQuery: query,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Error contacting the chatbot service." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage(event) {
    event.preventDefault();
    const query = input.trim();
    if (!query) return;
    setInput("");
    await submitQuery(query);
  }

  const chartTypeLabel = (chart) => {
    if (!chart?.type) return "Bar Plot";
    const type = chart.type.toLowerCase();
    if (type === "pie") return "Pie Chart";
    if (type === "line") return "Line Trend";
    if (type === "histogram") return "Histogram";
    return "Bar Plot";
  };

  const axisLabel = (chart) => {
    if (!chart?.labels?.length) {
      return "categories";
    }
    return "categories";
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-10">
        <header className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Chatbot</p>
            <h1 className="font-display text-3xl text-slate-100 md:text-4xl">
              AI Employee Insights
            </h1>
            <p className="mt-2 text-sm text-slate-300">
              Ask workforce questions and get narrative answers with inline visuals.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              className="rounded-full border border-amber-400/40 bg-amber-500/10 px-5 py-2 text-sm font-semibold text-amber-100 transition hover:-translate-y-0.5 hover:border-amber-300/70"
              onClick={() => (window.location.href = "/")}
            >
              Back to Home
            </button>
            <button
              type="button"
              className="rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-emerald-400"
              onClick={() => (window.location.href = "/dashboard")}
            >
              Open Dashboard
            </button>
          </div>
        </header>

        <div className="grid gap-8 lg:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
          <section className="glass-panel rounded-3xl p-6">
            <h2 className="font-display text-xl text-slate-100">Conversation</h2>
            <div className="mt-5 flex max-h-[520px] flex-col gap-4 overflow-y-auto pr-2">
              {messages.length === 0 && (
                <div className="rounded-2xl border border-dashed border-slate-700/70 p-5 text-sm text-slate-400">
                  Start by asking a question about performance, training, attrition, or compensation.
                </div>
              )}
              {messages.map((msg, idx) => (
                <div
                  key={`${msg.role}-${idx}`}
                  className={`rounded-2xl border p-4 transition ${
                    msg.role === "user"
                      ? "border-sky-400/40 bg-sky-500/10"
                      : "border-emerald-400/30 bg-emerald-500/10"
                  }`}
                >
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                    {msg.role === "user" ? "You" : "Assistant"}
                  </p>
                  <div className="mt-2 space-y-2">
                    {msg.role === "bot" ? formatInsight(msg.text) : (
                      <p className="text-sm text-slate-200">{msg.text}</p>
                    )}
                  </div>
                  {msg.role === "bot" && (msg.groundingColumns?.length || msg.groundingRowCount !== null) && (
                    <div className="mt-3 rounded-2xl border border-slate-800/70 bg-slate-950/40 p-3 text-xs text-slate-300">
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Grounding Summary</p>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {msg.groundingRowCount !== null && (
                          <span className="rounded-full border border-slate-700/70 bg-slate-900/70 px-3 py-1 text-[11px] text-slate-200">
                            Rows used: {msg.groundingRowCount}
                          </span>
                        )}
                        {msg.groundingColumns?.length ? (
                          <span className="rounded-full border border-slate-700/70 bg-slate-900/70 px-3 py-1 text-[11px] text-slate-200">
                            Columns: {msg.groundingColumns.join(", ")}
                          </span>
                        ) : null}
                      </div>
                    </div>
                  )}
                  {msg.role === "bot" && msg.chart && (
                    <div className="mt-4 space-y-4 rounded-2xl border border-emerald-400/30 bg-slate-950/40 p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div>
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Visual Summary</p>
                          <h3 className="font-display text-lg text-slate-100">{msg.chartTitle}</h3>
                        </div>
                        <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-xs text-emerald-100">
                          {chartTypeLabel(msg.chart)}
                        </span>
                      </div>
                      <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-3 text-xs text-emerald-100">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Chart Context</p>
                        <div className="mt-2 space-y-1">
                          <p>
                            <span className="text-slate-400">Query:</span> {msg.sourceQuery || "Current request"}
                          </p>
                          <p>
                            <span className="text-slate-400">X-axis:</span> {axisLabel(msg.chart)}
                          </p>
                          <p>
                            <span className="text-slate-400">Y-axis:</span> values or counts
                          </p>
                          <p>
                            <span className="text-slate-400">Chart type:</span> {chartTypeLabel(msg.chart)}
                          </p>
                        </div>
                      </div>
                      <ChartCanvas chart={msg.chart} />
                      {msg.chartDescription && (
                        <p className="text-xs text-slate-400">{msg.chartDescription}</p>
                      )}
                      <div className="rounded-2xl border border-slate-800/70 bg-slate-900/70 p-3">
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Data Breakdown</p>
                        <div className="mt-3 grid gap-2 md:grid-cols-2">
                          {msg.chart.labels?.map((label, labelIndex) => (
                            <div
                              key={`${label}-${labelIndex}`}
                              className="flex items-center justify-between rounded-xl border border-slate-800/60 bg-slate-950/50 px-3 py-2 text-xs text-emerald-100"
                            >
                              <span className="truncate">{label}</span>
                              <span className="ml-3 font-semibold text-slate-100">
                                {msg.chart.values?.[labelIndex] ?? "--"}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="rounded-2xl border border-slate-600/50 bg-slate-900/90 p-4 text-sm text-slate-300">
                  Thinking through the data...
                </div>
              )}
              <div ref={endRef} />
            </div>
            <form className="mt-6 flex flex-col gap-3 sm:flex-row" onSubmit={sendMessage}>
              <input
                type="text"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Ask about engagement, projects, hiring..."
                className="flex-1 rounded-full border border-slate-700/70 bg-slate-900/80 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-sky-400"
              />
              <button
                type="submit"
                className="rounded-full bg-sky-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-sky-400"
              >
                Send
              </button>
            </form>
          </section>

          <aside className="glass-panel rounded-3xl border border-amber-500/20 bg-amber-500/5 p-6">
            <h2 className="font-display text-xl text-slate-100">Guided Prompts</h2>
            <p className="mt-2 text-sm text-slate-300">
              Jump into common analytics workflows with one click.
            </p>
            <div className="mt-5 space-y-5">
              {PRESET_SECTIONS.map((section) => (
                <div key={section.title} className="space-y-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-amber-200">Section</p>
                    <h3 className="font-display text-base text-slate-100">{section.title}</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {section.buttons.map((button) => (
                      <button
                        key={button.label}
                        type="button"
                        className="rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-100 transition hover:-translate-y-0.5 hover:border-amber-300/70"
                        onClick={() => submitQuery(button.query)}
                      >
                        {button.label}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

export default ChatbotPage;
