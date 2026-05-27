import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "./App.css";
import { getDashboardOverview } from "./services/api";

const CHART_COLORS = [
  "#38bdf8",
  "#22c55e",
  "#f97316",
  "#a855f7",
  "#facc15",
  "#06b6d4",
];

const KPI_CONFIG = [
  { key: "total_employees", label: "Total Employees" },
  { key: "avg_performance", label: "Avg Performance" },
  { key: "avg_engagement", label: "Avg Engagement" },
  { key: "avg_salary_increase", label: "Avg Salary Increase" },
  { key: "avg_skill_score", label: "Avg Skill Score" },
  { key: "attrition_risk_count", label: "Attrition Risk Count" },
];

function hasData(dataset) {
  return Array.isArray(dataset) && dataset.length > 0;
}

function InsightPanel({ title, description, items }) {
  return (
    <div className="rounded-2xl border border-slate-800/80 bg-slate-950/60 p-4 text-sm text-slate-300">
      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{title}</p>
      <p className="mt-2 text-sm text-slate-200">{description}</p>
      {items?.length ? (
        <ul className="mt-3 space-y-1 text-sm text-slate-300">
          {items.map((item) => (
            <li key={item} className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-400/80" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

function SectionCard({ title, subtitle, children }) {
  return (
    <section className="glass-panel rounded-3xl border border-slate-800/70 bg-slate-900/70 p-6">
      <div className="mb-4 space-y-1">
        <h2 className="font-display text-xl text-slate-100">{title}</h2>
        {subtitle && <p className="text-sm text-slate-400">{subtitle}</p>}
      </div>
      {children}
    </section>
  );
}

function HomePage() {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadOverview() {
      try {
        const response = await getDashboardOverview();
        if (!isMounted) {
          return;
        }
        if (response.status === "success") {
          setOverview(response.data);
        } else {
          setError(response.message || "Failed to load dashboard overview.");
        }
      } catch (err) {
        if (isMounted) {
          setError("Failed to load dashboard overview.");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadOverview();
    return () => {
      isMounted = false;
    };
  }, []);

  const kpis = useMemo(() => {
    const values = overview?.kpis || {};
    return KPI_CONFIG.map((item, index) => ({
      ...item,
      value: values[item.key] ?? "--",
      accent:
        index % 3 === 0
          ? "from-sky-500/15"
          : index % 3 === 1
          ? "from-emerald-500/15"
          : "from-amber-500/15",
    }));
  }, [overview]);

  const performanceDistribution = overview?.performance?.performance_distribution || [];
  const departmentPerformance = overview?.performance?.department_performance || [];
  const avgSkills = overview?.skills?.avg_skills || [];
  const softSkillClusters = overview?.skills?.soft_skill_clusters || [];
  const engagementAttrition = overview?.attrition?.engagement_vs_attrition || [];
  const overtimeAttrition = overview?.attrition?.overtime_vs_resignation || [];
  const engagementDistribution = overview?.attrition?.engagement_distribution || [];
  const overtimeDistribution = overview?.attrition?.overtime_distribution || [];
  const trainingHoursPerformance = overview?.training?.training_hours_vs_performance || [];
  const trainingPrograms = overview?.training?.training_program_comparison || [];
  const projectOutcomes = overview?.projects?.project_success_failure || [];
  const projectRolePerformance = overview?.projects?.project_role_comparison || [];
  const salaryVsPerformance = overview?.compensation?.salary_increase_vs_performance || [];
  const bonusVsPerformance = overview?.compensation?.bonus_vs_performance || [];
  const salaryIncreaseDistribution = overview?.compensation?.salary_increase_distribution || [];
  const salaryIncreaseByDepartment = overview?.compensation?.salary_increase_by_department || [];
  const hiringSourceEffectiveness = overview?.hiring?.hiring_source_effectiveness || [];
  const recruitmentCostBySource = overview?.hiring?.recruitment_cost_by_source || [];

  const trainingScatter = trainingHoursPerformance.map((item, index) => ({
    index: index + 1,
    label: item.label,
    value: item.value,
  }));

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-10">
        <header className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Overview</p>
            <h1 className="font-display text-3xl text-slate-100 md:text-4xl">
              GenAI Employee Analytics Overview
            </h1>
            <p className="mt-2 text-sm text-slate-300">
              Executive snapshot of workforce health, performance, and operational signals.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              className="rounded-full border border-sky-400/40 bg-sky-500/10 px-5 py-2 text-sm font-semibold text-sky-100 transition hover:-translate-y-0.5 hover:border-sky-300/70"
              onClick={() => (window.location.href = "/reports")}
            >
              Reports Center
            </button>
            <button
              type="button"
              className="rounded-full border border-amber-400/40 bg-amber-500/10 px-5 py-2 text-sm font-semibold text-amber-100 transition hover:-translate-y-0.5 hover:border-amber-300/70"
              onClick={() => (window.location.href = "/dashboard")}
            >
              Open Insights Dashboard
            </button>
            <button
              type="button"
              className="rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-emerald-400"
              onClick={() => (window.location.href = "/chatbot")}
            >
              Launch Chatbot
            </button>
          </div>
        </header>

        {error && (
          <div className="rounded-2xl border border-rose-400/40 bg-rose-500/10 p-4 text-sm text-rose-200">
            {error}
          </div>
        )}
        {loading && !error && (
          <p className="text-sm text-slate-400">Loading dashboard overview...</p>
        )}

        <section className="grid gap-4 md:grid-cols-3">
          {kpis.map((item) => (
            <div
              key={item.key}
              className={`glass-panel rounded-2xl bg-gradient-to-br ${item.accent} via-slate-900/0 to-slate-900/0 p-5 shadow-lg`}
            >
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{item.label}</p>
              <p className="mt-2 text-2xl font-semibold text-slate-100">{item.value}</p>
            </div>
          ))}
        </section>

        <SectionCard title="Performance Analytics" subtitle="Employee performance trends across departments and ratings">
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-3">
              {hasData(performanceDistribution) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={performanceDistribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Bar dataKey="count" fill="#38bdf8" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              <InsightPanel
                title="Performance Mix"
                description={
                  hasData(performanceDistribution)
                    ? "Balanced performance distribution indicates steady delivery consistency across the workforce."
                    : "Performance distribution data is not available. Review rating inputs to enable benchmarking."
                }
                items={[
                  "Track shifts in high and low ratings month-over-month.",
                  "Use distribution to calibrate manager evaluations.",
                ]}
              />
            </div>
            <div className="space-y-3">
              {hasData(departmentPerformance) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={departmentPerformance}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Bar dataKey="value" fill="#22c55e" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              <InsightPanel
                title="Department Benchmarks"
                description={
                  hasData(departmentPerformance)
                    ? "Identify teams outperforming peers and replicate their practices across divisions."
                    : "Department performance averages are not available yet."
                }
                items={[
                  "Spot underperforming units early.",
                  "Align staffing and coaching priorities.",
                ]}
              />
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Skills Analytics" subtitle="Technical and behavioral capability overview">
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-3">
              {hasData(avgSkills) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={avgSkills}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Bar dataKey="value" fill="#a855f7" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              <InsightPanel
                title="Skill Averages"
                description={
                  hasData(avgSkills)
                    ? "Use core skill averages to prioritize targeted upskilling initiatives."
                    : "Skill averages are not available. Populate skill scores to unlock insights."
                }
                items={[
                  "Identify top capability gaps by role.",
                  "Plan quarterly training with measurable outcomes.",
                ]}
              />
            </div>
            <div className="space-y-3">
              {hasData(softSkillClusters) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={softSkillClusters} dataKey="count" nameKey="label" outerRadius={90}>
                        {softSkillClusters.map((entry, index) => (
                          <Cell key={`soft-skill-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              <InsightPanel
                title="Soft Skill Mix"
                description={
                  hasData(softSkillClusters)
                    ? "Behavioral clusters highlight collaboration and leadership strengths across teams."
                    : "Soft skill clustering data is not available."
                }
                items={[
                  "Invest in leadership coaching where gaps persist.",
                  "Align team composition with project complexity.",
                ]}
              />
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Attrition Analytics" subtitle="Engagement and overtime signals tied to resignation risk">
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-6">
              {hasData(engagementAttrition) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={engagementAttrition}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="resigned" stackId="a" fill="#ef4444" />
                      <Bar dataKey="retained" stackId="a" fill="#22c55e" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : hasData(engagementDistribution) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={engagementDistribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Bar dataKey="count" fill="#38bdf8" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              {hasData(overtimeAttrition) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={overtimeAttrition}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="resigned" stackId="b" fill="#f97316" />
                      <Bar dataKey="retained" stackId="b" fill="#38bdf8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : hasData(overtimeDistribution) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={overtimeDistribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Bar dataKey="count" fill="#f97316" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
            </div>
            <div className="space-y-4">
              <InsightPanel
                title="Engagement Signal"
                description={
                  hasData(engagementAttrition)
                    ? "Lower engagement bands show higher resignation pressure, indicating teams at risk."
                    : "Engagement distribution highlights morale levels while resignation labels are missing."
                }
                items={[
                  "Prioritize pulse surveys for low-engagement cohorts.",
                  "Review manager effectiveness in at-risk groups.",
                ]}
              />
              <InsightPanel
                title="Overtime Load"
                description={
                  hasData(overtimeAttrition)
                    ? "Sustained overtime correlates with higher resignation probability."
                    : "Overtime distribution provides a baseline workload view."
                }
                items={[
                  "Rebalance staffing where overtime spikes persist.",
                  "Compare overtime against project deadlines.",
                ]}
              />
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Training Analytics" subtitle="Training impact and program performance">
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-3">
              {hasData(trainingScatter) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart>
                      <CartesianGrid stroke="#1f2937" />
                      <XAxis type="number" dataKey="index" stroke="#94a3b8" tickFormatter={(value) => trainingScatter[value - 1]?.label || value} />
                      <YAxis type="number" dataKey="value" stroke="#94a3b8" />
                      <Tooltip cursor={{ strokeDasharray: "3 3" }} />
                      <Scatter data={trainingScatter} fill="#38bdf8" />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              <InsightPanel
                title="Training vs Performance"
                description={
                  hasData(trainingScatter)
                    ? "Employees with higher training hours often exhibit stronger performance trajectories."
                    : "Training and performance linkage is not available."
                }
                items={[
                  "Focus budget on programs linked to measurable lift.",
                  "Promote high-impact tracks organization-wide.",
                ]}
              />
            </div>
            <div className="space-y-3">
              {hasData(trainingPrograms) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={trainingPrograms}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Bar dataKey="value" fill="#facc15" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              <InsightPanel
                title="Program Effectiveness"
                description={
                  hasData(trainingPrograms)
                    ? "Program comparisons highlight where training investments deliver the strongest outcomes."
                    : "Training program comparison data is not available."
                }
                items={[
                  "Scale programs with the highest lift.",
                  "Retire low-impact offerings.",
                ]}
              />
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Project Analytics" subtitle="Outcome balance and role-level performance">
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-3">
              {hasData(projectOutcomes) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={projectOutcomes} dataKey="count" nameKey="label" outerRadius={90}>
                        {projectOutcomes.map((entry, index) => (
                          <Cell key={`project-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              <InsightPanel
                title="Outcome Balance"
                description={
                  hasData(projectOutcomes)
                    ? "Balance between successful and delayed projects reflects delivery maturity."
                    : "Project outcome distribution is not available."
                }
                items={[
                  "Use success ratios to forecast delivery risk.",
                  "Focus retrospectives on failure drivers.",
                ]}
              />
            </div>
            <div className="space-y-3">
              {hasData(projectRolePerformance) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={projectRolePerformance}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Bar dataKey="value" fill="#22c55e" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              <InsightPanel
                title="Role Contribution"
                description={
                  hasData(projectRolePerformance)
                    ? "Performance differences by role indicate where coaching or resourcing is needed."
                    : "Role performance benchmarks are not available."
                }
                items={[
                  "Reinforce cross-functional alignment.",
                  "Allocate senior talent to critical roles.",
                ]}
              />
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Compensation Analytics" subtitle="Pay uplift and bonus alignment with performance">
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-3">
              {hasData(salaryVsPerformance) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={salaryVsPerformance}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Line type="monotone" dataKey="value" stroke="#38bdf8" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              <InsightPanel
                title="Salary Progression"
                description={
                  hasData(salaryVsPerformance)
                    ? "Salary increases correlate with stronger performance ratings."
                    : "Salary progression data is not available."
                }
                items={[
                  "Verify pay equity across performance bands.",
                  "Align merit cycles with impact metrics.",
                ]}
              />
            </div>
            <div className="space-y-3">
              {hasData(bonusVsPerformance) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={bonusVsPerformance}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Line type="monotone" dataKey="value" stroke="#f97316" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : hasData(salaryIncreaseDistribution) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={salaryIncreaseDistribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Bar dataKey="count" fill="#f97316" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : hasData(salaryIncreaseByDepartment) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={salaryIncreaseByDepartment}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Bar dataKey="value" fill="#f97316" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              <InsightPanel
                title="Bonus Alignment"
                description={
                  hasData(bonusVsPerformance)
                    ? "Bonus payouts reflect performance differentiation and retention incentives."
                    : "Bonus data is limited. Using pay uplift distributions where available."
                }
                items={[
                  "Ensure incentives reward critical talent.",
                  "Compare bonus curves across departments.",
                ]}
              />
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Hiring Analytics" subtitle="Source performance and recruitment costs">
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-3">
              {hasData(hiringSourceEffectiveness) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={hiringSourceEffectiveness}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Bar dataKey="value" fill="#06b6d4" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              <InsightPanel
                title="Source Quality"
                description={
                  hasData(hiringSourceEffectiveness)
                    ? "Source effectiveness highlights the channels driving high-performing hires."
                    : "Hiring source effectiveness data is not available."
                }
                items={[
                  "Invest in sources with strong quality signals.",
                  "Reduce low-yield sourcing spend.",
                ]}
              />
            </div>
            <div className="space-y-3">
              {hasData(recruitmentCostBySource) ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={recruitmentCostBySource}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="label" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip />
                      <Bar dataKey="value" fill="#facc15" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : null}
              <InsightPanel
                title="Cost Efficiency"
                description={
                  hasData(recruitmentCostBySource)
                    ? "Cost per source highlights where recruiting spend can be optimized."
                    : "Recruitment cost data is not available."
                }
                items={[
                  "Balance quality with cost efficiency.",
                  "Negotiate vendor pricing for top channels.",
                ]}
              />
            </div>
          </div>
        </SectionCard>
      </div>
    </div>
  );
}

export default HomePage;
