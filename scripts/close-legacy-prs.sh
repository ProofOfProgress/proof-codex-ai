#!/usr/bin/env bash
# Close open PRs that target the retired Peripheral/horror/YouTube stack.
# Requires gh auth with pull-request write (repo admin or maintainer).
# Run: bash scripts/close-legacy-prs.sh
# Dry-run: bash scripts/close-legacy-prs.sh --dry-run

set -euo pipefail

REPO="${GITHUB_REPOSITORY:-ProofOfProgress/proof-codex-ai}"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

CLOSE_MSG='Closing: repo pivoted to TikTok Shop affiliate (bubble-wrap phase). Targets retired Peripheral/horror/YouTube/InVideo stack — conflicts with main.'

# All reviewed 2026-06-26 — none align with current mission (see docs/PRIORITIES.md).
PRS=(
  1   # pytest housekeeping (superseded on main)
  2   # line endings (superseded)
  4   # README fix (superseded)
  16  # ChainsFR / niche research
  17  # YouTube production + Discord ROBOTUS
  18  # Soft Continuity cosy aesthetic
  19  # AlphaBeta001 manager agents
  20  # AI video prompting Soft Continuity
  31  # horror A/V jumpscare sync
  32  # horror SFX / CapCut
  34  # YouTube YPP compliance (out of scope)
  36  # Codex ask (archived)
  38  # Slack ops (already on main — superseded)
  51  # daily upload blockers
  56  # Blender creature models
  57  # Blender curriculum
  58  # daily video automation
  59  # Blender course draft #2
  60  # micro jumpscare
  61  # Blender self-train
  62  # daily video guardrails
  63  # Recraft horror stills
  64  # daily cron horror prompts
  65  # Facebook/Meta Reels Peripheral
  66  # daily upload guardrails
  67  # daily pipeline guardrails
  71  # daily video + Blender upload
  72  # daily video guardrails
  83  # InVideo upload reliability
  91  # InVideo recovery
  115 # B2B outreach (unrelated)
  116 # daily upload readiness
)

echo "Repo: $REPO"
echo "PRs to close: ${#PRS[@]}"
echo

for n in "${PRS[@]}"; do
  if $DRY_RUN; then
    gh pr view "$n" --repo "$REPO" --json number,title,state,headRefName \
      --jq '"#\(.number) [\(.state)] \(.title) (\(.headRefName))"' 2>/dev/null \
      || echo "#$n (not found)"
    continue
  fi
  if gh pr close "$n" --repo "$REPO" -c "$CLOSE_MSG" 2>/dev/null; then
    echo "closed #$n"
  else
    echo "FAILED #$n (need pull-request write — try: gh auth login)" >&2
  fi
done

echo
echo "Done. Verify: gh pr list --repo $REPO --state open"
