"""SQL queries for crime statistics segmentation"""

CRIME_STATS_QUERY = """
SELECT
    c.area_id AS neighborhood_id,
    c.neighborhood,
    r.inhabitants AS population,
    c.total_number_cases AS total_crimes,
    SUM(CASE WHEN c.category = 'violent' THEN c.total_number_cases ELSE 0 END) AS violent_crimes,
    SUM(CASE WHEN c.category = 'property' THEN c.total_number_cases ELSE 0 END) AS property_crimes,
    AVG(c.severity_weight) AS avg_severity,
    (c.total_number_cases * 100000.0) / NULLIF(r.inhabitants, 0) AS crime_rate_per_100k,
    c.year,
    EXTRACT(MONTH FROM c.updated_at) AS month
FROM
    crime_statistics c
JOIN
    regional_statistics r ON c.neighborhood = r.neighborhood AND c.year = r.year
WHERE
    c.updated_at BETWEEN CURRENT_DATE - INTERVAL '1 year' AND CURRENT_DATE
GROUP BY
    c.area_id, c.neighborhood, r.inhabitants, c.total_number_cases,
    c.year, c.updated_at
"""

TREND_ANALYSIS_QUERY = """
SELECT
    c.area_id AS neighborhood_id,
    EXTRACT(MONTH FROM c.updated_at) AS month,
    SUM(CASE WHEN c.category = 'violent' THEN c.total_number_cases ELSE 0 END) AS violent_crimes,
    SUM(CASE WHEN c.category = 'property' THEN c.total_number_cases ELSE 0 END) AS property_crimes
FROM
    crime_statistics c
JOIN
    regional_statistics r ON c.neighborhood = r.neighborhood AND c.year = r.year
WHERE
    c.updated_at BETWEEN CURRENT_DATE - INTERVAL '3 months' AND CURRENT_DATE
GROUP BY
    c.area_id, EXTRACT(MONTH FROM c.updated_at)
"""