# Export Controls for Reading Data

Data exports create a separate disclosure path and should not be added casually.

- Require authentication and authorization on any export endpoint.
- Limit date range and result count.
- Use a safe, explicit format and prevent spreadsheet formula injection in CSV exports.
- Set `Cache-Control: no-store` for sensitive responses.
- Record export metadata without recording the exported content.
- Avoid emailing exports or placing them in public CI artifacts.
- Define an expiry and deletion process for generated files.

The current project does not claim a general-purpose export feature; this checklist applies before one is implemented.
