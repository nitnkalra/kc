"""
One-time script to build all_participant_history.xlsx from
historical Teams attendance report files.

Run once, then delete this script.

Expected input
--------------
Put all old attendance .xlsx files (any filename) into:
    <kc>/historical_attendance/

Expected columns inside each file (Teams export format):
    Name | First Join | Last Leave | In-Meeting Duration |
    Email | Participant ID (UPN) | Role

Output
------
    <kc>/all_participant_history.xlsx
    Columns: Session_Date (date), Email (str)
    One row per unique attendee per session.
"""

import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

from config import SEASON_FOLDER


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

HISTORICAL_FOLDER = (
    SEASON_FOLDER.parent / "historical_attendance"
)
OUTPUT_FILE = (
    SEASON_FOLDER.parent / "all_participant_history.xlsx"
)
ALL_SESSIONS_FILE = (
    SEASON_FOLDER.parent / "all_session_details.xlsx"
)
BOT_EMAIL = "knowledge_club@inxiteout.ai"
REQUIRED_COLUMNS = {"Email", "First Join"}

# Minimum expected unique attendees per session file.
# Files below this threshold are flagged for review.
LOW_ATTENDANCE_THRESHOLD = 3


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class FileResult:
    file_name: str
    status: str = "ok"          # "ok" | "skipped" | "error"
    session_date: date | None = None
    total_rows: int = 0
    valid_rows: int = 0
    skipped_bot: int = 0
    skipped_no_email: int = 0
    skipped_no_date: int = 0
    missing_columns: list = field(default_factory=list)
    error_message: str | None = None


# ---------------------------------------------------------------------------
# Step 1 — Read file
# Raises on I/O failure so only the read call needs try/except
# (SCPAP005: pandas transformations must stay outside try/except)
# ---------------------------------------------------------------------------

def _read_file(file_path: Path) -> pd.DataFrame:
    """
    Read an Excel file from disk.
    Raises immediately on failure — caller wraps in try/except.
    """
    return pd.read_excel(file_path)


# ---------------------------------------------------------------------------
# Step 2 — Normalise columns (fixes SCPAP001)
# ---------------------------------------------------------------------------

