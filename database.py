# database.py
# Minimal SQLite wrapper for Hospital Management System
import sqlite3
from typing import List, Optional, Tuple, Dict

DB_PATH = "hospital.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    conn = get_connection()
    cur = conn.cursor()

    # Patients table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        contact TEXT,
        notes TEXT
    );
    """)

    # Doctors table
    # working_hours stored as simple "HH:MM-HH:MM" string e.g. "09:00-17:00"
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialty TEXT,
        working_hours TEXT,
        contact TEXT,
        notes TEXT
    );
    """)

    # Appointments table
    # date in YYYY-MM-DD, time in HH:MM
    # Prevent double-booking by UNIQUE constraint on (doctor_id, date, time)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        patient_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id),
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        UNIQUE (doctor_id, date, time)
    );
    """)

    conn.commit()
    conn.close()


# ---------------------------
# Patient CRUD
# ---------------------------
def add_patient(name: str, age: Optional[int], gender: Optional[str], contact: Optional[str], notes: Optional[str]) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patients (name, age, gender, contact, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (name, age, gender, contact, notes))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def get_patients() -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_patient(patient_id: int) -> Optional[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    row = cur.fetchone()
    conn.close()
    return row


def update_patient(patient_id: int, name: str, age: Optional[int], gender: Optional[str], contact: Optional[str], notes: Optional[str]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE patients SET name=?, age=?, gender=?, contact=?, notes=? WHERE id=?
    """, (name, age, gender, contact, notes, patient_id))
    conn.commit()
    conn.close()


def delete_patient(patient_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()


# ---------------------------
# Doctor CRUD
# ---------------------------
def add_doctor(name: str, specialty: Optional[str], working_hours: Optional[str], contact: Optional[str], notes: Optional[str]) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO doctors (name, specialty, working_hours, contact, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (name, specialty, working_hours, contact, notes))
    conn.commit()
    did = cur.lastrowid
    conn.close()
    return did


def get_doctors() -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM doctors ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_doctor(doctor_id: int) -> Optional[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
    row = cur.fetchone()
    conn.close()
    return row


def update_doctor(doctor_id: int, name: str, specialty: Optional[str], working_hours: Optional[str], contact: Optional[str], notes: Optional[str]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE doctors SET name=?, specialty=?, working_hours=?, contact=?, notes=? WHERE id=?
    """, (name, specialty, working_hours, contact, notes, doctor_id))
    conn.commit()
    conn.close()


def delete_doctor(doctor_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    # Optionally cascade delete appointments for that doctor:
    cur.execute("DELETE FROM appointments WHERE doctor_id = ?", (doctor_id,))
    cur.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
    conn.commit()
    conn.close()


# ---------------------------
# Appointment CRUD
# ---------------------------
def add_appointment(doctor_id: int, patient_id: int, date: str, time: str, reason: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Returns (success, error_message). Uses UNIQUE constraint to avoid double-booking.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO appointments (doctor_id, patient_id, date, time, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (doctor_id, patient_id, date, time, reason))
        conn.commit()
        conn.close()
        return True, None
    except sqlite3.IntegrityError as e:
        conn.close()
        return False, str(e)


def get_appointments(limit: int = 100) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.*, d.name as doctor_name, p.name as patient_name
        FROM appointments a
        LEFT JOIN doctors d ON a.doctor_id = d.id
        LEFT JOIN patients p ON a.patient_id = p.id
        ORDER BY a.date DESC, a.time DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_appointments_by_doctor_date_time(doctor_id: int, date: str, time: str) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM appointments WHERE doctor_id=? AND date=? AND time=?
    """, (doctor_id, date, time))
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_appointment(appointment_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()


# ---------------------------
# Dashboard helpers
# ---------------------------
def count_patients() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM patients")
    (c,) = cur.fetchone()
    conn.close()
    return c


def count_doctors() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM doctors")
    (c,) = cur.fetchone()
    conn.close()
    return c


def count_appointments() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM appointments")
    (c,) = cur.fetchone()
    conn.close()
    return c


def recent_appointments(limit: int = 5) -> List[sqlite3.Row]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.*, d.name as doctor_name, p.name as patient_name
        FROM appointments a
        LEFT JOIN doctors d ON a.doctor_id = d.id
        LEFT JOIN patients p ON a.patient_id = p.id
        ORDER BY a.created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


# initialize DB on import
initialize_db()
