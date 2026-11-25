"""
Website publishing settings - used by publish/publish_site.py.
"""

# ---------------------------------------------------------------------------
# Auto git push
#   After each run, commit + push only frontend/src/data/*.json.
#   Push happens only from PUSH_BRANCH; the live site deploys after the
#   develop -> qa -> main pull requests are merged.
# ---------------------------------------------------------------------------
AUTO_GIT_PUSH = True
PUSH_BRANCH   = "develop"

# ---------------------------------------------------------------------------
# all_session_details.xlsx conventions for the site
#   Topic    : regular -> one topic; decode-it -> comma-separated speaker topics.
#   Category : extra column (ignored by the scoring pipeline). One category for
#              regular sessions; decode-it -> comma-separated, same order as Topic.
#              Free text allowed - mapped to site categories via categories.py.
# ---------------------------------------------------------------------------
CATEGORY_COLUMN          = "Category"
DECODE_PLACEHOLDER_TOPIC = "decode it session"   # legacy value = topics not filled

# Previous-season winners shown on the site
WINNERS_COUNT = 3
