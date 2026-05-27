import { useEffect, useMemo, useState } from "react";

import "./App.css";
import ChatbotPage from "./ChatbotPage";
import HomePage from "./HomePage";
import ReportsPage from "./ReportsPage";

import { getBasicStats } from "./services/api";

const QUESTION_SECTIONS = [
  {
    title: "Section 1: Employee Performance & Skill Analytics",
    questions: [
      {
        id: "q1",
        text: "Analyze how Technical_Skills_Rating, Communication_Skills_Rating, and Problem_Solving_Skills_Rating collectively influence Performance_Rating.",
        query: "Analyze how Technical_Skills_Rating, Communication_Skills_Rating, and Problem_Solving_Skills_Rating collectively influence Performance_Rating.",
        answer:
          "Technical, communication, and problem-solving ratings move together with performance, with technical strength showing the strongest lift.\nBalanced profiles (no single weak skill) consistently land in higher performance bands.\nHigh technical skill without communication tends to cap performance at mid levels.\nProblem-solving stands out as the tie-breaker for top ratings when other skills are similar.\nOverall, performance rises most when all three ratings are jointly high.",
      },
      {
        id: "q2",
        text: "Identify employees with high performance but low leadership potential and suggest possible reasons using contextual attributes.",
        query: "Identify employees with high performance but low leadership potential and suggest possible reasons using contextual attributes.",
        answer:
          "High performers with low leadership scores typically show strong individual output but limited mentoring or cross-team influence.\nThey are often concentrated in specialist roles where deep expertise is rewarded over people leadership.\nLower collaboration or communication ratings appear alongside lower leadership potential.\nShorter tenure or limited training in management programs is a common pattern.\nTargeted leadership coaching and project ownership can help close the gap.",
      },
      {
        id: "q3",
        text: "Compare employees with Performance_Rating >= 10 vs <= 5 and generate behavioral patterns using prompt-based clustering.",
        query: "Compare employees with Performance_Rating >= 10 vs <= 5 and generate behavioral patterns using prompt-based clustering.",
        answer:
          "Top performers cluster around high engagement, consistent project delivery, and strong problem-solving.\nLower performers show more variance in engagement and weaker soft-skill alignment.\nOvertime is not a consistent driver in the top group, suggesting quality over hours.\nHigh performers often combine stable training participation with higher mentor ratings.\nLow performers show more mismatch between skills and project assignments.",
      },
      {
        id: "q4",
        text: "Detect inconsistencies where high ratings (skills) do not align with project outcomes and explain anomalies.",
        query: "Detect inconsistencies where high ratings (skills) do not align with project outcomes and explain anomalies.",
        answer:
          "A subset of high-skill employees are tied to failed projects, indicating external drivers.\nCommon anomalies include high project complexity paired with tight timelines.\nRole mismatch and limited cross-functional support appear frequently in these cases.\nCommunication gaps can reduce outcome quality even with strong technical scores.\nThese cases suggest process and resourcing issues rather than individual skill limits.",
      },
      {
        id: "q5",
        text: "Generate a profile of an ideal employee using top 10% performers across all rating columns.",
        query: "Generate a profile of an ideal employee using top 10% performers across all rating columns.",
        answer:
          "Ideal employees show consistently high ratings across technical, communication, and problem-solving.\nThey maintain strong engagement and job satisfaction scores with low conflict signals.\nProject outcomes trend successful even on larger or more complex work.\nThey participate in advanced training and score well on mentorship alignment.\nRetention risk is low, indicating stable fit with role and culture.",
      },
    ],
  },
  {
    title: "Section 2: Training, Mentorship & Development",
    questions: [
      {
        id: "q6",
        text: "Evaluate whether Professional_Development_Hours correlate with Performance_Rating and Promotions using LLM-driven inference.",
        query: "Evaluate whether Professional_Development_Hours correlate with Performance_Rating and Promotions using LLM-driven inference.",
        answer:
          "Professional development hours show a positive but moderate correlation with performance ratings.\nThe strongest gains appear once a baseline training threshold is met.\nPromotions align more with performance consistency than raw training hours alone.\nAdvanced training types amplify impact compared to basic programs.\nTraining appears most effective when paired with active mentoring.",
      },
      {
        id: "q7",
        text: "Analyze the impact of Mentor_Rating and Mentor_Experience_Level on Internship_Conversion_Status and Employee_Performance.",
        query: "Analyze the impact of Mentor_Rating and Mentor_Experience_Level on Internship_Conversion_Status and Employee_Performance.",
        answer:
          "Higher mentor ratings align with stronger conversion to full-time roles.\nExperienced mentors drive better early performance and faster skill ramp-up.\nConversion success is highest when mentor ratings and engagement scores are both high.\nLower mentor ratings often coincide with weaker onboarding outcomes.\nMentor quality appears more predictive than mentor tenure alone.",
      },
      {
        id: "q8",
        text: "Identify employees who received training but show low performance improvement, and generate hypotheses.",
        query: "Identify employees who received training but show low performance improvement, and generate hypotheses.",
        answer:
          "Some employees show training participation without measurable performance lift.\nPossible causes include role misalignment or training not tailored to job needs.\nLow engagement or weak mentoring can dampen training impact.\nOverloaded project schedules may limit time to apply new skills.\nA targeted skills-to-role mapping is likely needed for these cases.",
      },
      {
        id: "q9",
        text: "Compare Training_Program types (Basic vs Advanced) and their effect on performance and career growth.",
        query: "Compare Training_Program types (Basic vs Advanced) and their effect on performance and career growth.",
        answer:
          "Advanced programs show stronger gains in performance and promotion signals.\nBasic programs are useful for onboarding but plateau quickly.\nEmployees completing advanced tracks show higher confidence and project impact.\nCareer growth accelerates when advanced training is paired with leadership exposure.\nOverall, advanced programs deliver higher long-term ROI.",
      },
      {
        id: "q10",
        text: "Predict which employees are likely to benefit most from advanced training programs using reasoning-based prompts.",
        query: "Predict which employees are likely to benefit most from advanced training programs using reasoning-based prompts.",
        answer:
          "Employees with strong baseline performance and high learning engagement benefit most.\nThose with solid technical ratings but mid-level project outcomes show the highest uplift.\nMentor-supported employees realize faster post-training gains.\nEmployees with stable attendance and consistent feedback adapt quickly to advanced programs.\nSelection should prioritize readiness and role alignment over tenure alone.",
      },
    ],
  },
  {
    title: "Section 3: Behavioral & Soft Skills Intelligence",
    questions: [
      {
        id: "q11",
        text: "Cluster employees based on soft skill ratings (Leadership, Teamwork, Adaptability, Creativity) and describe each cluster.",
        query: "Cluster employees based on soft skill ratings (Leadership, Teamwork, Adaptability, Creativity) and describe each cluster.",
        answer:
          "Three primary clusters emerge: collaborative leaders, adaptive specialists, and individual contributors.\nCollaborative leaders score high across teamwork and leadership with strong adaptability.\nAdaptive specialists show high creativity and adaptability but moderate leadership.\nIndividual contributors excel in creativity but lag in teamwork alignment.\nCluster movement improves with mentoring and cross-functional exposure.",
      },
      {
        id: "q12",
        text: "Identify employees with high conflict resolution cases but low teamwork scores and explain contradictions.",
        query: "Identify employees with high conflict resolution cases but low teamwork scores and explain contradictions.",
        answer:
          "High conflict resolution with low teamwork suggests reactive problem solving rather than proactive collaboration.\nThese employees often step in during crises but are less integrated in day-to-day teamwork.\nRole pressures or cross-team responsibilities can reduce perceived teamwork scores.\nCommunication style differences may resolve conflicts but still harm cohesion.\nTeam dynamics coaching could improve alignment.",
      },
      {
        id: "q13",
        text: "Generate insights on how Employee_Engagement_Score impacts Job Satisfaction and Retention.",
        query: "Generate insights on how Employee_Engagement_Score impacts Job Satisfaction and Retention.",
        answer:
          "Higher engagement strongly aligns with improved job satisfaction.\nRetention risk drops significantly in the highest engagement bands.\nLow engagement clusters show higher absenteeism and turnover indicators.\nEngagement appears to mediate the effect of compensation on satisfaction.\nTargeted engagement initiatives are likely to improve retention outcomes.",
      },
      {
        id: "q14",
        text: "Detect employees with high initiative but low innovation contribution and explain possible blockers.",
        query: "Detect employees with high initiative but low innovation contribution and explain possible blockers.",
        answer:
          "High initiative without innovation suggests operational focus over experimentation.\nTime constraints and risk-averse project scopes are common blockers.\nLack of cross-team collaboration reduces idea visibility and adoption.\nInnovation improves when initiative is paired with mentorship and ownership.\nProcess changes can convert initiative into measurable innovation output.",
      },
    ],
  },
  {
    title: "Section 4: Project & Work Performance Analysis",
    questions: [
      {
        id: "q15",
        text: "Analyze how Project_Complexity and Project_Size influence Project_Outcome.",
        query: "Analyze how Project_Complexity and Project_Size influence Project_Outcome.",
        answer:
          "Higher complexity projects show a wider spread of outcomes.\nSuccess improves when complexity is matched with senior roles and strong planning.\nLarge projects succeed more often when team composition is balanced.\nSmaller projects are less sensitive to complexity but more to role mismatch.\nOutcome stability rises with consistent project management practices.",
      },
      {
        id: "q16",
        text: "Identify patterns among employees involved in successful vs failed projects.",
        query: "Identify patterns among employees involved in successful vs failed projects.",
        answer:
          "Successful project teams show higher engagement and cross-skill balance.\nFailed projects correlate with higher skill-role mismatch and lower mentor support.\nLeadership and communication scores are stronger in successful teams.\nOvertime is more common in failed projects, suggesting late recovery attempts.\nEarly risk signals include low adaptability and uneven workload distribution.",
      },
      {
        id: "q17",
        text: "Generate a predictive reasoning model: What combination of skills and ratings leads to successful project outcomes?",
        query: "Generate a predictive reasoning model: What combination of skills and ratings leads to successful project outcomes?",
        answer:
          "Success is most likely when technical strength is paired with communication and problem-solving balance.\nModerate leadership with high teamwork is a strong predictor for delivery success.\nHigh adaptability reduces failure risk on complex projects.\nMentor-supported teams convert skill strengths into execution outcomes.\nOverall, balance across skills matters more than a single peak rating.",
      },
      {
        id: "q18",
        text: "Compare performance of employees across different Project_Roles (Manager vs Developer vs Analyst).",
        query: "Compare performance of employees across different Project_Roles (Manager vs Developer vs Analyst).",
        answer:
          "Managers show the highest leadership and communication scores but more variance in technical ratings.\nDevelopers lead in technical strength with strong problem-solving consistency.\nAnalysts show high adaptability and steady performance but lower leadership scores.\nTop performance is most common when role strengths align with project needs.\nCross-role collaboration lifts overall outcomes across the board.",
      },
    ],
  },
  {
    title: "Section 5: Attrition & Retention Intelligence",
    questions: [
      {
        id: "q19",
        text: "Identify factors contributing to Employee_Resignation_Status = Yes using multi-variable reasoning.",
        query: "Identify factors contributing to Employee_Resignation_Status = Yes using multi-variable reasoning.",
        answer:
          "Resignation aligns with low engagement, weaker satisfaction, and lower mentor support.\nCompensation gaps amplify risk when paired with high workload.\nEmployees with limited training participation show higher exit likelihood.\nPoor work-life balance is a consistent signal across resignation cases.\nEarly intervention should focus on engagement and career growth paths.",
      },
      {
        id: "q20",
        text: "Generate a risk profile of employees likely to resign using behavioral and compensation features.",
        query: "Generate a risk profile of employees likely to resign using behavioral and compensation features.",
        answer:
          "High-risk employees show low engagement, low satisfaction, and below-market compensation trends.\nOvertime plus weak mentor ratings raises risk sharply.\nLow training investment often appears with limited growth signals.\nBehavioral volatility is higher in at-risk groups.\nRetention improves when compensation and engagement are addressed together.",
      },
      {
        id: "q21",
        text: "Compare work-life balance, overtime, and engagement scores between resigned vs retained employees.",
        query: "Compare work-life balance, overtime, and engagement scores between resigned vs retained employees.",
        answer:
          "Resigned employees show lower work-life scores and higher overtime frequency.\nEngagement is consistently lower in the resigned group.\nRetention is strongest when work-life scores and engagement move together.\nHigh overtime without recognition correlates with lower satisfaction.\nBalancing workload is a key lever for retention.",
      },
    ],
  },
  {
    title: "Section 6: Compensation & Benefits Analysis",
    questions: [
      {
        id: "q22",
        text: "Analyze the relationship between Salary Increase %, Bonus %, and Performance Rating.",
        query: "Analyze the relationship between Salary Increase %, Bonus %, and Performance Rating.",
        answer:
          "Salary increases track performance but with a noticeable mid-band compression.\nBonus percentages show stronger alignment with top performers than base increases.\nHigh performers with low bonus allocations appear as outliers.\nCompensation alignment improves when bonuses are tied to project outcomes.\nOverall, variable pay is the clearest performance differentiator.",
      },
      {
        id: "q23",
        text: "Identify employees who are underpaid relative to their performance and skills.",
        query: "Identify employees who are underpaid relative to their performance and skills.",
        answer:
          "Underpaid employees generally show high performance with below-average salary growth.\nThey often have strong skill scores and consistent project contributions.\nLower compensation is more common in specialist roles with limited visibility.\nRetention risk increases when pay and performance remain misaligned.\nReviewing salary bands for high performers can reduce attrition risk.",
      },
      {
        id: "q24",
        text: "Evaluate whether compensation benefits influence retention and satisfaction.",
        query: "Evaluate whether compensation benefits influence retention and satisfaction.",
        answer:
          "Benefits correlate with higher satisfaction, especially in mid-tenure employees.\nRetention improves when benefits are paired with competitive base pay.\nBenefits alone do not offset low engagement or poor work-life balance.\nHigh benefit satisfaction is linked to lower resignation intent.\nThe best outcomes come from balanced pay, benefits, and growth options.",
      },
    ],
  },
  {
    title: "Section 7: Recruitment & Hiring Effectiveness",
    questions: [
      {
        id: "q25",
        text: "Analyze how Hiring_Source, Time_to_Hire, and Recruitment_Cost impact performance, retention, and job satisfaction.",
        query: "Analyze how Hiring_Source, Time_to_Hire, and Recruitment_Cost impact performance, retention, and job satisfaction.",
        answer:
          "Shorter time-to-hire correlates with faster early performance, but only when role fit is high.\nHigher recruitment cost is justified when retention and performance remain strong.\nReferral and targeted sources show stronger satisfaction outcomes.\nLonger hiring cycles often align with higher skill match and lower attrition.\nOverall, quality of fit matters more than speed alone.",
      },
    ],
  },
];

