import axios from "axios";

const BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 8000,
});

const insightClient = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
});

const reportClient = axios.create({
  baseURL: BASE_URL,
  timeout: 90000,
});

export async function getBasicStats() {
  const response = await apiClient.get("/basic-stats");
  return response.data;
}

export async function getDashboardOverview() {
  const response = await apiClient.get("/dashboard-overview");
  return response.data;
}

export async function getPerformanceGroups() {
  const response = await apiClient.get("/performance-groups");
  return response.data;
}

export async function getUnderpaid() {
  const response = await apiClient.get("/underpaid");
  return response.data;
}

export async function getAttritionRisk() {
  const response = await apiClient.get("/attrition-risk");
  return response.data;
}

export async function getPerformanceInsight() {
  const response = await insightClient.get("/insights/performance");
  return response.data;
}

export async function getUnderpaidInsight() {
  const response = await insightClient.get("/insights/underpaid");
  return response.data;
}

export async function getAttritionInsight() {
  const response = await insightClient.get("/insights/attrition");
  return response.data;
}

export async function getIdealEmployeeInsight() {
  const response = await insightClient.get("/insights/ideal-employee");
  return response.data;
}

export async function getTrainingInsight() {
  const response = await insightClient.get("/insights/training");
  return response.data;
}

export async function getSoftSkillsInsight() {
  const response = await insightClient.get("/insights/soft-skills");
  return response.data;
}

export async function getProjectInsight() {
  const response = await insightClient.get("/insights/project");
  return response.data;
}

export async function getCompensationInsight() {
  const response = await insightClient.get("/insights/compensation");
  return response.data;
}

export async function getHiringInsight() {
  const response = await insightClient.get("/insights/hiring");
  return response.data;
}

export async function getSkillWeightedInsight() {
  const response = await insightClient.get("/insights/skill-weighted-model");
  return response.data;
}

export async function getSkillMismatchInsight() {
  const response = await insightClient.get("/insights/skill-mismatch");
  return response.data;
}

export async function getHighPerfLowLeadershipInsight() {
  const response = await insightClient.get("/insights/high-perf-low-leadership");
  return response.data;
}

export async function getAdvancedIdealInsight() {
  const response = await insightClient.get("/insights/ideal-employee-advanced");
  return response.data;
}

export async function getTrainingCorrelationInsight() {
  const response = await insightClient.get("/insights/training-correlation");
  return response.data;
}

export async function getMentorshipInsight() {
  const response = await insightClient.get("/insights/mentorship");
  return response.data;
}

export async function getTrainingProgramsInsight() {
  const response = await insightClient.get("/insights/training-programs");
  return response.data;
}

export async function getTrainingGapInsight() {
  const response = await insightClient.get("/insights/training-gap");
  return response.data;
}

export async function getTrainingRecommendationInsight() {
  const response = await insightClient.get("/insights/training-recommendation");
  return response.data;
}

export async function getSoftSkillClustersInsight() {
  const response = await insightClient.get("/insights/soft-skill-clusters");
  return response.data;
}

export async function getConflictTeamworkInsight() {
  const response = await insightClient.get("/insights/conflict-teamwork");
  return response.data;
}

export async function getEngagementSatisfactionInsight() {
  const response = await insightClient.get("/insights/engagement-satisfaction");
  return response.data;
}

export async function getInitiativeInnovationInsight() {
  const response = await insightClient.get("/insights/initiative-innovation");
  return response.data;
}

export async function getProjectComplexityInsight() {
  const response = await insightClient.get("/insights/project-complexity-size");
  return response.data;
}

export async function getProjectSuccessFailureInsight() {
  const response = await insightClient.get("/insights/project-success-failure");
  return response.data;
}

export async function getProjectSuccessModelInsight() {
  const response = await insightClient.get("/insights/project-success-model");
  return response.data;
}

export async function getProjectRoleInsight() {
  const response = await insightClient.get("/insights/project-role");
  return response.data;
}

export async function getResignationInsight() {
  const response = await insightClient.get("/insights/resignation");
  return response.data;
}

export async function getAttritionRiskScoreInsight() {
  const response = await insightClient.get("/insights/attrition-risk-score");
  return response.data;
}

export async function getWorklifeInsight() {
  const response = await insightClient.get("/insights/worklife-retention");
  return response.data;
}

export async function getCompensationBonusInsight() {
  const response = await insightClient.get("/insights/compensation-bonus");
  return response.data;
}

export async function getBenefitsInsight() {
  const response = await insightClient.get("/insights/benefits");
  return response.data;
}

export async function getHiringIntelligenceInsight() {
  const response = await insightClient.get("/insights/hiring-intelligence");
  return response.data;
}

export async function downloadReport(reportKey) {
  const response = await reportClient.get(`/reports/${reportKey}`, {
    responseType: "blob",
  });
  return response;
}
