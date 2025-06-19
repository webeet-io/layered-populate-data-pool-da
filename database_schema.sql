-- Berlin Crime Statistics Database Schema
-- Step 1: Data Modeling Phase
-- This schema defines the planned database structure for crime statistics integration

-- =============================================================================
-- MAIN TABLES
-- =============================================================================

-- Crime Statistics - Primary table for Berlin crime data
CREATE TABLE crime_statistics (
    id SERIAL PRIMARY KEY,
    area_id VARCHAR(20) NOT NULL,                    -- LOR area identifier (e.g., "1011303")
    area_name VARCHAR(255) NOT NULL,                 -- Human readable name (e.g., "Alexanderplatzviertel")
    area_type VARCHAR(50) NOT NULL,                  -- 'district', 'district_region', 'planning_area'
    bezirk_id VARCHAR(10),                          -- District ID (1-12)
    bezirk_name VARCHAR(100),                       -- District name (e.g., "Mitte")
    crime_type VARCHAR(100) NOT NULL,               -- Standardized crime category
    crime_type_german VARCHAR(100),                 -- Original German crime type
    year INTEGER NOT NULL,                          -- Year of data
    absolute_cases INTEGER NOT NULL,                -- Total number of reported cases
    frequency_per_100k FLOAT NOT NULL,             -- Cases per 100,000 inhabitants
    population_base INTEGER,                        -- Population used for frequency calculation
    coordinates GEOMETRY(POINT, 4326),             -- Geographic center of area (WGS84)
    area_km2 FLOAT,                                -- Area size in square kilometers
    data_source VARCHAR(50) DEFAULT 'crime_atlas', -- Source identifier
    data_quality VARCHAR(20) DEFAULT 'verified',   -- 'verified', 'interpolated', 'estimated'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT crime_stats_unique UNIQUE(area_id, crime_type, year),
    CONSTRAINT crime_stats_cases_positive CHECK (absolute_cases >= 0),
    CONSTRAINT crime_stats_frequency_positive CHECK (frequency_per_100k >= 0),
    CONSTRAINT crime_stats_year_valid CHECK (year >= 2000 AND year <= 2030),
    CONSTRAINT crime_stats_area_type_valid CHECK (area_type IN ('district', 'district_region', 'planning_area'))
);

-- Emergency Services - Fire department and emergency response data
CREATE TABLE emergency_services (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(50) UNIQUE NOT NULL,        -- Unique incident identifier
    call_datetime TIMESTAMP NOT NULL,               -- When emergency call was received
    incident_type VARCHAR(50) NOT NULL,             -- 'fire', 'medical', 'technical', 'other'
    incident_subtype VARCHAR(100),                  -- More specific categorization
    response_time_minutes FLOAT,                    -- Time from call to first vehicle arrival
    area_id VARCHAR(20),                           -- LOR area identifier (FK)
    coordinates GEOMETRY(POINT, 4326),             -- Incident location (may be anonymized)
    address_anonymized VARCHAR(255),               -- Anonymized address for privacy
    units_dispatched INTEGER,                      -- Number of emergency units sent
    resolution_time_minutes FLOAT,                -- Total incident duration
    severity_level VARCHAR(20),                   -- 'low', 'medium', 'high', 'critical'
    outcome VARCHAR(50),                          -- 'resolved', 'referred', 'ongoing'
    data_source VARCHAR(50) DEFAULT 'berlin_fire', -- Source identifier
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT emergency_response_time_valid CHECK (response_time_minutes >= 0),
    CONSTRAINT emergency_units_positive CHECK (units_dispatched > 0),
    CONSTRAINT emergency_incident_type_valid CHECK (incident_type IN ('fire', 'medical', 'technical', 'other')),
    CONSTRAINT emergency_severity_valid CHECK (severity_level IN ('low', 'medium', 'high', 'critical'))
);

