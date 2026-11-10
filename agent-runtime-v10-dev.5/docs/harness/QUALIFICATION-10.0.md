# GAR 10 qualification

Status: BLOCKED development candidate (2026-11-10). GAR 10 is not officially
released. The package's build date is 2026-11-10; its release date is null.
Candidate source and ZIP hashes, exact command exits, skips, and artifact
provenance belong in the active root qualification task and final run report.

Current mandatory blockers from the 2026-10-12 qualification report:

- Security: host loopback isolation check failed; Bandit reported 49 low
  findings, including 13 runtime findings not fully triaged; independent
  security review and authenticity/provenance evidence are not verified.
- Human comprehension: representative user comprehension evidence remains
  unverified.
- Code quality: a fresh full regression run on the release candidate is
  required; predecessor results do not qualify changed package/docs metadata.
- Observability/release: fresh final artifact provenance and clean extraction
  evidence are required.
- UX: human comprehension remains unverified; no GUI exists in GAR itself,
  so visual UI review is not applicable to this release.

Local structural and package checks do not clear these independent blockers.
Do not tag, publish, or describe GAR 10 as officially released while a required
gate is blocked or not verified. No production approval is implied.

Human comprehension, live host interception, real qualified external tool execution, complete frozen GAR9 behavioral repetitions and full GAR10 comparative evaluation remain independently required. Native report profiles are parser contracts, not proof of exact tool compatibility.
