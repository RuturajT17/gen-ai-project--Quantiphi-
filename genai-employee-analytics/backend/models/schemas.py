from pydantic import BaseModel


class BasicStatsResponse(BaseModel):
    total_employees: int
    avg_performance: float
    avg_salary_increase: float