function App() {
  const path = window.location.pathname;
  if (path === "/") {
    return <HomePage />;
  }
  if (path === "/chatbot") {
    return <ChatbotPage />;
  }
  if (path === "/reports") {
    return <ReportsPage />;
  }

  const isDashboard = path === "/dashboard";
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(isDashboard);
  const [expandedAnswers, setExpandedAnswers] = useState({});

  useEffect(() => {
    if (!isDashboard) {
      return;
    }

    async function fetchStats() {
      try {
        const response = await getBasicStats();
        if (response.status === "success") {
          setStats(response.data);
        } else {
          setError(response.message || "Failed to load stats.");
        }
      } catch (err) {
        setError("Failed to load stats.");
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, [isDashboard]);

  const overviewCards = useMemo(
    () => [
      {
        label: "Total Employees",
        value: stats?.total_employees ?? "--",
      },
      {
        label: "Avg Performance",
        value: stats?.avg_performance ?? "--",
      },
      {
        label: "Avg Salary Increase",
        value: stats?.avg_salary_increase ?? "--",
      },
    ],
    [stats]
  );

  function renderAnswerLines(text) {
    if (!text) {
      return <p className="text-sm text-slate-300">No summary available.</p>;
    }
    return text
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .map((line, index) => (
        <p key={`answer-line-${index}`} className="text-sm text-slate-200">
          {line}
        </p>
      ));
  }

  const toggleAnswer = (id) => {
    setExpandedAnswers((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  if (!isDashboard) {
    return <HomePage />;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-10">
        <header className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Dashboard</p>
            <h1 className="font-display text-3xl text-slate-100 md:text-4xl">
              GenAI Employee Analytics
            </h1>
            <p className="mt-2 text-sm text-slate-300">
              Sectioned AI insights with quick summaries and guided chatbot deep dives.
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
              onClick={() => (window.location.href = "/")}
            >
              Back to Home
            </button>
            <button
              type="button"
              className="rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-emerald-400"
              onClick={() => (window.location.href = "/chatbot")}
            >
              Open Chatbot
            </button>
          </div>
        </header>

        {error && (
          <div className="rounded-2xl border border-rose-400/40 bg-rose-500/10 p-4 text-sm text-rose-200">
            {error}
          </div>
        )}
        {!error && loading && (
          <p className="text-sm text-slate-400">Loading overview metrics...</p>
        )}

        <section className="grid gap-4 md:grid-cols-3">
          {overviewCards.map((card, index) => {
            const accents = [
              "from-sky-500/15 via-slate-900/0 to-slate-900/0",
              "from-amber-500/15 via-slate-900/0 to-slate-900/0",
              "from-emerald-500/15 via-slate-900/0 to-slate-900/0",
            ];
            return (
            <div
              key={card.label}
              className={`glass-panel card-sheen rounded-2xl bg-gradient-to-br ${accents[index % accents.length]} p-5 transition hover:-translate-y-1 hover:shadow-2xl`}
            >
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{card.label}</p>
              <p className="mt-2 text-2xl font-semibold text-slate-100">{card.value}</p>
            </div>
            );
          })}
        </section>

        <section className="space-y-6">
          <div className="flex items-center gap-4">
            <h2 className="font-display text-2xl text-slate-100">AI Insight Sections</h2>
            <div className="fade-divider h-px flex-1 bg-gradient-to-r from-amber-400/0 via-amber-300/60 to-amber-300/0" />
          </div>

          <div className="space-y-8">
            {QUESTION_SECTIONS.map((section) => (
              <div key={section.title} className="glass-panel rounded-3xl border border-slate-800/70 bg-slate-900/70 p-6">
                <div className="flex flex-col gap-2 border-b border-slate-800/70 pb-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Insight Section</p>
                  <h3 className="font-display text-xl text-slate-100">{section.title}</h3>
                </div>
                <div className="mt-5 grid gap-4">
                  {section.questions.map((question) => {
                    const isOpen = Boolean(expandedAnswers[question.id]);
                    return (
                      <div
                        key={question.id}
                        className="rounded-2xl border border-slate-800/70 bg-slate-950/40 p-5 transition hover:-translate-y-1 hover:border-emerald-400/50"
                      >
                        <p className="text-sm font-semibold text-slate-100">
                          {question.text}
                        </p>
                        {isOpen && (
                          <div className="mt-3 space-y-2">
                            {renderAnswerLines(question.answer)}
                          </div>
                        )}
                        <div className="mt-4 flex flex-wrap gap-3">
                          <button
                            type="button"
                            className="rounded-full border border-amber-400/50 bg-amber-500/10 px-4 py-2 text-xs font-semibold text-amber-100 transition hover:border-amber-300/70"
                            onClick={() => toggleAnswer(question.id)}
                          >
                            {isOpen ? "Hide Summary" : "Show Summary"}
                          </button>
                          <button
                            type="button"
                            className="rounded-full bg-emerald-500/90 px-4 py-2 text-xs font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-emerald-400"
                            onClick={() =>
                              (window.location.href = `/chatbot?query=${encodeURIComponent(
                                question.query
                              )}`)
                            }
                          >
                            Explore in Chatbot
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;
