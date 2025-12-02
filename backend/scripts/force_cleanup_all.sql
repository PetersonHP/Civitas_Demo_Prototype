-- Nuclear cleanup - drops everything civitas-related
-- Use this when you need to completely start fresh

-- Drop all indexes explicitly (CASCADE will remove dependencies)
DROP INDEX IF EXISTS idx_support_crew_location_coordinates CASCADE;
DROP INDEX IF EXISTS idx_ticket_location_coordinates CASCADE;

-- Drop all tables with CASCADE (this will drop all dependent objects)
DROP TABLE IF EXISTS ticket_user_assignees_association CASCADE;
DROP TABLE IF EXISTS ticket_update_log CASCADE;
DROP TABLE IF EXISTS ticket_labels_association CASCADE;
DROP TABLE IF EXISTS ticket_crew_assignees_association CASCADE;
DROP TABLE IF EXISTS ticket_comment CASCADE;
DROP TABLE IF EXISTS user_roles_association CASCADE;
DROP TABLE IF EXISTS ticket CASCADE;
DROP TABLE IF EXISTS label CASCADE;
DROP TABLE IF EXISTS crew_members_association CASCADE;
DROP TABLE IF EXISTS crew_leads_association CASCADE;
DROP TABLE IF EXISTS support_crew CASCADE;
DROP TABLE IF EXISTS civitas_user CASCADE;
DROP TABLE IF EXISTS civitas_role CASCADE;

-- Drop all enum types with CASCADE
DROP TYPE IF EXISTS supportcrewstatus CASCADE;
DROP TYPE IF EXISTS supportcrewtype CASCADE;
DROP TYPE IF EXISTS ticketpriority CASCADE;
DROP TYPE IF EXISTS ticketstatus CASCADE;
DROP TYPE IF EXISTS ticketorigin CASCADE;
DROP TYPE IF EXISTS userstatus CASCADE;

-- Clean up any remaining geometry_columns entries (PostGIS metadata)
DELETE FROM geometry_columns WHERE f_table_name IN ('ticket', 'support_crew');
