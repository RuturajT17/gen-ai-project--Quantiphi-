SALARY_INCREASE_COLUMN = "Annual_Salary_Increase_Percentage"
SAMPLE_SIZE = 10

NUMERIC_COLUMNS = [
    "Performance_Rating",
    "Technical_Skills_Rating",
    "Communication_Skills_Rating",
    "Problem_Solving_Skills_Rating",
    "Leadership_Skills_Rating",
    "Teamwork_Skills_Rating",
    "Adaptability_Skills_Rating",
    "Creativity_Skills_Rating",
    SALARY_INCREASE_COLUMN,
]

REQUIRED_COLUMNS = [
    "Performance_Rating",
    "Technical_Skills_Rating",
    "Communication_Skills_Rating",
    "Problem_Solving_Skills_Rating",
    "Teamwork_Skills_Rating",
]

SOFT_SKILL_COLUMN_MAP = {
    "Leadership_Skills_Rating": [
        "Leadership_Skills_Rating",
        "Leadership_Qualities_Rating",
    ],
    "Adaptability_Skills_Rating": [
        "Adaptability_Skills_Rating",
        "Adaptability_Rating",
    ],
    "Creativity_Skills_Rating": [
        "Creativity_Skills_Rating",
        "Creativity_Rating",
    ],
}
