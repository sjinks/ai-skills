Read this when guiding repo structure or explaining what code is local vs in the container.

# WordPress skeleton (VIP repo layout)

- VIP app repo is based on `vip-go-skeleton`.
- Only specific paths deploy from the repo root; other root folders are ignored.
- The required/optional split below follows the official skeleton structure; verify against `https://docs.wpvip.com/wordpress-skeleton/` and the `Automattic/vip-go-skeleton` README, which document the directories in the "Required directories" list as required.

Required directories (must exist in the repo):
- `/client-mu-plugins`
- `/images`
- `/languages`
- `/plugins`
- `/private`
- `/themes`
- `/vip-config`

Optional in repo (can be removed):
- `/docs`
- `.editorconfig`
- `.phpcs.xml.dist`
- `composer.json`
- `composer.lock`

Local vs container code:
- App repo content is local (mounted into the dev environment).
- WordPress core and VIP MU plugins live in the container image and are not part of the repo.
