# Anglo AMB Defect Elimination Tool

## Setup

- Load data fixtures in the following order:

  > python manage.py loaddata defects/fixtures/groups.json
  > python manage.py loaddata defects/fixtures/users.json

## Technical Questions

- OS
- docker available
- network limitations
- access to server
- SMTP server
- SSO / AD
- storage
- backups

## Application Questions

- "circulation to AS&R Team"
- areas, sections
- production cost (calculator, how it will be recorded)
- notifications / emails
- RELIABILITY INCIDENT EFFECT (dynamic, multi-choice?)
- incident status
- solution priority
- dates on close out slide solution categories

## TODO

- audit logging
- application logging
- edit locks
- background tasks
- add pagination to list views
- add ordering, searching to list views
- custom error templates
- render possible effect, production loss in notification html view and pdf
- integrate modals and forms with unpoly
- replace icons with BSI
- group creation
- setup logging
- prelim findings input
- figure out incident status
- permission checks

## Key Features

- home dashboard
- RI register
- notification reports
- close out slides
- upload of RCA
- approval in various stages of RI lifecycle
- recording of solutions
- solutions register
- value dashboard
- compliance dashboard
- anniversary tracker
- audit logging & viewing
- permission structure

## Demo

- add incident
- equipment select
- admin dashboard
- audit log
- edit incident
- groups created, user area
- unpoly ?
- feedback
- new icons
- about page
- fixtures
- image uploads and editing

- PDF generation
