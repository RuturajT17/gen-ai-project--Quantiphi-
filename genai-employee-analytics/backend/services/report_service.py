import datetime
import logging
import os
import re
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from services.analytics import (
    compensation_analysis,
    dashboard_overview_analysis,
    get_attrition_risk,
    get_performance_groups,
    hiring_analysis,
    project_analysis,
    soft_skills_analysis,
    training_analysis,
)
from services.llm_service import generate_insight
from services.prompt_builder import (
    build_attrition_prompt,
    build_compensation_prompt,
    build_hiring_prompt,
    build_performance_prompt,
    build_project_prompt,
    build_soft_skills_prompt,
    build_training_prompt,
)

logger = logging.getLogger("genai-employee-analytics.reports")


REPORT_DEFINITIONS = {
    "performance": {
        "title": "Performance Intelligence Report",
        "filename": "Performance_Intelligence_Report.pdf",
        "analysis_fn": get_performance_groups,
        "prompt_fn": build_performance_prompt,
        "charts": [
            ("Performance Distribution", "performance", "performance_distribution", "count"),
            ("Department Performance", "performance", "department_performance", "value"),
        ],
    },
    "attrition": {
        "title": "Attrition & Retention Report",
        "filename": "Attrition_Retention_Report.pdf",
        "analysis_fn": get_attrition_risk,
        "prompt_fn": build_attrition_prompt,
        "charts": [
            ("Engagement vs Attrition", "attrition", "engagement_vs_attrition", "resigned"),
            ("Overtime vs Resignation", "attrition", "overtime_vs_resignation", "resigned"),
        ],
    },
    "compensation": {
        "title": "Compensation Intelligence Report",
        "filename": "Compensation_Intelligence_Report.pdf",
        "analysis_fn": compensation_analysis,
        "prompt_fn": build_compensation_prompt,
        "charts": [
            ("Salary Increase vs Performance", "compensation", "salary_increase_vs_performance", "value"),
            ("Bonus vs Performance", "compensation", "bonus_vs_performance", "value"),
        ],
    },
    "training": {
        "title": "Training & Mentorship Report",
        "filename": "Training_Mentorship_Report.pdf",
        "analysis_fn": training_analysis,
        "prompt_fn": build_training_prompt,
        "charts": [
            ("Training Hours vs Performance", "training", "training_hours_vs_performance", "value"),
            ("Training Program Comparison", "training", "training_program_comparison", "value"),
        ],
    },
    "behavioral": {
        "title": "Behavioral & Soft Skills Report",
        "filename": "Behavioral_Soft_Skills_Report.pdf",
        "analysis_fn": soft_skills_analysis,
        "prompt_fn": build_soft_skills_prompt,
        "charts": [
            ("Soft Skill Clusters", "skills", "soft_skill_clusters", "count"),
            ("Average Skill Ratings", "skills", "avg_skills", "value"),
        ],
    },
    "project": {
        "title": "Project Intelligence Report",
        "filename": "Project_Intelligence_Report.pdf",
        "analysis_fn": project_analysis,
        "prompt_fn": build_project_prompt,
        "charts": [
            ("Project Outcome Distribution", "projects", "project_success_failure", "count"),
            ("Project Role Performance", "projects", "project_role_comparison", "value"),
        ],
    },
    "hiring": {
        "title": "Hiring Intelligence Report",
        "filename": "Hiring_Intelligence_Report.pdf",
        "analysis_fn": hiring_analysis,
        "prompt_fn": build_hiring_prompt,
        "charts": [
            ("Hiring Source Effectiveness", "hiring", "hiring_source_effectiveness", "value"),
            ("Recruitment Cost by Source", "hiring", "recruitment_cost_by_source", "value"),
        ],
    },
    "executive-summary": {
        "title": "Executive Summary Report",
        "filename": "Executive_Summary_Report.pdf",
        "analysis_fn": None,
        "prompt_fn": None,
        "charts": [
            ("Performance Distribution", "performance", "performance_distribution", "count"),
            ("Attrition Signals", "attrition", "engagement_vs_attrition", "resigned"),
            ("Compensation vs Performance", "compensation", "salary_increase_vs_performance", "value"),
            ("Hiring Source Effectiveness", "hiring", "hiring_source_effectiveness", "value"),
        ],
    },
}


def _build_executive_prompt(overview):
    return f"""
You are an executive HR analyst.

Task:
Generate a concise executive summary of workforce analytics.

Top KPIs:
{overview.get("kpis", {})}

Performance Overview:
{overview.get("performance", {})}

Attrition Overview:
{overview.get("attrition", {})}

Compensation Overview:
{overview.get("compensation", {})}

Hiring Overview:
{overview.get("hiring", {})}

Instructions:
1. Summarize the most important business signals.
2. Highlight top risks and opportunities.
3. Provide actionable executive recommendations.

Output Format:
- Key Insights:
- Risks:
- Recommendations:
"""


