"""SQL queries for green spaces segmentation"""

GREEN_SPACES_QUERY = """
SELECT
    g.neighborhood,
    COUNT(g.technical_id) AS num_green_spaces,
    SUM(g.size_sqm) AS total_green_area,
    AVG(g.size_sqm) AS avg_park_size,  
    AVG(EXTRACT(YEAR FROM CURRENT_DATE) - g.last_renovation_year) AS avg_years_since_renovation,
    COALESCE(SUM(r.inhabitants), 1) AS population
FROM test_berlin_data.green_spaces g
LEFT JOIN test_berlin_data.regional_statistics r 
    ON g.neighborhood = r.neighborhood
GROUP BY g.neighborhood
"""