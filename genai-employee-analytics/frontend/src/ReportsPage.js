import { useEffect, useMemo, useState } from "react";

import "./App.css";
import { downloadReport } from "./services/api";

const REPORTS = [
  {
    key: "performance",
    title: "Performance Intelligence",
    description: "Performance distribution, department benchmarks, and AI guidance.",
    icon: "📈",
    filename: "Performance_Intelligence_Report.pdf",
  },
  {
    key: "attrition",
    title: "Attrition & Retention",
    description: "Attrition signals, engagement risks, and retention recommendations.",
    icon: "🧭",
    filename: "Attrition_Retention_Report.pdf",
  },
  {
    key: "compensation",
    title: "Compensation Intelligence",
    description: "Pay uplift analysis, performance alignment, and incentive signals.",
    icon: "💼",
    filename: "Compensation_Intelligence_Report.pdf",
  },
  {
    key: "training",
    title: "Training & Mentorship",
    description: "Training impact, program ROI, and development recommendations.",
    icon: "🎓",
    filename: "Training_Mentorship_Report.pdf",
  },
  {
    key: "behavioral",
    title: "Behavioral & Soft Skills",
    description: "Soft skill clusters, behavior signals, and coaching actions.",
    icon: "🧠",
    filename: "Behavioral_Soft_Skills_Report.pdf",
  },
  {
    key: "project",
    title: "Project Intelligence",
    description: "Outcome balance, role performance, and delivery insights.",
    icon: "🛠️",
    filename: "Project_Intelligence_Report.pdf",
  },
  {
    key: "hiring",
    title: "Hiring Intelligence",
    description: "Source effectiveness, hiring cost, and pipeline insights.",
    icon: "🧲",
    filename: "Hiring_Intelligence_Report.pdf",
  },
  {
    key: "executive-summary",
    title: "Executive Summary",
    description: "Top KPIs, enterprise signals, and executive recommendations.",
    icon: "🏛️",
    filename: "Executive_Summary_Report.pdf",
  },
];

function ReportsPage() {
  const [status, setStatus] = useState({});
  const blobUrls = useMemo(() => ({}), []);

  useEffect(() => {
    return () => {
      Object.values(blobUrls).forEach((url) => {
        if (url) {
          URL.revokeObjectURL(url);
        }
      });
    };
  }, [blobUrls]);

  const handleGenerate = async (report, autoDownload = false) => {
    setStatus((prev) => ({
      ...prev,
      [report.key]: { loading: true, error: "", ready: false },
    }));

    try {
      const response = await downloadReport(report.key);
      const blob = new Blob([response.data], { type: "application/pdf" });
      if (blobUrls[report.key]) {
        URL.revokeObjectURL(blobUrls[report.key]);
      }
      const url = URL.createObjectURL(blob);
      blobUrls[report.key] = url;

      setStatus((prev) => ({
        ...prev,
        [report.key]: { loading: false, error: "", ready: true },
      }));

      if (autoDownload) {
        const link = document.createElement("a");
        link.href = url;
        link.download = report.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (err) {
      setStatus((prev) => ({
        ...prev,
        [report.key]: {
          loading: false,
          error: "Failed to generate report.",
          ready: false,
        },
      }));
    }
  };

  const handleDownload = (report) => {
    const url = blobUrls[report.key];
    if (!url) {
      handleGenerate(report, true);
      return;
    }

    const link = document.createElement("a");
    link.href = url;
    link.download = report.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-10">
        <header className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Reports Center</p>
            <h1 className="font-display text-3xl text-slate-100 md:text-4xl">
              Analytics Reports Center
            </h1>
            <p className="mt-2 text-sm text-slate-300">
              Generate professional PDF reports with charts, KPIs, and AI insights on demand.
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

        <section className="grid gap-6 md:grid-cols-2">
          {REPORTS.map((report) => {
            const state = status[report.key] || {};
            return (
              <div
                key={report.key}
                className="glass-panel rounded-3xl border border-slate-800/70 bg-slate-900/70 p-6 transition hover:-translate-y-1 hover:border-emerald-400/40"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Report</p>
                    <h2 className="mt-1 font-display text-xl text-slate-100">
                      {report.title}
                    </h2>
                  </div>
                  <div className="text-3xl">{report.icon}</div>
                </div>
                <p className="mt-3 text-sm text-slate-300">{report.description}</p>

                <div className="mt-4 flex flex-wrap gap-3">
                  <button
                    type="button"
                    className="rounded-full border border-sky-400/40 bg-sky-500/10 px-4 py-2 text-xs font-semibold text-sky-100 transition hover:-translate-y-0.5 hover:border-sky-300/70 disabled:cursor-not-allowed disabled:opacity-60"
                    onClick={() => handleGenerate(report)}
                    disabled={state.loading}
                  >
                    {state.loading ? "Generating..." : "Generate Report"}
                  </button>
                  <button
                    type="button"
                    className="rounded-full bg-emerald-500/90 px-4 py-2 text-xs font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
                    onClick={() => handleDownload(report)}
                    disabled={state.loading}
                  >
                    Download PDF
                  </button>
                </div>

                {state.ready && !state.error && (
                  <p className="mt-3 text-xs text-emerald-300">
                    Report generated and ready for download.
                  </p>
                )}
                {state.error && (
                  <p className="mt-3 text-xs text-rose-300">{state.error}</p>
                )}
              </div>
            );
          })}
        </section>
      </div>
    </div>
  );
}

export default ReportsPage;
