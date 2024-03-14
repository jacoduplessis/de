# Anglo AMB Defect Elimination Tool

## Setup

- Load data fixtures in the following order:

> python manage.py loaddata defects/fixtures/groups.json
> python manage.py loaddata defects/fixtures/users.json

- Create Operations, Areas and Sections in Admin

> python manage.py generate_fake_data 100

## Technical Questions

- OS / VPS
- 2Gb Ram
- docker available / install?
- network limitations / firewalls
- access to server / VPN,
- SMTP server
- SSO / AD
- storage
- backups

## Hardware Requirements

Windows Server 2019/2022
MS SQL Server 2019/2022
4GB Ram
2 CPU cores
MS IIS
MS WSL

## Application Questions

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
- fonts / Arial? ATM it uses dejavu sans on the server

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
- indication that filters are active
- clear filters button
- mark solution as verified
- add solution verification comment

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

## notes

- rand value calculated
- script the demo
- prepare data for input to save time
- end with value graph to tie it up
- actively search incident database - maintains referential integrity and allows for deeper data analysis
- search "distributor"

## Application Questions

- taxonomy clarification: operation, section, area
- how are the dates for short, medium and long term solution calculated
- what is solution priority
- where can we retrieve data relating to market price of platinum group metals
- dashboards (compliance, value, home)
- values / units
- close-out process


## todo

Issues

35
30
29
28
25
22
14
6

- add user details to comments in timeline


