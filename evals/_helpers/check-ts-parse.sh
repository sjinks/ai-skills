#!/usr/bin/env bash
# Reads waza grader output JSON on stdin and checks that any TypeScript code
# fences embedded in the agent output parse with `tsc --noEmit --allowJs
# --skipLibCheck`. Exits 0 if all fences parse, 1 otherwise.
#
# Usage: piped from waza program grader.

set -euo pipefail

INPUT=$(cat)
WORKDIR=$(mktemp -d)
trap 'rm -rf "$WORKDIR"' EXIT

# Extract `output` field (waza passes a JSON envelope with fields output,
# outcome, transcript, tool_calls, errors, duration_ms).
OUTPUT=$(echo "$INPUT" | jq -r '.output // empty')

if [ -z "$OUTPUT" ]; then
    echo "no output field" >&2
    exit 1
fi

# Pull every ```ts and ```typescript fenced block, write to numbered .ts files.
echo "$OUTPUT" | awk '
  /^```(ts|typescript)\s*$/ { fence=1; n++; out=sprintf("'"$WORKDIR"'/snippet_%02d.ts", n); next }
  /^```\s*$/ { fence=0; next }
  fence { print > out }
'

shopt -s nullglob
files=("$WORKDIR"/snippet_*.ts)

if [ "${#files[@]}" -eq 0 ]; then
    echo "no typescript fences found in output" >&2
    exit 1
fi

if ! command -v tsc > /dev/null 2>&1; then
    echo "tsc not on PATH; install TypeScript (e.g. 'npm i -g typescript') to run this grader" >&2
    exit 1
fi

cat > "$WORKDIR/tsconfig.json" << JSON
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "strict": false,
    "noEmit": true,
    "allowJs": true,
    "skipLibCheck": true,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  },
  "include": ["snippet_*.ts"]
}
JSON

if ! tsc --noEmit -p "$WORKDIR" 2> "$WORKDIR/tsc.err"; then
    cat "$WORKDIR/tsc.err" >&2
    exit 1
fi

exit 0
