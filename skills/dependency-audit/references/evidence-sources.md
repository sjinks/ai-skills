# Evidence Sources By Ecosystem

Read this when locating manifest, lockfile, audit-report, SBOM, and provenance evidence for a specific ecosystem.


- JavaScript/TypeScript/npm/pnpm/yarn/Bun/Deno: `package.json`, `package-lock.json`, `npm-shrinkwrap.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `yarn.lock`, `bun.lock`, `bun.lockb`, `deno.json`, `deno.lock`, workspace files, `turbo.json`, `nx.json`, package-manager audit reports, `npm ls` or package-manager tree output when explicitly provided.
- Python/pip/uv/poetry: `pyproject.toml`, `setup.cfg`, `setup.py`, `requirements*.txt`, `Pipfile.lock`, `uv.lock`, `poetry.lock`, pip-audit/safety reports, wheel metadata when provided.
- Rust/cargo: `Cargo.toml`, `Cargo.lock`, cargo-audit or RustSec reports, crate features, target-specific dependencies.
- Go modules: `go.mod`, `go.sum`, module graph output, govulncheck output, replaced modules, vendored modules.
- Java/Maven/Gradle: `pom.xml`, Maven lock or effective dependency output, `build.gradle`, `gradle.lockfile`, dependency-check reports, plugin dependencies.
- .NET/NuGet: `*.csproj`, `Directory.Packages.props`, `packages.lock.json`, NuGet audit output, central package management files.
- Ruby/Bundler: `Gemfile`, `Gemfile.lock`, bundler-audit reports, platform-specific gems.
- PHP/Composer: `composer.json`, `composer.lock`, composer audit output, plugin configuration.
- Container/OS packages when explicitly in scope: Dockerfiles, image lock/SBOM files, package manager manifests, base image digest, distro advisory output, and scanner report provenance.
- SBOM and provenance artifacts when available: CycloneDX, SPDX, SLSA or in-toto attestations, build provenance, signature verification output, checksum manifests, vendored dependency directories, generated artifacts, and package metadata snapshots.

