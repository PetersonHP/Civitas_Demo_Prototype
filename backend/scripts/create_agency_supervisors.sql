-- SQL Script to Create Supervisor Users for NYC 311 Agencies
-- Run this in pgAdmin

-- First, ensure the supervisor role exists (if it doesn't already)
INSERT INTO civitas_role (role_id, role_name)
VALUES (gen_random_uuid(), 'supervisor')
ON CONFLICT (role_name) DO NOTHING;

-- Insert supervisor users for each agency
INSERT INTO civitas_user (
    user_id,
    firstname,
    lastname,
    email,
    phone_number,
    status,
    time_created,
    meta_data
) VALUES
    -- DEP - Department of Environmental Protection
    (gen_random_uuid(), 'David', 'Martinez', 'david.martinez@dep.nyc.gov', '212-555-0101', 'ACTIVE', NOW(), '{"agency": "DEP", "agency_name": "Department of Environmental Protection"}'::jsonb),

    -- DHS - Department of Homeless Services
    (gen_random_uuid(), 'Sarah', 'Johnson', 'sarah.johnson@dhs.nyc.gov', '212-555-0102', 'ACTIVE', NOW(), '{"agency": "DHS", "agency_name": "Department of Homeless Services"}'::jsonb),

    -- DOB - Department of Buildings
    (gen_random_uuid(), 'Michael', 'Chen', 'michael.chen@buildings.nyc.gov', '212-555-0103', 'ACTIVE', NOW(), '{"agency": "DOB", "agency_name": "Department of Buildings"}'::jsonb),

    -- DOE - Department of Education
    (gen_random_uuid(), 'Emily', 'Rodriguez', 'emily.rodriguez@schools.nyc.gov', '212-555-0104', 'ACTIVE', NOW(), '{"agency": "DOE", "agency_name": "Department of Education"}'::jsonb),

    -- DOHMH - Department of Health and Mental Hygiene
    (gen_random_uuid(), 'James', 'Thompson', 'james.thompson@health.nyc.gov', '212-555-0105', 'ACTIVE', NOW(), '{"agency": "DOHMH", "agency_name": "Department of Health and Mental Hygiene"}'::jsonb),

    -- DOT - Department of Transportation
    (gen_random_uuid(), 'Lisa', 'Anderson', 'lisa.anderson@dot.nyc.gov', '212-555-0106', 'ACTIVE', NOW(), '{"agency": "DOT", "agency_name": "Department of Transportation"}'::jsonb),

    -- DPR - Department of Parks and Recreation
    (gen_random_uuid(), 'Robert', 'Williams', 'robert.williams@parks.nyc.gov', '212-555-0107', 'ACTIVE', NOW(), '{"agency": "DPR", "agency_name": "Department of Parks and Recreation"}'::jsonb),

    -- DSNY - Department of Sanitation
    (gen_random_uuid(), 'Jennifer', 'Davis', 'jennifer.davis@dsny.nyc.gov', '212-555-0108', 'ACTIVE', NOW(), '{"agency": "DSNY", "agency_name": "Department of Sanitation"}'::jsonb),

    -- EDC - Economic Development Corporation
    (gen_random_uuid(), 'Thomas', 'Garcia', 'thomas.garcia@edc.nyc', '212-555-0109', 'ACTIVE', NOW(), '{"agency": "EDC", "agency_name": "Economic Development Corporation"}'::jsonb),

    -- OOS - Office of the Sheriff
    (gen_random_uuid(), 'Patricia', 'Miller', 'patricia.miller@sheriff.nyc.gov', '212-555-0110', 'ACTIVE', NOW(), '{"agency": "OOS", "agency_name": "Office of the Sheriff"}'::jsonb)
ON CONFLICT (email) DO NOTHING;

-- Assign supervisor role to all newly created supervisor users
INSERT INTO user_roles_association (user_id, role_id)
SELECT
    cu.user_id,
    cr.role_id
FROM civitas_user cu
CROSS JOIN civitas_role cr
WHERE cr.role_name = 'supervisor'
  AND cu.email IN (
    'david.martinez@dep.nyc.gov',
    'sarah.johnson@dhs.nyc.gov',
    'michael.chen@buildings.nyc.gov',
    'emily.rodriguez@schools.nyc.gov',
    'james.thompson@health.nyc.gov',
    'lisa.anderson@dot.nyc.gov',
    'robert.williams@parks.nyc.gov',
    'jennifer.davis@dsny.nyc.gov',
    'thomas.garcia@edc.nyc',
    'patricia.miller@sheriff.nyc.gov'
  )
ON CONFLICT DO NOTHING;

-- Verify the inserted users
SELECT
    cu.firstname,
    cu.lastname,
    cu.email,
    cu.phone_number,
    cu.meta_data->>'agency' as agency_code,
    cu.meta_data->>'agency_name' as agency_name,
    cr.role_name
FROM civitas_user cu
LEFT JOIN user_roles_association ura ON cu.user_id = ura.user_id
LEFT JOIN civitas_role cr ON ura.role_id = cr.role_id
WHERE cu.email LIKE '%@%.nyc.gov' OR cu.email LIKE '%@edc.nyc'
ORDER BY cu.meta_data->>'agency';
