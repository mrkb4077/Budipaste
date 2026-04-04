/**
 * Data migration script: Import Participants, Enrolments, and Contacts
 * from old Budibase exports into the new Budipaste Railway API.
 *
 * Run: node migrate_data.mjs
 */

import { readFileSync } from 'fs';
import { parse } from 'path';
import XLSX from 'xlsx';

const API_BASE = process.env.API_BASE || 'https://budipaste-production.up.railway.app/api/v1';
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || 'admin@budipaste.com';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';

const PARTICIPANTS_CSV = 'C:\\Users\\yiliy\\Downloads\\Participants_CSV_2026-04-04.csv';
const ENROLMENT_XLSX = 'C:\\Users\\yiliy\\OneDrive - Yiliyapinya Indigenous Corporation\\Enrolment_CSV_2026-04-04.xlsx';
const CONTACTS_XLSX = 'C:\\Users\\yiliy\\OneDrive - Yiliyapinya Indigenous Corporation\\Contacts_CSV_2026-04-04.xlsx';

const TERM = 2;
const YEAR = 2026;

// ── Helpers ──────────────────────────────────────────────────────────────────

function clean(val) {
  if (val === null || val === undefined) return null;
  const s = String(val).trim();
  return s === '' ? null : s;
}

function parseDate(val) {
  if (!val) return null;
  const s = String(val).trim();
  if (!s) return null;
  // Excel serial date number
  if (/^\d{5}$/.test(s)) {
    const d = XLSX.SSF.parse_date_code(parseInt(s));
    return `${d.y}-${String(d.m).padStart(2, '0')}-${String(d.d).padStart(2, '0')}T00:00:00`;
  }
  // ISO or common formats
  const d = new Date(s);
  if (!isNaN(d)) return d.toISOString().replace(/\.\d{3}Z$/, '');
  return null;
}

function readXlsx(path) {
  const wb = XLSX.readFile(path);
  const ws = wb.Sheets[wb.SheetNames[0]];
  return XLSX.utils.sheet_to_json(ws, { defval: null, raw: false });
}

function readCsv(path) {
  const wb = XLSX.readFile(path);
  const ws = wb.Sheets[wb.SheetNames[0]];
  return XLSX.utils.sheet_to_json(ws, { defval: null, raw: false });
}

async function post(path, payload, token) {
  const resp = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  const text = await resp.text();
  let body;
  try { body = JSON.parse(text); } catch { body = { raw: text }; }
  return { status: resp.status, body };
}

async function getAll(path, token) {
  const resp = await fetch(`${API_BASE}${path}?limit=500`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  return resp.json();
}

// ── Step 1: Login ─────────────────────────────────────────────────────────────

console.log(`Logging in to ${API_BASE}...`);
const loginResp = await fetch(`${API_BASE}/auth/access-token`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: `username=${encodeURIComponent(ADMIN_EMAIL)}&password=${encodeURIComponent(ADMIN_PASSWORD)}`,
});

if (!loginResp.ok) {
  const errorText = await loginResp.text();
  throw new Error(`Login failed (${loginResp.status}): ${errorText}`);
}

const { access_token: token } = await loginResp.json();
console.log('✓ Token obtained\n');

// ── Step 2: Import Participants ───────────────────────────────────────────────

console.log('Importing participants...');
const pRows = readCsv(PARTICIPANTS_CSV);
const pidMap = {}; // old identifier → new identifier
let ok = 0, skip = 0;

