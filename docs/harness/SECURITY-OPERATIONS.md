# Secure Operations for Internet-Facing Hosts

The safest response to a confirmed cryptominer or remote-code-execution incident is not an in-place cleanup. Preserve evidence if required, isolate the host, revoke and rotate credentials from a clean system, rebuild from trusted images, restore only validated data, and monitor the replacement.

## Deployment boundary

- Run the application as a dedicated non-root identity with no interactive login.
- Prefer an immutable image and read-only root filesystem; write only to explicit volumes.
- Drop Linux capabilities, enable `no-new-privileges`, and use seccomp/AppArmor/SELinux where supported.
- Keep the database and control plane off the public network.
- Default-deny inbound traffic except through the reverse proxy; restrict outbound traffic to required destinations.
- Set CPU, memory, process, file-descriptor, and disk quotas. Alert on sustained CPU, unknown processes, outbound mining-pool traffic, and unexpected persistence.
- Keep runtime/framework versions pinned to the current dated policy and rebuild frequently.
- Store secrets outside the image and repository; use scoped, short-lived credentials.
- Separate build runners from production and never build untrusted pull requests with production credentials.

## Incident minimum

Record detection time, host identity, affected service, containment, credential scope, artifacts/hashes, persistence indicators, outbound destinations, recovery source, validation, and owner. Do not paste secrets or private customer data into Harness artifacts.

The Harness validates that these controls are considered and evidenced. Enforcement belongs in the VPS, container runtime, network, identity provider, CI/CD, and monitoring platform.
