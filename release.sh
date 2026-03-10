#!/usr/bin/env bash
set -euo pipefail

# ── Failure trap ─────────────────────────────────────────────────────────────
_on_error() {
    local exit_code=$?
    local line_no=${1:-}
    echo "" >&2
    echo -e "\033[0;31m╔══════════════════════════════════════════════════════════════╗\033[0m" >&2
    echo -e "\033[0;31m║                    RELEASE SCRIPT FAILED                    ║\033[0m" >&2
    echo -e "\033[0;31m╠══════════════════════════════════════════════════════════════╣\033[0m" >&2
    echo -e "\033[0;31m║  Exit code : ${exit_code}$(printf '%*s' $((61 - ${#exit_code})) '')║\033[0m" >&2
    [[ -n "$line_no" ]] && \
    echo -e "\033[0;31m║  Line      : ${line_no}$(printf '%*s' $((61 - ${#line_no})) '')║\033[0m" >&2
    echo -e "\033[0;31m║  No version was committed, tagged, or pushed.               ║\033[0m" >&2
    echo -e "\033[0;31m╚══════════════════════════════════════════════════════════════╝\033[0m" >&2
    echo "" >&2
}
trap '_on_error $LINENO' ERR

# ── Portable in-place sed ────────────────────────────────────────────────────
sedi() {
    if sed --version 2>/dev/null | grep -q GNU; then
        sed -i "$@"
    else
        sed -i '' "$@"
    fi
}

PYPROJECT="pyproject.toml"
REMOTE="origin"
BRANCH="main"

# ── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail()  { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }

# ── Pre-flight checks ──────────────────────────────────────────────────────

# Must be in the repo root (where pyproject.toml lives)
[[ -f "$PYPROJECT" ]] || fail "$PYPROJECT not found. Run this from the repo root."

# Must be on the main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
[[ "$CURRENT_BRANCH" == "$BRANCH" ]] || fail "Not on $BRANCH branch (on $CURRENT_BRANCH). Switch first."

# Must have a clean working tree (user should have already committed)
if [[ -n "$(git diff --cached --name-only)" ]]; then
    fail "You have staged but uncommitted changes. Commit first, then run this script."
fi

if [[ -n "$(git diff --name-only)" ]]; then
    warn "You have unstaged changes in tracked files. They will NOT be included."
    echo -e "       Untracked files are always ignored.\n"
fi

# Must have at least one commit ahead of remote (the user's commit)
LOCAL_HEAD=$(git rev-parse HEAD)
REMOTE_HEAD=$(git rev-parse "$REMOTE/$BRANCH" 2>/dev/null || echo "none")
if [[ "$LOCAL_HEAD" == "$REMOTE_HEAD" ]]; then
    fail "No new commits to release. Commit your changes first, then run this script."
fi

# ── Read & bump version ────────────────────────────────────────────────────

CURRENT_VERSION=$(grep '^version = ' "$PYPROJECT" | sed 's/version = "\(.*\)"/\1/')
[[ -n "$CURRENT_VERSION" ]] || fail "Could not read version from $PYPROJECT"

IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
NEW_PATCH=$((PATCH + 1))
NEW_VERSION="${MAJOR}.${MINOR}.${NEW_PATCH}"
NEW_TAG="v${NEW_VERSION}"

info "Current version: $CURRENT_VERSION"
info "New version:     $NEW_VERSION"
info "Tag:             $NEW_TAG"

# Check tag doesn't already exist
if git rev-parse "$NEW_TAG" &>/dev/null; then
    fail "Tag $NEW_TAG already exists. Manually resolve the version."
fi

echo ""

# ── Update pyproject.toml and amend the commit ─────────────────────────────

info "Updating $PYPROJECT to version $NEW_VERSION..."
sedi "s/^version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" "$PYPROJECT"
ok "Version updated in $PYPROJECT"

info "Amending last commit to include version bump..."
git add "$PYPROJECT"
git commit --amend --no-edit --quiet
ok "Commit amended"

# ── Push commit ─────────────────────────────────────────────────────────────

info "Pushing to $REMOTE/$BRANCH..."
echo ""
git push "$REMOTE" "$BRANCH"
echo ""
ok "Pushed to $REMOTE/$BRANCH"

# ── Tag and push tag ───────────────────────────────────────────────────────

info "Creating tag $NEW_TAG..."
git tag "$NEW_TAG"
ok "Tag created"

info "Pushing tag $NEW_TAG..."
echo ""
git push "$REMOTE" "$NEW_TAG"
echo ""
ok "Tag pushed"

# ── Done ────────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Released matrx-orm $NEW_VERSION${NC}"
echo -e "${GREEN}  GitHub Actions will now build and publish to PyPI.${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Monitor: ${CYAN}https://github.com/armanisadeghi/matrx-orm/actions${NC}"
echo ""
echo -e "  Update:  ${CYAN}uv add matrix-orm==${NEW_VERSION}${NC}"
echo -e "  --> Not Available Yet?   Speed up indexing:  ${CYAN}pip index versions matrx-orm${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
