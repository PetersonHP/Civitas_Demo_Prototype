# PowerShell script to import tickets to Heroku
Get-Content "backend\scripts\insert_20_tickets.sql" | heroku pg:psql --app=civitas-demo
