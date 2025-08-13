"""SQL queries for green spaces segmentation"""

GREEN_SPACES_QUERY = """
SELECT
    g.neighborhood,
    COUNT(g.technical_id) AS num_green_spaces,
    SUM(g.size_sqm) AS total_green_area,
    r.inhabitants AS population
FROM
    test_berlin_data.green_spaces g
LEFT JOIN
    test_berlin_data.regional_statistics r ON g.neighborhood = r.neighborhood
GROUP BY
    g.neighborhood, r.inhabitants
"""