Read this when domains do not resolve, when using a custom domain, or when multiple LDEs run at once.

# Networking and custom domains

Risk level
- Level: Mixed (Medium/High)
- Why: Domain and routing changes are medium risk; changing bind address beyond localhost is high risk.
- Controls: Apply controls from `references/security.md`.

Core behavior
- Traefik routes traffic based on the full domain name to the correct LDE.
- Multiple LDEs can run simultaneously if each has a unique `--slug`.
- Default domain pattern: `<slug>.vipdev.lndo.site`.
- Safer default: keep traffic bound to localhost unless LAN access is explicitly required.

Custom domains (global)
- Custom domain config applies to all LDEs on the machine.
- The global Lando config file lives in the VIP-CLI data directory, whose base path is platform- and version-dependent (commonly `~/.local/share/vip` on Linux/WSL2); discover it rather than assuming. The file is at `<vip-data-dir>/lando/config.yml`.
- Create or update that `lando/config.yml` with:
  - `domain: example-domain.com`
- Create the environment after setting the domain so it uses `<slug>.example-domain.com`.
- If a custom domain is set after existing envs, those envs may become unreachable.
- If this happens, recreate affected envs so routes are regenerated for the new domain.

DNS / hosts resolution
- Custom domains must resolve to the local bind address (default `127.0.0.1`).
- If DNS is not set up, add entries to the hosts file as instructed by VIP-CLI warnings.
- Example hosts entries:
  - `127.0.0.1 <slug>.example-domain.com`
  - `127.0.0.1 <slug>-pma.example-domain.com` (phpMyAdmin)
  - `127.0.0.1 <slug>-mailpit.example-domain.com` (Mailpit)

Bind address override
- LDE can bind to a different host IP using:
  - the same `<vip-data-dir>/lando/config.yml` with `bindAddress: "0.0.0.0"` (or another IP)
- When bindAddress is set, DNS/hosts must resolve to that IP, not `127.0.0.1`.
- Security note: `0.0.0.0` exposes services on all interfaces. Prefer a specific local IP and trusted network only.

Useful command
- `vip dev-env info --slug=<slug>` shows service URLs and ports.

Troubleshooting checklist
1) `vip dev-env info --slug=<slug>` and verify expected domain.
2) Check `<vip-data-dir>/lando/config.yml` (commonly under `~/.local/share/vip` on Linux/WSL2) for `domain` and `bindAddress`.
3) Ensure hosts/DNS entries point to the configured bind address.
4) Confirm another LDE is not using the same slug.

Common networking warnings and fixes
1) `WARNING: Failed to resolve <domain>: <message>`
- Add the suggested hosts entry for the domain.
- Re-check that DNS/hosts points to the configured `bindAddress`.

2) `WARNING: <domain> resolves to <ip> instead of 127.0.0.1.`
- If using the default config, point the domain back to `127.0.0.1`.
- If using a custom `bindAddress`, ensure the hostname resolves to that exact IP instead.

3) Wrong env opens in browser
- Confirm the slug-specific hostname from `vip dev-env info --slug=<slug>`.
- Recreate the env only if global domain settings changed after the env was created.
