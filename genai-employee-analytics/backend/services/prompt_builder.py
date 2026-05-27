def build_base_prompt(title, data):
    sample = data.get("sample", [])
    summary = data.get("summary", {})
    count = data.get("count", 0)

    return f"""
You are an expert HR data analyst.

Task:
{title}

Dataset Information:
- Total Matching Employees: {count}

Summary Metrics:
{summary}

Sample Employee Records:
{sample}

Instructions:
1. Identify key patterns in the data
2. Explain possible reasons behind those patterns
3. Highlight any risks or concerns
4. Provide actionable recommendations

Output Format:
- Key Insights:
- Reasons:
- Risks:
- Recommendations:

Keep the explanation concise, structured, and professional.
"""


def build_performance_prompt(data):
    return build_base_prompt(
        "Analyze differences between high-performing and low-performing employees.",
        data,
    )


def build_attrition_prompt(data):
    return build_base_prompt(
        "Analyze employees who are at risk of leaving the organization.",
        data,
    )


def build_underpaid_prompt(data):
    return build_base_prompt(
        "Analyze employees who may be underpaid based on their performance and salary growth.",
        data,
    )


def build_ideal_employee_prompt(df):
    sample = df.head(10).to_dict(orient="records")

    return f"""
You are an expert HR strategist.

Task:
Generate an ideal employee profile based on top-performing employees.

Sample Top Performers:
{sample}

Instructions:
1. Identify key technical and soft skills
2. Highlight behavioral traits
3. Describe work patterns
4. Define what makes them successful

Output Format:
- Ideal Profile:
- Key Skills:
- Behavioral Traits:
- Success Factors:
"""


def build_training_prompt(data):
    return build_base_prompt(
        "Analyze impact of training on employee performance",
        data,
    )


def build_soft_skills_prompt(data):
    return build_base_prompt(
        "Analyze employee soft skill patterns and clusters",
        data,
    )


def build_project_prompt(data):
    return build_base_prompt(
        "Analyze project success patterns based on complexity and roles",
        data,
    )


def build_compensation_prompt(data):
    return build_base_prompt(
        "Analyze compensation fairness and performance relationship",
        data,
    )


def build_hiring_prompt(data):
    return build_base_prompt(
        "Analyze effectiveness of hiring sources and recruitment process",
        data,
    )


def build_skill_weight_prompt(data):
    return build_base_prompt(
        "Analyze the importance of different skills in determining employee performance.",
        data,
    )


def build_skill_mismatch_prompt(data):
    return build_base_prompt(
        "Analyze cases where highly skilled employees are associated with failed projects.",
        data,
    )


def build_low_leadership_prompt(data):
    return build_base_prompt(
        "Analyze employees with high performance but low leadership potential.",
        data,
    )


def build_composite_ideal_prompt(data):
    return build_base_prompt(
        "Analyze top employees based on a composite score across all skill dimensions and define an ideal employee profile.",
        data,
    )


def build_training_correlation_prompt(data):
    return build_base_prompt(
        "Analyze how training hours influence performance and promotions.",
        data,
    )


def build_mentorship_prompt(data):
    return build_base_prompt(
        "Analyze how mentor rating and experience influence employee performance and conversion outcomes.",
        data,
    )


def build_training_program_prompt(data):
    return build_base_prompt(
        "Compare different training programs and their impact on performance and growth.",
        data,
    )


def build_training_gap_prompt(data):
    return build_base_prompt(
        "Analyze why some employees receive training but show low performance improvement, and explain possible blockers.",
        data,
    )


def build_training_recommendation_prompt(data):
    return build_base_prompt(
        "Identify which employees would benefit most from advanced training programs, justify the selection, and suggest next steps.",
        data,
    )


def build_soft_cluster_prompt(data):
    return build_base_prompt(
        "Analyze clusters of employees based on multiple soft skill dimensions and describe each cluster.",
        data,
    )


def build_conflict_teamwork_prompt(data):
    return build_base_prompt(
        "Analyze employees with high conflict resolution but low teamwork and explain contradictions.",
        data,
    )


def build_engagement_satisfaction_prompt(data):
    return build_base_prompt(
        "Analyze how engagement affects satisfaction, how both influence retention, compare resigned vs retained employees, and recommend actions to improve retention.",
        data,
    )


def build_initiative_innovation_prompt(data):
    return build_base_prompt(
        "Analyze employees with high initiative but low innovation and identify possible blockers.",
        data,
    )


def build_project_complexity_prompt(data):
    return build_base_prompt(
        "Analyze how project complexity and size influence project outcomes.",
        data,
    )


def build_project_success_failure_prompt(data):
    return build_base_prompt(
        "Analyze patterns between successful and failed projects.",
        data,
    )


def build_project_success_model_prompt(data):
    return build_base_prompt(
        "Compare successful vs failed projects, identify key contributing factors, highlight role and skill impact, and suggest how to improve project success rate.",
        data,
    )


def build_project_role_prompt(data):
    return build_base_prompt(
        "Compare performance across different project roles and explain differences.",
        data,
    )


def build_resignation_prompt(data):
    return build_base_prompt(
        "Analyze the factors contributing to employee resignation.",
        data,
    )


def build_attrition_risk_prompt(data):
    return build_base_prompt(
        "Analyze employees at high risk of leaving and identify key risk factors.",
        data,
    )


def build_worklife_prompt(data):
    return build_base_prompt(
        "Compare work-life balance, engagement, and overtime between resigned and retained employees, and explain retention implications.",
        data,
    )


def build_compensation_bonus_prompt(data):
    return build_base_prompt(
        "Analyze the relationship between salary increase, bonus, and performance.",
        data,
    )


def build_benefits_prompt(data):
    return build_base_prompt(
        "Analyze how employee benefits influence satisfaction and retention, and identify improvement opportunities.",
        data,
    )


def build_hiring_intelligence_prompt(data):
    return build_base_prompt(
        "Analyze hiring effectiveness across different hiring sources. "
        "Consider time to hire, recruitment cost, performance, retention, and job satisfaction. "
        "Identify which sources produce the best employees and explain why. "
        "Provide recommendations to improve hiring strategy.",
        data,
    )