for (const row of pRows) {
  const firstName = clean(row['First Name']);
  const lastName = clean(row['Last Name']);
  const dob = parseDate(row['Date of Birth']);

  if (!firstName || !lastName || !dob) {
    console.log(`  SKIP (missing required): ${row['Full Name']}`);
    skip++; continue;
  }

  const payload = {
    first_name: firstName,
    last_name: lastName,
    full_name: clean(row['Full Name']) || `${firstName} ${lastName}`,
    date_of_birth: dob,
    gender: clean(row['Gender']),
    cultural_identity: clean(row['Cultural Identity']),
    living_situation: clean(row['Living Situation']),
    employment: clean(row['Employment']),
    address_1: clean(row['Address 1']),
    address_2: clean(row['Address 2']),
    address_3: clean(row['Address 3']),
    contact_ph_1: clean(row['Contact ph 1'] || row['Contact Ph 1']),
    contact_ph_2: clean(row['Contact Ph 2']),
    contact_ph_3: clean(row['Contact Ph 3']),
    is_enrolled: String(row['Is Enrolled']).toLowerCase() === 'true',
    date_last_attended: parseDate(row['Date Last Attended']),
    date_commenced: parseDate(row['Date Commenced']),
    dietary_needs: clean(row['Dietary Needs']),
    medical_needs: clean(row['Medical Needs']),
    neuro_diverse: clean(row['Neuro Diverse']),
    learning_disorder: clean(row['Learning Disorder']),
    physical_disorder: clean(row['Physical Disorder']),
    cannot_be_around: clean(row['Cannot be around']),
    contact_1_name: clean(row['Contact 1 Name']),
    contact_1_relationship: clean(row['Contact 1 Relationship']),
    contact_2_name: clean(row['Contact 2 Name']),
    contact_2_relationship: clean(row['Contact 2 Relationship']),
    contact_3_name: clean(row['Contact 3 Name']),
    contact_3_relationship: clean(row['Contact 3 Relationship']),
  };

  const { status, body } = await post('/participants/', payload, token);
  const oldId = clean(row['Identifyer'] || row['ID']);

  if (status === 200 || status === 201) {
    pidMap[oldId] = body.identifier;
    console.log(`  ✓ ${payload.full_name}`);
    ok++;
  } else if (status === 400 && JSON.stringify(body).toLowerCase().includes('already')) {
    console.log(`  ~ Already exists: ${payload.full_name}`);
    // fetch existing to get identifier
    const all = await getAll('/participants/', token);
    const existing = all.find(p => p.full_name === payload.full_name);
    if (existing && oldId) pidMap[oldId] = existing.identifier;
    skip++;
  } else {
    console.log(`  ✗ FAILED ${payload.full_name}: ${status} ${JSON.stringify(body).slice(0, 120)}`);
    skip++;
  }
}
console.log(`\nParticipants: ${ok} imported, ${skip} skipped\n`);

// ── Step 3: Import Enrolments ─────────────────────────────────────────────────

console.log('Importing enrolments (Term 2 2026)...');
const eRows = readXlsx(ENROLMENT_XLSX);
ok = 0; skip = 0;

for (const row of eRows) {
  const oldPid = clean(row['Participant ID']);
  if (!oldPid) { skip++; continue; }

  const newPid = pidMap[oldPid] || oldPid;
  const carers = row['Number of carers'];

  const payload = {
    participant_id: newPid,
    term: TERM,
    year: YEAR,
    days: clean(row['Days']),
    dual_enrollment: String(row['Dual Enrollment'] || 'false').toLowerCase() === 'true',
    dual_enrolment_details: clean(row['Dual Enrolment Details']),
    number_of_carers: carers !== null && !isNaN(parseInt(carers)) ? parseInt(carers) : null,
    research_project: clean(row['Research Project']),
    transition_plan: clean(row['Transition Plan']),
    transition_outcome_end_of_term: clean(row['Transition outcome end of term']),
  };

  const { status, body } = await post('/enrolment/', payload, token);
  if (status === 200 || status === 201) {
    console.log(`  ✓ Enrolment: ${oldPid}`);
    ok++;
  } else {
    console.log(`  ✗ FAILED ${oldPid}: ${status} ${JSON.stringify(body).slice(0, 120)}`);
    skip++;
  }
}
console.log(`\nEnrolments: ${ok} imported, ${skip} skipped\n`);

// ── Step 4: Import Contacts ───────────────────────────────────────────────────

console.log('Importing contacts...');
try {
  const cRows = readXlsx(CONTACTS_XLSX);
  ok = 0; skip = 0;

  for (const row of cRows) {
    const oldPid = clean(row['Participant ID']);
    if (!oldPid) { skip++; continue; }

    const newPid = pidMap[oldPid] || oldPid;

    const payload = {
      participant_id: newPid,
      contact_name: clean(row['Contact Name']),
      contact_relationship: clean(row['Contact Relationship']),
      contact_email: clean(row['Contact Email']),
      contact_phone: clean(row['Contact Phone']),
      address: clean(row['Address']),
      add_detail: clean(row['Add Detail']),
    };

    const { status, body } = await post('/contacts/', payload, token);
    if (status === 200 || status === 201) {
      console.log(`  ✓ Contact: ${payload.contact_name} → ${oldPid}`);
      ok++;
    } else {
      console.log(`  ✗ FAILED ${oldPid}: ${status} ${JSON.stringify(body).slice(0, 120)}`);
      skip++;
    }
  }
  console.log(`\nContacts: ${ok} imported, ${skip} skipped\n`);
} catch (e) {
  console.log(`  Contacts import error: ${e.message}\n`);
}

console.log('Migration complete!');
