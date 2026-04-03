#!/usr/bin/env python3
"""
Data migration script: Import Participants, Enrolments, and Contacts
from old Budibase CSV/XLSX exports into the new Budipaste Railway API.

Usage:
    python migrate_data.py

Before running:
    pip install requests openpyxl
"""

import csv
import json
import sys
import requests
import openpyxl
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────────────────────
API_BASE = "https://budipaste-production.up.railway.app/api/v1"
ADMIN_EMAIL = "admin@budipaste.com"
ADMIN_PASSWORD = "admin123"

PARTICIPANTS_CSV = r"C:\Users\yiliy\Downloads\Participants_CSV_2026-04-04.csv"
ENROLMENT_XLSX  = r"C:\Users\yiliy\OneDrive - Yiliyapinya Indigenous Corporation\Enrolment_CSV_2026-04-04.xlsx"
CONTACTS_XLSX   = r"C:\Users\yiliy\OneDrive - Yiliyapinya Indigenous Corporation\Contacts_CSV_2026-04-04.xlsx"

# Term 2 2026
TERM = 2
YEAR = 2026


# ── Helpers ────────────────────────────────────────────────────────────────────

def get_token():
    resp = requests.post(
        f"{API_BASE}/auth/access-token",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def parse_date(val):
    """Return ISO 8601 string or None."""
    if not val or str(val).strip() in ("", "None"):
        return None
    val = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(val, fmt).isoformat()
        except ValueError:
            continue
    return None


def clean(val):
    """Return stripped string or None."""
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def xlsx_to_rows(path):
    """Read an xlsx file and return list of dicts (header → value)."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers_row = [str(h).strip() if h is not None else "" for h in rows[0]]
    result = []
    for row in rows[1:]:
        if all(v is None for v in row):
            continue
        result.append(dict(zip(headers_row, row)))
    wb.close()
    return result


# ── Step 1: Login ──────────────────────────────────────────────────────────────

print("Logging in...")
token = get_token()
print("✓ Token obtained\n")


# ── Step 2: Import Participants ────────────────────────────────────────────────

print("Importing participants...")
participant_id_map = {}  # old identifier → new API identifier

with open(PARTICIPANTS_CSV, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

ok = 0
skip = 0
for row in rows:
    first_name = clean(row.get("First Name"))
    last_name  = clean(row.get("Last Name"))
    dob        = parse_date(row.get("Date of Birth"))

    if not first_name or not last_name or not dob:
        print(f"  SKIP (missing required fields): {row.get('Full Name')}")
        skip += 1
        continue

    payload = {
        "first_name":         first_name,
        "last_name":          last_name,
        "full_name":          clean(row.get("Full Name")) or f"{first_name} {last_name}",
        "date_of_birth":      dob,
        "gender":             clean(row.get("Gender")),
        "cultural_identity":  clean(row.get("Cultural Identity")),
        "living_situation":   clean(row.get("Living Situation")),
        "employment":         clean(row.get("Employment")),
        "address_1":          clean(row.get("Address 1")),
        "address_2":          clean(row.get("Address 2")),
        "address_3":          clean(row.get("Address 3")),
        "contact_ph_1":       clean(row.get("Contact ph 1") or row.get("Contact Ph 1")),
        "contact_ph_2":       clean(row.get("Contact Ph 2")),
        "contact_ph_3":       clean(row.get("Contact Ph 3")),
        "is_enrolled":        str(row.get("Is Enrolled", "true")).lower() == "true",
        "date_last_attended": parse_date(row.get("Date Last Attended")),
        "date_commenced":     parse_date(row.get("Date Commenced")),
        "dietary_needs":      clean(row.get("Dietary Needs")),
        "medical_needs":      clean(row.get("Medical Needs")),
        "neuro_diverse":      clean(row.get("Neuro Diverse")),
        "learning_disorder":  clean(row.get("Learning Disorder")),
        "physical_disorder":  clean(row.get("Physical Disorder")),
        "cannot_be_around":   clean(row.get("Cannot be around")),
        "contact_1_name":         clean(row.get("Contact 1 Name")),
        "contact_1_relationship": clean(row.get("Contact 1 Relationship")),
        "contact_2_name":         clean(row.get("Contact 2 Name")),
        "contact_2_relationship": clean(row.get("Contact 2 Relationship")),
        "contact_3_name":         clean(row.get("Contact 3 Name")),
        "contact_3_relationship": clean(row.get("Contact 3 Relationship")),
    }

    resp = requests.post(f"{API_BASE}/participants/", json=payload, headers=headers(token))
    if resp.status_code in (200, 201):
        data = resp.json()
        old_id = clean(row.get("Identifyer") or row.get("ID"))
        new_id = data.get("identifier")
        if old_id:
            participant_id_map[old_id] = new_id
        print(f"  ✓ {payload['full_name']}")
        ok += 1
    elif resp.status_code == 400 and "already" in resp.text.lower():
        print(f"  ~ Already exists: {payload['full_name']}")
        # Still need the identifier for linking — fetch it
        search = requests.get(
            f"{API_BASE}/participants/",
            headers=headers(token),
            params={"limit": 200}
        )
        for p in search.json():
            if p.get("full_name") == payload["full_name"]:
                old_id = clean(row.get("Identifyer") or row.get("ID"))
                if old_id:
                    participant_id_map[old_id] = p["identifier"]
                break
        skip += 1
    else:
        print(f"  ✗ FAILED {payload['full_name']}: {resp.status_code} {resp.text[:120]}")
        skip += 1

print(f"\nParticipants: {ok} imported, {skip} skipped\n")


# ── Step 3: Import Enrolments ──────────────────────────────────────────────────

print("Importing enrolments (Term 2 2026)...")
enrol_rows = xlsx_to_rows(ENROLMENT_XLSX)

ok = 0
skip = 0
for row in enrol_rows:
    old_pid = clean(row.get("Participant ID"))
    if not old_pid:
        skip += 1
        continue

    # Map old identifier to new one (they should match since name|dob is stable)
    new_pid = participant_id_map.get(old_pid, old_pid)

    days_val = clean(row.get("Days"))

    payload = {
        "participant_id":               new_pid,
        "term":                         TERM,
        "year":                         YEAR,
        "days":                         days_val,
        "dual_enrollment":              str(row.get("Dual Enrollment", "false")).lower() == "true",
        "dual_enrolment_details":       clean(row.get("Dual Enrolment Details")),
        "number_of_carers":             int(row["Number of carers"]) if row.get("Number of carers") and str(row["Number of carers"]).isdigit() else None,
        "research_project":             clean(row.get("Research Project")),
        "transition_plan":              clean(row.get("Transition Plan")),
        "transition_outcome_end_of_term": clean(row.get("Transition outcome end of term")),
    }

    resp = requests.post(f"{API_BASE}/enrolment/", json=payload, headers=headers(token))
    if resp.status_code in (200, 201):
        print(f"  ✓ Enrolment: {old_pid}")
        ok += 1
    else:
        print(f"  ✗ FAILED {old_pid}: {resp.status_code} {resp.text[:120]}")
        skip += 1

print(f"\nEnrolments: {ok} imported, {skip} skipped\n")


# ── Step 4: Import Contacts ────────────────────────────────────────────────────

print("Importing contacts...")
try:
    contact_rows = xlsx_to_rows(CONTACTS_XLSX)
    ok = 0
    skip = 0
    for row in contact_rows:
        old_pid = clean(row.get("Participant ID"))
        if not old_pid:
            skip += 1
            continue

        new_pid = participant_id_map.get(old_pid, old_pid)

        payload = {
            "participant_id":      new_pid,
            "contact_name":        clean(row.get("Contact Name")),
            "contact_relationship":clean(row.get("Contact Relationship")),
            "contact_email":       clean(row.get("Contact Email")),
            "contact_phone":       clean(row.get("Contact Phone")),
            "address":             clean(row.get("Address")),
            "add_detail":          clean(row.get("Add Detail")),
        }

        resp = requests.post(f"{API_BASE}/contacts/", json=payload, headers=headers(token))
        if resp.status_code in (200, 201):
            print(f"  ✓ Contact: {payload['contact_name']} → {old_pid}")
            ok += 1
        else:
            print(f"  ✗ FAILED {old_pid}: {resp.status_code} {resp.text[:120]}")
            skip += 1

    print(f"\nContacts: {ok} imported, {skip} skipped\n")
except Exception as e:
    print(f"  Contacts import error: {e}\n")


print("Migration complete!")