-- Demographics - Supporting demographic and socioeconomic data
CREATE TABLE demographics (
    id SERIAL PRIMARY KEY,
    area_id VARCHAR(20) NOT NULL,                   -- LOR area identifier
    year INTEGER NOT NULL,                          -- Year of demographic data
    total_population INTEGER NOT NULL,              -- Total registered residents
    population_density_per_km2 FLOAT,              -- Population density
    area_km2 FLOAT,                                -- Area size for density calculation
    
    -- Age distribution
    age_group_0_18 INTEGER,                        -- Population under 18
    age_group_18_65 INTEGER,                       -- Working age population (18-64)
    age_group_65_plus INTEGER,                     -- Senior population (65+)
    
    -- Migration and diversity
    migration_background_total INTEGER,            -- Total with migration background
    migration_background_pct FLOAT,               -- Percentage with migration background
    eu_citizens INTEGER,                          -- EU citizens count
    non_eu_citizens INTEGER,                      -- Non-EU citizens count
    
    -- Economic indicators
    unemployment_rate FLOAT,                      -- Local unemployment rate
    social_assistance_recipients INTEGER,          -- People receiving social assistance
    
    -- Housing
    total_households INTEGER,                     -- Number of households
    avg_household_size FLOAT,                    -- Average people per household
    
    data_source VARCHAR(50) DEFAULT 'berlin_stats', -- Source identifier
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT demographics_unique UNIQUE(area_id, year),
    CONSTRAINT demographics_population_positive CHECK (total_population > 0),
    CONSTRAINT demographics_year_valid CHECK (year >= 2000 AND year <= 2030),
    CONSTRAINT demographics_percentages_valid CHECK (migration_background_pct >= 0 AND migration_background_pct <= 100)
);

-- =============================================================================
-- LOOKUP AND MAPPING TABLES
-- =============================================================================

-- Area Hierarchy - Maps relationships between different spatial units
CREATE TABLE area_hierarchy (
    id SERIAL PRIMARY KEY,
    area_id VARCHAR(20) NOT NULL,                  -- Child area ID
    parent_area_id VARCHAR(20),                    -- Parent area ID
    hierarchy_level INTEGER NOT NULL,              -- 1=district, 2=district_region, 3=planning_area
    area_name VARCHAR(255) NOT NULL,
    area_type VARCHAR(50) NOT NULL,
    coordinates GEOMETRY(POINT, 4326),            -- Area centroid
    boundary_geom GEOMETRY(MULTIPOLYGON, 4326),   -- Area boundary (if available)
    
    CONSTRAINT area_hierarchy_level_valid CHECK (hierarchy_level BETWEEN 1 AND 3)
);

-- Crime Type Mapping - Translation and standardization of crime categories
CREATE TABLE crime_type_mapping (
    id SERIAL PRIMARY KEY,
    german_name VARCHAR(200) NOT NULL UNIQUE,      -- Original German crime type
    english_name VARCHAR(200) NOT NULL,            -- Standardized English name
    category VARCHAR(100) NOT NULL,                -- High-level category
    severity_weight FLOAT DEFAULT 1.0,             -- Weight for safety score calculation
    public_safety_relevance BOOLEAN DEFAULT TRUE,  -- Whether relevant for public safety
    description_german TEXT,                       -- German description
    description_english TEXT,                      -- English description
    
    CONSTRAINT crime_mapping_weight_valid CHECK (severity_weight >= 0)
);

