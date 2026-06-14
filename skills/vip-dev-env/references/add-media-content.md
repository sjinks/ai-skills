Read this when media files need to be available locally in an LDE.

# Add media to a VIP Local Development Environment

Risk level
- Level: Medium
- Why: Media import changes local uploads state but is usually reversible.
- Controls: Apply controls from `references/security.md`.

Prereqs
- LDE is created and running.
- Recommended: load local app code first.

Limitations
- LDE does not include VIP File System; test VIP File System features on a non-prod VIP env.
- Proxying media from multisite with Access-Controlled Files is not supported.

Find uploads/ location
- `vip dev-env info --slug=<slug>`
- Use the `LOCATION` value; uploads live at:
  - `<LOCATION>/uploads/`

Import local uploads
- `vip dev-env import media /absolute/path/uploads --slug=<slug>`

Common media import error and fix
1) `The provided path does not exist or it is not valid (see "--help" for examples)`
- `import media` takes a directory path, not a file; confirm the path exists and points to a directory of media files.
- Prefer an absolute path if the current working directory is uncertain.

Proxy media from a VIP Platform environment
- Use `--media-redirect-domain` to point at the platform domain.
- Example create:
  - `vip dev-env create --slug=<slug> --media-redirect-domain=www.example.com`
- Example update:
  - `vip dev-env update --slug=<slug> --media-redirect-domain=www.example.com`
