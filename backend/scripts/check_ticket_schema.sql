-- Check the ticket table schema
\d ticket

-- Check enum types
SELECT unnest(enum_range(NULL::ticketorigin)) as origin_values;
SELECT unnest(enum_range(NULL::ticketstatus)) as status_values;
SELECT unnest(enum_range(NULL::ticketpriority)) as priority_values;
