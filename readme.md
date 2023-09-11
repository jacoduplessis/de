# Anglo AMB Defect Elimination Tool

## Setup

- Load data fixtures in the following order:

> python manage.py loaddata defects/fixtures/groups.json
> python manage.py loaddata defects/fixtures/users.json

- Create Operations, Areas and Sections in Admin

> python manage.py generate_fake_data 100

## Technical Questions

- OS / VPS
- docker available / install?
- network limitations
- access to server
- SMTP server
- SSO / AD
- storage
- backups

## Application Questions

- "circulation to AS&R Team"
- taxonomy: operation, areas, sections
- production cost (calculator, how it will be recorded)
- notifications / emails
- RELIABILITY INCIDENT EFFECT (select one)
- solution priority (not the same as short, med, long term)
- dates on close out slide solution categories
- extra fields for close out slide - immediate cause, root cause, images
- significant incident => RCA process triggered
- design of compliance dashboard - breakdown per area, section?
- anniversaries

- should user actions be dismissible
- fonts / Arial? ATM it uses dejavu sans on the serverr

## TODO

- audit logging
- application logging
- edit locks
- background tasks
- add pagination to list views ?
- add ordering, searching to list views
- custom error templates
- setup logging
- figure out incident status
- permission checks
- indicator that results are filtered.
- email links
- install fonts in container
- add test case that generates pdf
- global list of issues with incident data
- maps SRS permissions into concrete db permission / group entries

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
- duration calculation
- PDF generation
- approvals in SEM dashboard
- workflow for failed approval requests
- timezone management
- upload / download RCA report
- data generator
- register search
- filtering

#### after 2023-08-25

- add status to incident filters
- remove order button
- rename label of image ordering field
- automated tests
- user action framework
- start adding permission checks

## Performance Improvements

- search indexes


## Demo

engineering manager meeting
really important
10 minutes
thursday

2-3 min introduction
6 min demo


# notes

- rand value calculated
- script the demo
- prepare data for input to save time
- end with value graph to tie it up
