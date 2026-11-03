# Frontend tooling and dependency maintenance

UI development requires Node.js 22.13+ on the 22.x line, or Node.js 24+. The packaged localhost application does not require Node.js.

The November 2026 update uses ESLint 10.14.0, `@eslint/js` 10.0.1, `typescript-eslint` 8.72.1 and React Hooks plugin 7.1.1. The existing flat configuration remains active. ESLint's supported Node versions and configuration changes are described in the [official v10 migration guide](https://eslint.org/docs/latest/use/migrate-to-10.0.0).

`package.json` pins the transitive `minimatch` resolution to 11.0.1. [GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249) identifies versions below 11.0.1 as vulnerable to pattern amplification. At the time of this update, the installed ESLint/config-array and TypeScript ESTree dependency chain still requested an earlier major. This explicit override installs the patched implementation; it does not hide the advisory or disable scanning. Lint, TypeScript, unit tests and the production build must pass against the overridden dependency. Remove the override once the upstream supported dependency chain resolves a patched version itself, and rerun these checks.

Use `npm ci` for a reproducible installation, then `npm run typecheck`, `npm run lint`, `npm test`, `npm run build` and `npm audit`. Do not run `npm audit fix --force`. The route and chart modules load on demand; Vite empties the output directory before rebuilding to avoid retaining obsolete generated assets.

Current release test counts, environment, build identity and browser evidence belong in `docs/evidence/poc-v0.3/` and the release verification report. Prior benchmark, training and browser records remain historical evidence.