def _chart_to_png(temp_dir, title, labels, values):
    if not labels or not values:
        return None

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(labels, values, color="#38bdf8")
    ax.set_title(title)
    ax.tick_params(axis="x", labelrotation=30)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()

    safe_name = title.lower().replace(" ", "_").replace("/", "-")
    output_path = os.path.join(temp_dir, f"{safe_name}.png")
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def _build_kpi_table(kpis):
    rows = [["Metric", "Value"]]
    for key, value in kpis.items():
        label = key.replace("_", " ").title()
        rows.append([label, str(value)])

    table = Table(rows, colWidths=[3 * inch, 2 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#e2e8f0")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ]
        )
    )
    return table


def _build_list(items):
    if not items:
        items = ["No additional findings available."]
    list_items = [ListItem(Paragraph(item, getSampleStyleSheet()["BodyText"])) for item in items]
    return ListFlowable(list_items, bulletType="bullet")


def _default_findings(title):
    return [
        f"{title} highlights the most influential workforce drivers for this segment.",
        "Data trends indicate where leadership attention is most required.",
    ]


def _default_recommendations():
    return [
        "Prioritize targeted interventions for the most material trends.",
        "Align resource planning with observed performance signals.",
    ]


def _clean_insight_text(text):
    if not text:
        return ""
    cleaned = str(text)
    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.replace("__", "")
    cleaned = cleaned.replace("`", "")
    cleaned = re.sub(r"^[-*]\s+", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def generate_report(report_key, df):
    if report_key not in REPORT_DEFINITIONS:
        raise ValueError("Unknown report type")

    report_def = REPORT_DEFINITIONS[report_key]
    overview = dashboard_overview_analysis(df)
    temp_dir = tempfile.mkdtemp(prefix="reports_")
    pdf_path = os.path.join(temp_dir, report_def["filename"])

    try:
        analysis_data = None
        prompt_text = None
        if report_def.get("analysis_fn"):
            analysis_data = report_def["analysis_fn"](df)
            prompt_text = report_def["prompt_fn"](analysis_data)
        else:
            prompt_text = _build_executive_prompt(overview)

        ai_insight = generate_insight(prompt_text)
        if not ai_insight:
            ai_insight = "AI insights are temporarily unavailable. Please try again later."

        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        story = []
        story.append(Paragraph(report_def["title"], styles["Title"]))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        story.append(Paragraph(f"Generated: {timestamp}", styles["Normal"]))
        story.append(Spacer(1, 12))

        story.append(Paragraph("KPI Summary", styles["Heading2"]))
        kpis = overview.get("kpis", {})
        if kpis:
            story.append(_build_kpi_table(kpis))
        else:
            story.append(Paragraph("KPI data not available.", styles["Normal"]))
        story.append(Spacer(1, 16))

        story.append(Paragraph("Charts & Visualizations", styles["Heading2"]))
        for title, section_key, data_key, value_key in report_def.get("charts", []):
            try:
                chart_data = overview.get(section_key, {}).get(data_key, [])
                labels = [item.get("label") for item in chart_data]
                values = [item.get(value_key, 0) for item in chart_data]
                chart_path = _chart_to_png(temp_dir, title, labels, values)
                if chart_path and os.path.isfile(chart_path):
                    story.append(Paragraph(title, styles["Heading3"]))
                    story.append(Image(chart_path, width=6.5 * inch, height=3 * inch))
                else:
                    story.append(Paragraph(f"{title}: Data not available.", styles["Normal"]))
            except Exception as exc:
                logger.warning("[REPORT ERROR] chart=%s details=%s", title, str(exc))
                story.append(Paragraph(f"{title}: Unable to render chart.", styles["Normal"]))
            story.append(Spacer(1, 12))

        story.append(Paragraph("AI-Generated Insights", styles["Heading2"]))
        insight_text = _clean_insight_text(ai_insight).replace("\n", "<br />")
        story.append(Paragraph(insight_text, styles["BodyText"]))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Key Findings", styles["Heading2"]))
        story.append(_build_list(_default_findings(report_def["title"])))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Recommendations", styles["Heading2"]))
        story.append(_build_list(_default_recommendations()))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Conclusion", styles["Heading2"]))
        story.append(
            Paragraph(
                "This report summarizes the latest analytics signals and actionable priorities."
                " Review insights regularly to track improvement over time.",
                styles["BodyText"],
            )
        )

        doc.build(story)
    except Exception as exc:
        logger.exception("[REPORT ERROR] type=generate details=%s", str(exc))
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )
        story = [
            Paragraph(report_def["title"], styles["Title"]),
            Spacer(1, 12),
            Paragraph(
                "This report could not be fully generated at this time."
                " Please try again in a few moments.",
                styles["BodyText"],
            ),
        ]
        doc.build(story)

    return pdf_path, temp_dir


def cleanup_report_assets(temp_dir):
    if not temp_dir or not os.path.isdir(temp_dir):
        return
    for name in os.listdir(temp_dir):
        path = os.path.join(temp_dir, name)
        try:
            os.remove(path)
        except OSError:
            pass
    try:
        os.rmdir(temp_dir)
    except OSError:
        pass
