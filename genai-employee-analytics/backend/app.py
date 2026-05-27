import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.analytics import (
    attrition_risk_score,
    benefits_impact_analysis,
    compensation_bonus_analysis,
    get_attrition_risk,
    get_basic_stats,
    get_performance_groups,
    get_underpaid,
    compensation_analysis,
    conflict_vs_teamwork,
    engagement_satisfaction_analysis,
    get_composite_top_employees,
    high_perf_low_leadership,
    hiring_analysis,
    hiring_intelligence_analysis,
    initiative_vs_innovation,
    project_analysis,
    project_complexity_size_analysis,
    project_role_analysis,
    project_success_failure_analysis,
    project_success_model,
    resignation_analysis,
    worklife_retention_analysis,
    skill_project_mismatch_analysis,
    skill_weighted_model_analysis,
    soft_skills_analysis,
    soft_skill_clustering,
    training_correlation_analysis,
    training_improvement_gap,
    training_program_analysis,
    training_recommendation_candidates,
    training_analysis,
    mentorship_analysis,
)
from services.data_loader import load_data
from services.data_preprocessing import add_features, clean_data
from services.chatbot_service import generate_chat_response
from services.llm_service import generate_insight
from services.prompt_builder import (
    build_attrition_risk_prompt,
    build_attrition_prompt,
    build_benefits_prompt,
    build_compensation_prompt,
    build_compensation_bonus_prompt,
    build_composite_ideal_prompt,
    build_conflict_teamwork_prompt,
    build_engagement_satisfaction_prompt,
    build_hiring_prompt,
    build_hiring_intelligence_prompt,
    build_ideal_employee_prompt,
    build_initiative_innovation_prompt,
    build_low_leadership_prompt,
    build_performance_prompt,
    build_project_prompt,
    build_project_complexity_prompt,
    build_project_role_prompt,
    build_project_success_failure_prompt,
    build_project_success_model_prompt,
    build_resignation_prompt,
    build_skill_mismatch_prompt,
    build_skill_weight_prompt,
    build_soft_cluster_prompt,
    build_soft_skills_prompt,
    build_training_prompt,
    build_underpaid_prompt,
    build_training_correlation_prompt,
    build_mentorship_prompt,
    build_training_program_prompt,
    build_training_gap_prompt,
    build_training_recommendation_prompt,
    build_worklife_prompt,
)
from services.utils import to_native_type, validate_dataframe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("genai-employee-analytics")

app = FastAPI()

