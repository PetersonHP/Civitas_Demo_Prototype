-- Cleanup script for civitas schema
-- Run this if the migration fails and you need to start fresh

-- Drop indexes first (before dropping tables)
DROP INDEX IF EXISTS idx_support_crew_location_coordinates;
DROP INDEX IF EXISTS idx_ticket_location_coordinates;
DROP INDEX IF EXISTS ix_ticket_user_assignees_association_ticket_id;
DROP INDEX IF EXISTS ix_ticket_user_assignees_association_user_id;
DROP INDEX IF EXISTS ix_ticket_update_log_user_of_origin;
DROP INDEX IF EXISTS ix_ticket_update_log_update_log_id;
DROP INDEX IF EXISTS ix_ticket_update_log_ticket_id;
DROP INDEX IF EXISTS ix_ticket_comment_ticket_id;
DROP INDEX IF EXISTS ix_ticket_comment_commenter;
DROP INDEX IF EXISTS ix_ticket_comment_comment_id;
DROP INDEX IF EXISTS ix_ticket_ticket_id;
DROP INDEX IF EXISTS ix_ticket_reporter_id;
DROP INDEX IF EXISTS ix_label_label_name;
DROP INDEX IF EXISTS ix_label_label_id;
DROP INDEX IF EXISTS ix_label_created_by;
DROP INDEX IF EXISTS ix_support_crew_team_name;
DROP INDEX IF EXISTS ix_support_crew_team_id;
DROP INDEX IF EXISTS ix_civitas_user_user_id;
DROP INDEX IF EXISTS ix_civitas_user_phone_number;
DROP INDEX IF EXISTS ix_civitas_user_google_id;
DROP INDEX IF EXISTS ix_civitas_user_email;
DROP INDEX IF EXISTS ix_civitas_role_role_name;

-- Drop all tables (in reverse dependency order)
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

-- Drop enum types
DROP TYPE IF EXISTS supportcrewstatus CASCADE;
DROP TYPE IF EXISTS supportcrewtype CASCADE;
DROP TYPE IF EXISTS ticketpriority CASCADE;
DROP TYPE IF EXISTS ticketstatus CASCADE;
DROP TYPE IF EXISTS ticketorigin CASCADE;
DROP TYPE IF EXISTS userstatus CASCADE;

-- Note: PostGIS extension is left enabled as it may be used by other parts of the system
-- If you want to remove it, uncomment the line below:
-- DROP EXTENSION IF EXISTS postgis CASCADE;
