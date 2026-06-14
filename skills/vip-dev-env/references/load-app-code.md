Read this when pointing an LDE at a local git clone.

# Load application code into a local environment

Risk level
- Level: Medium
- Why: Rewires mounted app code and can change runtime behavior unexpectedly.
- Controls: Apply controls from `references/security.md`.

Prereqs
- LDE is created and running.
- git installed.
- Confirm you know the target slug before running update commands.

Steps
1) Clone the app repo (wpcomvip GitHub):
   - `git clone git@github.com:wpcomvip/<repo>.git`
2) Identify the absolute path to the local repo.
3) Update the LDE to use local app code:
   - `vip dev-env update --app-code=/absolute/path/to/repo --slug=<slug>`
4) Restart the environment:
   - `vip dev-env start --slug=<slug>`
5) Confirm in browser:
   - Use NGINX URL from `vip dev-env info --slug=<slug>`
   - Use LOGIN URL for wp-admin

Notes
- Code changes in the local repo apply immediately without restarting.
- Branch switching is handled by git, not VIP-CLI.

Troubleshooting
1) If code does not update, verify the absolute path and repo branch/worktree.
2) Re-run `vip dev-env update --app-code=/absolute/path/to/repo --slug=<slug>`.
3) Check PHP/NGINX logs if behavior still differs from expected code state.

Common update-path errors and fixes
1) `Provided path "..." does not point to a valid or existing directory.`
- Fix the path first. VIP-CLI warns and drops the invalid `--app-code` value.
- Prefer an absolute path to the repo root.

2) `Environment doesn't exist.`
- Confirm the slug with `vip dev-env list`.
- Create the env first if it does not exist.

3) `Environment was created before update was supported.`
- This older env should be destroyed and recreated after confirming local data impact.

4) `More than one environment found:`
- Re-run with `--slug=<slug>` explicitly.
