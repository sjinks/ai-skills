Read this when walking users through `vip dev-env create`.

# Create a VIP Local Development Environment

Risk level
- Level: Medium
- Why: Creates and configures runtime state; low data-loss risk but networking can be misconfigured.
- Controls: Apply controls from `references/security.md`.

Prereqs
- VIP-CLI installed and up to date.
- Docker Desktop (or alternative) installed.
- macOS: Xcode Command Line Tools (`xcode-select --install`).
- Windows: WSL2 with Docker Desktop; run `vip dev-env` from the WSL distro shell.

Safety and naming
- Choose a unique slug to avoid collisions with existing local environments.
- Keep default localhost networking unless remote/LAN access is explicitly required.

Create basic environment
- `vip dev-env create --slug=<slug>`
- Walk through wizard options: site title, multisite, PHP version, WordPress version, app-code source, enable Elasticsearch, phpMyAdmin, Xdebug, Mailpit, Photon, Cron.

CLI-backed create details
- Accepted values and defaults for `--multisite`, `--php`, and `--wordpress` drift between VIP-CLI releases; confirm the current options with `vip dev-env create --help` before proposing flag values.
- `--multisite` selects single vs subdirectory/subdomain multisite, `--php` selects the PHP runtime, and `--wordpress` selects the WordPress version (for example a major version or `latest`).
- `vip @<app>.<env> dev-env create --slug=<slug>` can seed local configuration from a VIP Platform environment.
- Create prepares the environment, but the environment still needs `vip dev-env start --slug=<slug>` before exec, shell, import, or sync workflows.

Notes
- Successful create prints "environment created".
- Environment is created but not running until started.
- Validate URLs and services with `vip dev-env info --slug=<slug>` after first start.

Common create-time errors and fixes
1) `Environment already exists`
- Start the existing env with `vip dev-env start --slug=<slug>`.
- Use a different unique slug if a second env is intended.

2) `failed to fetch application "<app>" information`
- Treat this as a warning path. VIP-CLI can still continue with local prompts.
- Confirm the app/environment name and user access if remote defaults were expected.

3) `Configuration file ... could not be loaded` or `invalid configuration-version key`
- Fix `vip-dev-env.yml` before rerunning.
- Minimum valid shape is:
  - `configuration-version: 1`
  - `slug: <slug>`

4) `Unknown or unsupported PHP version:` or `Unknown or unsupported WordPress version:`
- Remove the invalid flag and use a supported version from the prompt.

5) `Provided path "..." does not point to a valid or existing directory.`
- Fix the absolute local path for `--app-code` or `--mu-plugins` before relying on it.

Helpful next command
- After create succeeds, start the env and optionally generate an editor workspace:
  - `vip dev-env start --slug=<slug>`
  - `vip dev-env start --editor=vscode --slug=<slug>`