_RAW_DF = None
_PROCESSED_DF = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "GenAI Employee Analytics Backend Running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chatbot/query")
def chatbot_query(payload: dict):
    try:
        query = (payload or {}).get("query", "").strip()
        if not query:
            return {
                "status": "success",
                "data": {
                    "insight": "Please provide a question to analyze.",
                    "count": 0,
                    "summary": {},
                },
            }
        _, processed_df = process_pipeline()
        result = generate_chat_response(processed_df, query)
        return {
            "status": "success",
            "data": {
                "insight": result.get("insight", ""),
                "count": to_native_type(result.get("count")),
                "summary": result.get("summary", {}),
                "sample": result.get("sample", []),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate chatbot response")
        return {"status": "error", "message": str(exc)}


def process_pipeline():
    global _RAW_DF, _PROCESSED_DF
    if _RAW_DF is None or _PROCESSED_DF is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "data", "employee_data.csv")

        _RAW_DF = load_data(file_path=data_path)
        logger.info("Rows after load: %s", len(_RAW_DF))
        df = clean_data(_RAW_DF)
        df = add_features(df)
        validate_dataframe(df)
        logger.info("Rows after preprocessing: %s", len(df))
        if df.empty:
            raise ValueError(
                "All rows removed during preprocessing. Check missing data handling."
            )
        _PROCESSED_DF = df

    return _RAW_DF, _PROCESSED_DF


@app.get("/basic-stats")
def basic_stats():
    try:
        _, processed_df = process_pipeline()
        stats = get_basic_stats(processed_df)
        logger.info("Processed employees: %s", len(processed_df))
        data = {key: to_native_type(value) for key, value in stats.items()}
        return {"status": "success", "data": data}
    except Exception as exc:
        logger.exception("Failed to generate basic stats")
        return {"status": "error", "message": str(exc)}


@app.get("/performance-groups")
def performance_groups():
    try:
        _, processed_df = process_pipeline()
        data = get_performance_groups(processed_df)
        return {"status": "success", "data": data}
    except Exception as exc:
        logger.exception("Failed to generate performance groups")
        return {"status": "error", "message": str(exc)}


@app.get("/underpaid")
def underpaid():
    try:
        _, processed_df = process_pipeline()
        data = get_underpaid(processed_df)
        return {"status": "success", "data": data}
    except Exception as exc:
        logger.exception("Failed to generate underpaid employees")
        return {"status": "error", "message": str(exc)}


@app.get("/attrition-risk")
def attrition_risk():
    try:
        _, processed_df = process_pipeline()
        data = get_attrition_risk(processed_df)
        return {"status": "success", "data": data}
    except Exception as exc:
        logger.exception("Failed to generate attrition risk employees")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/performance")
def performance_insight():
    try:
        _, processed_df = process_pipeline()
        data = get_performance_groups(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_performance_prompt(data)
        logger.info("Performance insight prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate performance insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/underpaid")
def underpaid_insight():
    try:
        _, processed_df = process_pipeline()
        data = get_underpaid(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_underpaid_prompt(data)
        logger.info("Underpaid insight prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate underpaid insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/attrition")
def attrition_insight():
    try:
        _, processed_df = process_pipeline()
        data = get_attrition_risk(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_attrition_prompt(data)
        logger.info("Attrition insight prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate attrition insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/ideal-employee")
def ideal_employee_insight():
    try:
        _, processed_df = process_pipeline()
        threshold = processed_df["Performance_Rating"].quantile(0.9)
        top_performers = processed_df[
            processed_df["Performance_Rating"] >= threshold
        ]
        if top_performers.empty:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_ideal_employee_prompt(top_performers)
        logger.info("Ideal employee prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(len(top_performers)),
                "summary": {},
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate ideal employee insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/training")
def training_insight():
    try:
        _, processed_df = process_pipeline()
        data = training_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_training_prompt(data)
        logger.info("Training insight prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate training insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/soft-skills")
def soft_skills_insight():
    try:
        _, processed_df = process_pipeline()
        data = soft_skills_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_soft_skills_prompt(data)
        logger.info("Soft skills insight prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate soft skills insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/project")
def project_insight():
    try:
        _, processed_df = process_pipeline()
        data = project_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_project_prompt(data)
        logger.info("Project insight prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate project insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/compensation")
def compensation_insight():
    try:
        _, processed_df = process_pipeline()
        data = compensation_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_compensation_prompt(data)
        logger.info("Compensation insight prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate compensation insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/hiring")
def hiring_insight():
    try:
        _, processed_df = process_pipeline()
        data = hiring_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_hiring_prompt(data)
        logger.info("Hiring insight prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate hiring insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/skill-weighted-model")
def skill_weighted_insight():
    try:
        _, processed_df = process_pipeline()
        data = skill_weighted_model_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_skill_weight_prompt(data)
        logger.info("Skill weighted model prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate skill weighted insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/skill-mismatch")
def skill_mismatch_insight():
    try:
        _, processed_df = process_pipeline()
        data = skill_project_mismatch_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_skill_mismatch_prompt(data)
        logger.info("Skill mismatch prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate skill mismatch insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/high-perf-low-leadership")
def high_perf_low_leadership_insight():
    try:
        _, processed_df = process_pipeline()
        data = high_perf_low_leadership(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_low_leadership_prompt(data)
        logger.info("High perf low leadership prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate high perf low leadership insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/ideal-employee-advanced")
def ideal_employee_advanced_insight():
    try:
        _, processed_df = process_pipeline()
        data = get_composite_top_employees(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_composite_ideal_prompt(data)
        logger.info("Advanced ideal employee prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate advanced ideal employee insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/training-correlation")
def training_correlation_insight():
    try:
        _, processed_df = process_pipeline()
        data = training_correlation_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_training_correlation_prompt(data)
        logger.info("Training correlation prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate training correlation insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/mentorship")
def mentorship_insight():
    try:
        _, processed_df = process_pipeline()
        data = mentorship_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_mentorship_prompt(data)
        logger.info("Mentorship prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate mentorship insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/training-programs")
def training_programs_insight():
    try:
        _, processed_df = process_pipeline()
        data = training_program_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_training_program_prompt(data)
        logger.info("Training programs prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate training programs insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/training-gap")
def training_gap_insight():
    try:
        _, processed_df = process_pipeline()
        data = training_improvement_gap(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_training_gap_prompt(data)
        logger.info("Training gap prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate training gap insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/training-recommendation")
def training_recommendation_insight():
    try:
        _, processed_df = process_pipeline()
        data = training_recommendation_candidates(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_training_recommendation_prompt(data)
        logger.info("Training recommendation prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate training recommendation insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/soft-skill-clusters")
def soft_skill_clusters_insight():
    try:
        _, processed_df = process_pipeline()
        data = soft_skill_clustering(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_soft_cluster_prompt(data)
        logger.info("Soft skill clusters prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate soft skill clusters insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/conflict-teamwork")
def conflict_teamwork_insight():
    try:
        _, processed_df = process_pipeline()
        data = conflict_vs_teamwork(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_conflict_teamwork_prompt(data)
        logger.info("Conflict vs teamwork prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate conflict vs teamwork insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/engagement-satisfaction")
def engagement_satisfaction_insight():
    try:
        _, processed_df = process_pipeline()
        data = engagement_satisfaction_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_engagement_satisfaction_prompt(data)
        logger.info("Engagement satisfaction prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate engagement satisfaction insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/initiative-innovation")
def initiative_innovation_insight():
    try:
        _, processed_df = process_pipeline()
        data = initiative_vs_innovation(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_initiative_innovation_prompt(data)
        logger.info("Initiative innovation prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate initiative innovation insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/project-complexity-size")
def project_complexity_size_insight():
    try:
        _, processed_df = process_pipeline()
        data = project_complexity_size_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_project_complexity_prompt(data)
        logger.info("Project complexity size prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate project complexity size insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/project-success-failure")
def project_success_failure_insight():
    try:
        _, processed_df = process_pipeline()
        data = project_success_failure_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_project_success_failure_prompt(data)
        logger.info("Project success failure prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate project success failure insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/project-success-model")
def project_success_model_insight():
    try:
        _, processed_df = process_pipeline()
        data = project_success_model(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_project_success_model_prompt(data)
        logger.info("Project success model prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate project success model insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/project-role")
def project_role_insight():
    try:
        _, processed_df = process_pipeline()
        data = project_role_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_project_role_prompt(data)
        logger.info("Project role prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate project role insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/resignation")
def resignation_insight():
    try:
        _, processed_df = process_pipeline()
        data = resignation_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_resignation_prompt(data)
        logger.info("Resignation prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate resignation insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/attrition-risk-score")
def attrition_risk_score_insight():
    try:
        _, processed_df = process_pipeline()
        data = attrition_risk_score(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_attrition_risk_prompt(data)
        logger.info("Attrition risk score prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate attrition risk score insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/worklife-retention")
def worklife_retention_insight():
    try:
        _, processed_df = process_pipeline()
        data = worklife_retention_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_worklife_prompt(data)
        logger.info("Worklife retention prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate worklife retention insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/compensation-bonus")
def compensation_bonus_insight():
    try:
        _, processed_df = process_pipeline()
        data = compensation_bonus_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_compensation_bonus_prompt(data)
        logger.info("Compensation bonus prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate compensation bonus insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/benefits")
def benefits_insight():
    try:
        _, processed_df = process_pipeline()
        data = benefits_impact_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_benefits_prompt(data)
        logger.info("Benefits prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate benefits insight")
        return {"status": "error", "message": str(exc)}


@app.get("/insights/hiring-intelligence")
def hiring_intelligence_insight():
    try:
        _, processed_df = process_pipeline()
        data = hiring_intelligence_analysis(processed_df)
        if data.get("count", 0) == 0:
            return {
                "status": "success",
                "data": {
                    "insight": "No matching employees found.",
                    "count": 0,
                    "summary": {},
                },
            }
        prompt = build_hiring_intelligence_prompt(data)
        logger.info("Hiring intelligence prompt: %s", prompt[:500])
        insight = generate_insight(prompt)
        return {
            "status": "success",
            "data": {
                "insight": insight,
                "count": to_native_type(data.get("count")),
                "summary": data.get("summary", {}),
            },
        }
    except Exception as exc:
        logger.exception("Failed to generate hiring intelligence insight")
        return {"status": "error", "message": str(exc)}