def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip whitespace from column names using rename()
    instead of direct .columns assignment, avoiding
    an Analyze RPC on Spark Connect (SCPAP001).
    """
    return df.rename(columns=lambda c: str(c).strip())


# ---------------------------------------------------------------------------
# Step 3 — Validate required columns
# ---------------------------------------------------------------------------

def _validate_columns(
    df: pd.DataFrame,
    result: FileResult,
) -> bool:
    """
    Check required columns are present.
    Uses set(df) instead of set(df.columns) to avoid
    an Analyze RPC on every call (SCPAP001).
    Marks result as skipped if any are missing.
    Returns True only when all required columns exist.
    """
    missing = sorted(REQUIRED_COLUMNS - set(df))
    if missing:
        result.missing_columns = missing
        result.status = "skipped"
        result.error_message = (
            f"Missing required columns: {missing}"
        )
        return False
    return True


# ---------------------------------------------------------------------------
# Step 4 — Extract records with per-row skip tracking
# ---------------------------------------------------------------------------

def _extract_records(
    df: pd.DataFrame,
    result: FileResult,
) -> list[dict]:
    """
    Extract {Session_Date, Email} records from a validated
    DataFrame.  Counts and reports every skipped row.
    """
    result.total_rows = len(df)

    df = df.copy()
    df["Email"] = (
        df["Email"]
        .astype(str)
        .str.lower()
        .str.strip()
    )
    df["First Join"] = pd.to_datetime(
        df["First Join"].astype(str),
        errors="coerce",
    )

    # --- Count and remove bot rows ---
    bot_mask = df["Email"] == BOT_EMAIL
    result.skipped_bot = int(bot_mask.sum())
    df = df[~bot_mask]

    # --- Count and remove blank / NaN emails ---
    bad_email_mask = df["Email"].isin(
        {"", "nan", "none", "nat"}
    )
    result.skipped_no_email = int(bad_email_mask.sum())
    df = df[~bad_email_mask]

    # --- Count and remove unparseable dates ---
    no_date_mask = df["First Join"].isna()
    result.skipped_no_date = int(no_date_mask.sum())
    df = df[~no_date_mask]

    if df.empty:
        result.status = "skipped"
        result.error_message = (
            "No valid rows after filtering"
        )
        return []

    # Session date = earliest First Join in the file
    session_date = df["First Join"].min().date()
    result.session_date = session_date

    unique_emails = df["Email"].unique().tolist()
    result.valid_rows = len(unique_emails)

    return [
        {"Session_Date": session_date, "Email": email}
        for email in unique_emails
    ]


# ---------------------------------------------------------------------------
# Step 5 — Orchestrate per-file processing
# ---------------------------------------------------------------------------

def process_file(
    file_path: Path,
) -> tuple[FileResult, list[dict]]:
    """
    Process a single attendance file end-to-end.
    Returns (FileResult, list-of-records).
    Only file I/O is wrapped in try/except (SCPAP005).
    """
    result = FileResult(file_name=file_path.name)
    records: list[dict] = []

    # Only I/O in try/except — raises immediately on failure
    try:
        df = _read_file(file_path)
    except Exception as e:
        result.status = "error"
        result.error_message = str(e)
        return result, records

    # All pandas transformations outside try/except (SCPAP005)
    df = _normalise_columns(df)

    if not _validate_columns(df, result):
        return result, records

    records = _extract_records(df, result)
    return result, records


# ---------------------------------------------------------------------------
# Reporting — file-level summary
# ---------------------------------------------------------------------------

def print_file_report(results: list[FileResult]) -> None:
    """Print a per-file processing table to stdout."""

    ok = sum(1 for r in results if r.status == "ok")
    skipped = sum(
        1 for r in results if r.status == "skipped"
    )
    errors = sum(
        1 for r in results if r.status == "error"
    )

    print("\n" + "=" * 72)
    print("FILE PROCESSING REPORT")
    print("=" * 72)

    for r in results:
        icon = "\u2713" if r.status == "ok" else "\u2717"
        date_str = (
            str(r.session_date) if r.session_date
            else "unknown   "
        )
        print(
            f"  {icon}  {r.file_name:<50}  "
            f"date={date_str:<12}  "
            f"attendees={r.valid_rows:>3}"
        )
        if r.skipped_bot:
            print(
                f"       \u2514\u2500 bot rows skipped    : "
                f"{r.skipped_bot}"
            )
        if r.skipped_no_email:
            print(
                f"       \u2514\u2500 blank email rows    : "
                f"{r.skipped_no_email}"
            )
        if r.skipped_no_date:
            print(
                f"       \u2514\u2500 unparseable dates   : "
                f"{r.skipped_no_date}"
            )
        if r.error_message:
            print(
                f"       \u2514\u2500 reason              : "
                f"{r.error_message}"
            )

    print("-" * 72)
    print(
        f"  Total: {len(results)}  |  "
        f"OK: {ok}  |  "
        f"Skipped: {skipped}  |  "
        f"Errors: {errors}"
    )


# ---------------------------------------------------------------------------
# Cross-check helpers
# ---------------------------------------------------------------------------

def _load_session_dates() -> pd.DataFrame | None:
    """
    Load all_session_details.xlsx and return rows with a
    valid Date.  Only Date, Name, and Topic are used —
    Season and Session_ID are not required.
    Returns None if the file is missing or empty.
    """
    if not ALL_SESSIONS_FILE.exists():
        return None

    df = pd.read_excel(ALL_SESSIONS_FILE)
    df = _normalise_columns(df)
    df["Date"] = pd.to_datetime(
        df["Date"], errors="coerce"
    )
    df = df.dropna(subset=["Date"])

    return df if not df.empty else None


def _print_count_summary(
    session_dates: set,
    extracted_dates: set,
) -> tuple[list, list]:
    """
    Print count comparison and return
    (missing_dates, extra_dates) sorted lists.
    """
    matched = session_dates & extracted_dates
    missing = sorted(session_dates - extracted_dates)
    extra = sorted(extracted_dates - session_dates)

    print("\n  -- Check 1: Count Summary --")
    print(
        f"  Sessions in all_session_details  : "
        f"{len(session_dates):>3}"
    )
    print(
        f"  Attendance files found           : "
        f"{len(extracted_dates):>3}"
    )
    print(
        f"  Matched (date in both)           : "
        f"{len(matched):>3}"
    )
    print(
        f"  Missing attendance files         : "
        f"{len(missing):>3}"
        + ("  \u2190 action needed" if missing else "  \u2713")
    )
    print(
        f"  Extra files (not in spreadsheet) : "
        f"{len(extra):>3}"
        + ("  \u2190 review" if extra else "  \u2713")
    )

    return missing, extra


def _print_missing_dates(
    missing: list,
    all_sessions: pd.DataFrame,
) -> None:
    """Check 2 — Sessions in spreadsheet with no
    matching attendance file."""
    print("\n  -- Check 2: Missing Attendance Files --")
    if not missing:
        print(
            "  \u2713  All sessions have a matching "
            "attendance file."
        )
        return

    print(
        f"  \u2717  {len(missing)} session(s) have no "
        f"attendance file:"
    )
    print(
        f"  {'Date':<13}  "
        f"{'Name':<32}  Topic"
    )
    print(
        f"  {'-' * 13}  {'-' * 32}  {'-' * 30}"
    )
    for d in missing:
        rows = all_sessions[
            all_sessions["Date"].dt.date == d
        ]
        for _, row in rows.iterrows():
            name = str(row.get("Name", "?"))[:32]
            topic = str(row.get("Topic", "?"))[:48]
            print(
                f"  {str(d):<13}  "
                f"{name:<32}  {topic}"
            )


def _print_extra_dates(extra: list) -> None:
    """Check 3 — Attendance files whose date is not
    in all_session_details."""
    print("\n  -- Check 3: Extra Attendance Files --")
    if not extra:
        print(
            "  \u2713  All file dates exist in "
            "all_session_details."
        )
        return

    print(
        f"  \u2717  {len(extra)} file date(s) not in "
        f"spreadsheet \u2014 misnamed or test file?"
    )
    for d in extra:
        print(f"    - {d}")


def _check_duplicate_sheet_dates(
    all_sessions: pd.DataFrame,
) -> None:
    """Check 4 — Duplicate dates in
    all_session_details.xlsx (spreadsheet data quality)."""
    print("\n  -- Check 4: Duplicate Dates in Spreadsheet --")

    counts = (
        all_sessions["Date"]
        .dt.date
        .value_counts()
    )
    duplicates = counts[counts > 1]

    if duplicates.empty:
        print(
            "  \u2713  No duplicate dates in "
            "all_session_details."
        )
        return

    print(
        f"  \u2717  {len(duplicates)} date(s) appear "
        f"more than once:"
    )
    for d, count in duplicates.items():
        rows = all_sessions[
            all_sessions["Date"].dt.date == d
        ]
        print(f"    {d}  ({count}x)")
        for _, row in rows.iterrows():
            name = str(row.get("Name", "?"))
            topic = str(row.get("Topic", "?"))
            print(f"      - {name} | {topic}")


def _check_duplicate_file_dates(
    file_results: list[FileResult],
) -> None:
    """Check 5 — Multiple attendance files that resolve
    to the same session date (possible duplicate export
    or split-room file)."""
    print("\n  -- Check 5: Duplicate Dates Across Files --")

    date_to_files: dict = defaultdict(list)
    for r in file_results:
        if r.session_date is not None:
            date_to_files[r.session_date].append(
                r.file_name
            )

    duplicates = {
        d: files
        for d, files in date_to_files.items()
        if len(files) > 1
    }

    if not duplicates:
        print(
            "  \u2713  No duplicate session dates "
            "across attendance files."
        )
        return

    print(
        f"  \u2717  {len(duplicates)} date(s) have "
        f"multiple files \u2014 verify no double-counting:"
    )
    for d, files in sorted(duplicates.items()):
        print(f"    {d}:")
        for f in files:
            print(f"      - {f}")


def _check_low_attendance(
    file_results: list[FileResult],
) -> None:
    """Check 6 — Files with fewer unique attendees than
    LOW_ATTENDANCE_THRESHOLD (may be corrupted or
    incomplete)."""
    print(
        f"\n  -- Check 6: Low Attendance "
        f"(< {LOW_ATTENDANCE_THRESHOLD} attendees) --"
    )

    low = [
        r for r in file_results
        if r.status == "ok"
        and r.valid_rows < LOW_ATTENDANCE_THRESHOLD
    ]

    if not low:
        print(
            f"  \u2713  All files have \u2265 "
            f"{LOW_ATTENDANCE_THRESHOLD} valid attendees."
        )
        return

    print(
        f"  \u26a0  {len(low)} file(s) below threshold:"
    )
    for r in low:
        print(
            f"    - {r.file_name}  "
            f"| date={r.session_date}  "
            f"| attendees={r.valid_rows}"
        )


def _parse_filename_date(filename: str) -> date | None:
    """
    Extract a date from filenames like:
        'Tech Tuesday - Attendance report 6-18-24.xlsx'
        'Tech Tuesday - Attendance report 12-03-25.xlsx'

    Expects M-DD-YY or MM-DD-YY at the end of the stem.
    Returns None if the pattern is not found or the
    date is invalid.
    """
    stem = Path(filename).stem.strip()
    match = re.search(
        r"(\d{1,2})-(\d{1,2})-(\d{2,4})$", stem
    )
    if not match:
        return None

    month_s, day_s, year_s = match.groups()
    year = (
        int(f"20{year_s}")
        if len(year_s) == 2
        else int(year_s)
    )
    try:
        return date(year, int(month_s), int(day_s))
    except ValueError:
        return None


def _check_filename_date_mismatch(
    file_results: list[FileResult],
) -> None:
    """Check 7 — Compare the date embedded in the
    filename against the session date extracted from
    First Join timestamps.  A mismatch suggests the
    file was misnamed or placed in the wrong folder."""
    print(
        "\n  -- Check 7: Filename Date vs "
        "Extracted Session Date --"
    )

    mismatches = []
    unparseable = []

    for r in file_results:
        if r.session_date is None:
            continue
        fname_date = _parse_filename_date(r.file_name)
        if fname_date is None:
            unparseable.append(r.file_name)
            continue
        if fname_date != r.session_date:
            mismatches.append(
                (r.file_name, fname_date, r.session_date)
            )

    if not mismatches and not unparseable:
        print(
            "  \u2713  All filename dates match "
            "extracted session dates."
        )
        return

    if mismatches:
        print(
            f"  \u2717  {len(mismatches)} mismatch(es) "
            f"found:"
        )
        for fname, fn_date, ex_date in mismatches:
            print(f"    {fname}")
            print(
                f"      filename date  : {fn_date}"
            )
            print(
                f"      extracted date : {ex_date}"
            )

    if unparseable:
        print(
            f"\n  \u26a0  {len(unparseable)} filename(s) "
            f"with no parseable date (skipped):"
        )
        for f in unparseable:
            print(f"    - {f}")


# ---------------------------------------------------------------------------
# Cross-check orchestrator
# ---------------------------------------------------------------------------

def cross_check_sessions(
    extracted_dates: set,
    file_results: list[FileResult],
) -> None:
    """
    Run all cross-checks between attendance files and
    all_session_details.xlsx.

    Checks:
      1. Count summary
      2. Sessions missing attendance files
      3. Extra attendance files not in spreadsheet
      4. Duplicate dates in spreadsheet
      5. Duplicate dates across attendance files
      6. Low attendance files
      7. Filename date vs extracted date mismatch
    """
    print("\n" + "=" * 72)
    print(
        "CROSS-CHECK  \u2014  "
        "historical_attendance vs all_session_details  "
        "(key: Date)"
    )
    print("=" * 72)

    all_sessions = _load_session_dates()

    if all_sessions is None:
        msg = (
            f"  [Skipped] {ALL_SESSIONS_FILE.name} "
            "not found."
            if not ALL_SESSIONS_FILE.exists()
            else "  No valid dates found in "
            "all_session_details.xlsx."
        )
        print(msg)
        # Still run file-only checks
        _check_duplicate_file_dates(file_results)
        _check_low_attendance(file_results)
        _check_filename_date_mismatch(file_results)
        return

    session_dates = set(all_sessions["Date"].dt.date)

    missing, extra = _print_count_summary(
        session_dates, extracted_dates
    )
    _print_missing_dates(missing, all_sessions)
    _print_extra_dates(extra)
    _check_duplicate_sheet_dates(all_sessions)
    _check_duplicate_file_dates(file_results)
    _check_low_attendance(file_results)
    _check_filename_date_mismatch(file_results)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:

    if not HISTORICAL_FOLDER.exists():
        print(
            f"Folder not found: {HISTORICAL_FOLDER}\n"
            "Create it and place all historical "
            "attendance .xlsx files inside."
        )
        sys.exit(1)

    files = sorted(HISTORICAL_FOLDER.glob("*.xlsx"))

    if not files:
        print(
            f"No .xlsx files found in {HISTORICAL_FOLDER}"
        )
        sys.exit(1)

    print(
        f"Found {len(files)} file(s) in "
        f"{HISTORICAL_FOLDER}\n"
    )

    all_records: list[dict] = []
    file_results: list[FileResult] = []

    for file in files:
        result, records = process_file(file)
        file_results.append(result)
        all_records.extend(records)

    # Per-file report
    print_file_report(file_results)

    if not all_records:
        print(
            "\nNo records extracted. "
            "Output file not created."
        )
        sys.exit(1)

    # All cross-checks
    extracted_dates = {
        r["Session_Date"] for r in all_records
    }
    cross_check_sessions(extracted_dates, file_results)

    # Save output
    df_out = (
        pd.DataFrame(all_records)
        .drop_duplicates()
        .sort_values("Session_Date")
        .reset_index(drop=True)
    )
    df_out.to_excel(OUTPUT_FILE, index=False)

    print(
        f"\n{'=' * 72}\n"
        f"DONE \u2014 {len(df_out)} rows saved "
        f"\u2192 {OUTPUT_FILE}\n"
        f"{'=' * 72}"
    )


if __name__ == "__main__":
    main()
