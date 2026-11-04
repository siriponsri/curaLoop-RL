# Security and data boundaries

The released application is a single-owner localhost research tool. Run it on loopback with one active server/worker. It is not designed as an authenticated public service, tenant-isolated platform or arbitrary-code sandbox. Keep proprietary libraries, confidential outcomes, credentials and local databases outside public Git.

Do not post sensitive vulnerability details or customer records in public issues. Use GitHub private vulnerability reporting if it is enabled; otherwise contact the repository owner through an already established private channel to agree a disclosure route. No security email or response SLA is asserted here.

For accidental exposure, stop the affected workflow, preserve relevant evidence, remove unauthorized access through the responsible account owner and assess the actual data involved. Do not erase logs or reset databases merely to hide an error. Customer-specific incident duties and access controls must be agreed before a proprietary-data pilot.

A later networked or regulated deployment needs a separate threat model and validation plan. The current package does not establish penetration-test coverage or enterprise readiness.
