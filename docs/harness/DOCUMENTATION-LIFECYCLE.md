# Project documentation lifecycle

Every task classifies documentation impact as `none`, `technical`, `user_manual`, or `both` and records a reason. Documentation may be updated at a coherent milestone instead of after each micro edit, but no required update may cross an official release gate.

Technical documentation changes with architecture, APIs, data, configuration, security, build/test, deployment, rollback, observability, recovery, operations, migration, or support. The user manual changes with features, navigation, workflows, permissions, feedback, errors, recovery, accessibility, or support behavior.

`docs/TECHNICAL-DOCUMENTATION.md` and `docs/USER-MANUAL.md` are canonical entrypoints. They may link to focused documents rather than growing without bound. Official release requires a current product version, owner, review date, required coverage, resolved local links, no placeholders, and consistency with the truth index and released evidence.

Release artifacts should contain the reviewed documentation for that version. A Git tag may preserve history when a trustworthy version-control workflow exists; otherwise retain the documentation inside the immutable release artifact and record its digest.