-- Neighborhood Crime Context - Links listings/neighborhoods to crime data
CREATE TABLE neighborhood_crime_context (
    id SERIAL PRIMARY KEY,
    neighborhood_id INTEGER,                       -- FK to existing neighborhoods table
    listing_id INTEGER,                           -- FK to existing listings table (optional)
    area_id VARCHAR(20) NOT NULL,                 -- FK to crime_statistics area_id
    distance_meters FLOAT,                        -- Distance from listing/neighborhood to crime area
    safety_score FLOAT,                          -- Calculated safety metric (0-100, higher = safer)
    crime_risk_level VARCHAR(20),                -- 'very_low', 'low', 'medium', 'high', 'very_high'
    last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT safety_score_valid CHECK (safety_score >= 0 AND safety_score <= 100),
    CONSTRAINT crime_risk_valid CHECK (crime_risk_level IN ('very_low', 'low', 'medium', 'high', 'very_high'))
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Spatial indexes
CREATE INDEX idx_crime_statistics_coordinates ON crime_statistics USING GIST(coordinates);
CREATE INDEX idx_emergency_services_coordinates ON emergency_services USING GIST(coordinates);
CREATE INDEX idx_area_hierarchy_coordinates ON area_hierarchy USING GIST(coordinates);
CREATE INDEX idx_area_hierarchy_boundary ON area_hierarchy USING GIST(boundary_geom);

-- Query optimization indexes
CREATE INDEX idx_crime_statistics_area_year ON crime_statistics(area_id, year);
CREATE INDEX idx_crime_statistics_type_year ON crime_statistics(crime_type, year);
CREATE INDEX idx_crime_statistics_bezirk ON crime_statistics(bezirk_id, year);
CREATE INDEX idx_emergency_services_datetime ON emergency_services(call_datetime);
CREATE INDEX idx_emergency_services_area ON emergency_services(area_id, call_datetime);
CREATE INDEX idx_demographics_area_year ON demographics(area_id, year);

-- Text search indexes
CREATE INDEX idx_crime_statistics_area_name ON crime_statistics USING gin(to_tsvector('german', area_name));
CREATE INDEX idx_area_hierarchy_name ON area_hierarchy USING gin(to_tsvector('german', area_name));

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS
-- =============================================================================

-- Note: These would be added after confirming existing table structure
-- ALTER TABLE emergency_services ADD CONSTRAINT fk_emergency_area 
--     FOREIGN KEY (area_id) REFERENCES crime_statistics(area_id);
-- 
-- ALTER TABLE demographics ADD CONSTRAINT fk_demographics_area 
--     FOREIGN KEY (area_id) REFERENCES crime_statistics(area_id);
--
-- ALTER TABLE neighborhood_crime_context ADD CONSTRAINT fk_context_area
--     FOREIGN KEY (area_id) REFERENCES crime_statistics(area_id);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Safety summary by district
CREATE OR REPLACE VIEW district_safety_summary AS
SELECT 
    cs.bezirk_name,
    cs.year,
    COUNT(*) as total_crime_types,
    SUM(cs.absolute_cases) as total_crimes,
    AVG(cs.frequency_per_100k) as avg_frequency_per_100k,
    d.total_population,
    ROUND(SUM(cs.absolute_cases)::NUMERIC / d.total_population * 100000, 2) as overall_crime_rate
FROM crime_statistics cs
LEFT JOIN demographics d ON cs.area_id = d.area_id AND cs.year = d.year
WHERE cs.area_type = 'district'
GROUP BY cs.bezirk_name, cs.year, d.total_population
ORDER BY cs.bezirk_name, cs.year;

-- Recent emergency response metrics
CREATE OR REPLACE VIEW emergency_response_summary AS
SELECT 
    DATE_TRUNC('month', call_datetime) as month,
    incident_type,
    COUNT(*) as total_incidents,
    AVG(response_time_minutes) as avg_response_time,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_minutes) as median_response_time,
    COUNT(CASE WHEN severity_level IN ('high', 'critical') THEN 1 END) as high_severity_count
FROM emergency_services
WHERE call_datetime >= CURRENT_DATE - INTERVAL '2 years'
GROUP BY DATE_TRUNC('month', call_datetime), incident_type
ORDER BY month DESC, incident_type;

-- =============================================================================
-- INITIAL DATA VALIDATION FUNCTIONS
-- =============================================================================

-- Function to validate area_id format (should match LOR system)
CREATE OR REPLACE FUNCTION validate_area_id(area_id TEXT) RETURNS BOOLEAN AS $$
BEGIN
    -- LOR area IDs are typically 7 digits: BPGBNPR
    -- B=Bezirk(1), PG=Prognoseraum(2), BN=Bezirksregion(2), PR=Planungsraum(2)
    RETURN area_id ~ '^[0-9]{7}$' OR area_id ~ '^[0-9]{1,2}$';
END;
$$ LANGUAGE plpgsql;

-- Function to calculate safety score based on crime statistics
CREATE OR REPLACE FUNCTION calculate_safety_score(
    area_id_param VARCHAR(20), 
    year_param INTEGER
) RETURNS FLOAT AS $$
DECLARE
    safety_score FLOAT;
    total_weighted_crimes FLOAT;
    population INTEGER;
BEGIN
    -- Get population for the area
    SELECT total_population INTO population 
    FROM demographics 
    WHERE area_id = area_id_param AND year = year_param;
    
    -- Calculate weighted crime score
    SELECT COALESCE(SUM(cs.absolute_cases * ctm.severity_weight), 0) INTO total_weighted_crimes
    FROM crime_statistics cs
    JOIN crime_type_mapping ctm ON cs.crime_type = ctm.english_name
    WHERE cs.area_id = area_id_param 
    AND cs.year = year_param
    AND ctm.public_safety_relevance = TRUE;
    
    -- Calculate safety score (higher = safer)
    IF population > 0 THEN
        safety_score := GREATEST(0, 100 - (total_weighted_crimes / population * 10000));
    ELSE
        safety_score := NULL;
    END IF;
    
    RETURN safety_score;
END;
$$ LANGUAGE plpgsql;