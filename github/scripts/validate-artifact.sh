#!/usr/bin/env zsh
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: validate-artifact.sh <artifact-path> [source-artifact-path]"
  exit 1
fi

artifact=$1
source_artifact=${2:-}

if [[ ! -f "$artifact" ]]; then
  echo "FAIL: artifact.path — file not found: $artifact"
  exit 1
fi

typeset -a failures

add_fail() {
  failures+=("$1")
}

if ! rg -q '^schema_version:[[:space:]]*2$' "$artifact"; then
  add_fail "artifact.schema_version — expected schema_version: 2"
fi

decision_ids=(${(@f)$( { rg -o '^  - id: "D[0-9]+"' "$artifact" || true; } | sed -E 's/^  - id: "(D[0-9]+)"$/\1/')})
requirement_ids=(${(@f)$( { rg -o '^  - id: "R[0-9]+"' "$artifact" || true; } | sed -E 's/^  - id: "(R[0-9]+)"$/\1/')})
step_ids=(${(@f)$( { rg -o 'id: "P[0-9]+\.S[0-9]+"' "$artifact" || true; } | sed -E 's/^id: "(P[0-9]+\.S[0-9]+)"$/\1/' | sort -u)})

for id in $decision_ids; do
  if [[ $(printf '%s\n' "${decision_ids[@]}" | rg -xc "$id") -gt 1 ]]; then
    add_fail "decisions.id — duplicate id $id"
  fi
done

for id in $requirement_ids; do
  if [[ $(printf '%s\n' "${requirement_ids[@]}" | rg -xc "$id") -gt 1 ]]; then
    add_fail "requirements.id — duplicate id $id"
  fi
done

while IFS= read -r ref; do
  [[ -z "$ref" ]] && continue
  if ! printf '%s\n' "${decision_ids[@]}" | rg -qx "$ref"; then
    add_fail "requirements.source_decision — $ref not found in decisions[*].id"
  fi
done < <({ rg -o 'source_decision:[[:space:]]*"D[0-9]+"' "$artifact" || true; } | sed -E 's/^source_decision:[[:space:]]*"(D[0-9]+)"$/\1/')

while IFS= read -r ref; do
  [[ -z "$ref" ]] && continue
  if ! printf '%s\n' "${step_ids[@]}" | rg -qx "$ref"; then
    add_fail "steps.depends_on — $ref not found in steps[*].id"
  fi
done < <({ rg -o '"P[0-9]+\.S[0-9]+"' "$artifact" || true; } | tr -d '"' | { rg '^P[0-9]+\.S[0-9]+$' || true; })

# Required-field checks on typed primitives (line-number bounded blocks)
eof_plus1=$(awk 'END {print NR+1}' "$artifact")

for id in $decision_ids; do
  start=$(rg -n "^  - id: \"$id\"$" "$artifact" | head -1 | cut -d: -f1)
  [[ -z "$start" ]] && continue
  next=$(awk -v s="$start" 'NR > s && /^  - id: "D[0-9]+"/ {print NR; exit}' "$artifact")
  [[ -z "$next" ]] && next=$eof_plus1
  if ! awk -v s="$start" -v e="$next" 'NR > s && NR < e' "$artifact" | rg -q '^\s+chosen:\s*\S'; then
    add_fail "decisions[$id].chosen — required field missing or empty"
  fi
done

for id in $requirement_ids; do
  start=$(rg -n "^  - id: \"$id\"$" "$artifact" | head -1 | cut -d: -f1)
  [[ -z "$start" ]] && continue
  next=$(awk -v s="$start" 'NR > s && /^  - id: "R[0-9]+"/ {print NR; exit}' "$artifact")
  [[ -z "$next" ]] && next=$eof_plus1
  if ! awk -v s="$start" -v e="$next" 'NR > s && NR < e' "$artifact" | rg -q '^\s+text:\s*\S'; then
    add_fail "requirements[$id].text — required field missing or empty"
  fi
  if ! awk -v s="$start" -v e="$next" 'NR > s && NR < e' "$artifact" | rg -q '^\s+acceptance:\s*\S'; then
    add_fail "requirements[$id].acceptance — required field missing or empty"
  fi
done

for id in $step_ids; do
  escaped_id=$(printf '%s' "$id" | sed 's/\./\\./g')
  start=$(rg -n "^      - id: \"$escaped_id\"$" "$artifact" | head -1 | cut -d: -f1)
  [[ -z "$start" ]] && continue
  next=$(awk -v s="$start" 'NR > s && /^      - id: "P[0-9]+\.S[0-9]+"/ {print NR; exit}' "$artifact")
  [[ -z "$next" ]] && next=$eof_plus1
  if ! awk -v s="$start" -v e="$next" 'NR > s && NR < e' "$artifact" | rg -q '^\s+files:'; then
    add_fail "steps[$id].files — required field missing or empty"
  fi
  if ! awk -v s="$start" -v e="$next" 'NR > s && NR < e' "$artifact" | rg -q '^\s+verify:\s*\S'; then
    add_fail "steps[$id].verify — required field missing or empty"
  fi
done

if [[ -n "$source_artifact" && -f "$source_artifact" ]]; then
  for field in problem open_decisions decisions requirements spec_constraints out_of_scope; do
    if rg -q "^$field:" "$source_artifact" && rg -q "^$field:" "$artifact"; then
      src_block=$(sed -n "/^$field:/,/^[^[:space:]]/p" "$source_artifact" | sed '$d')
      dst_block=$(sed -n "/^$field:/,/^[^[:space:]]/p" "$artifact" | sed '$d')
      if [[ "$src_block" != "$dst_block" ]]; then
        add_fail "$field — inherited field modified"
      fi
    fi
  done
fi

if (( ${#failures[@]} > 0 )); then
  for failure in "${failures[@]}"; do
    echo "FAIL: $failure"
  done
  exit 1
fi
