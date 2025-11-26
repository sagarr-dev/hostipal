# app.py
# Streamlit UI for Hospital Management System (single-file UI)
import streamlit as st
from datetime import date, datetime
import database
import utils

# Page config
st.set_page_config(page_title="Hospital Management", layout="wide")

st.title("🏥 Simple Hospital Management System")

# Sidebar navigation
menu = st.sidebar.selectbox("Navigation", ["Dashboard", "Patients", "Doctors", "Appointments"])

# ---------------------
# DASHBOARD
# ---------------------
if menu == "Dashboard":
    st.header("Dashboard")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Patients", database.count_patients())
    with c2:
        st.metric("Total Doctors", database.count_doctors())
    with c3:
        st.metric("Total Appointments", database.count_appointments())

    st.subheader("Recent Activity (latest appointments)")
    recent = database.recent_appointments(limit=10)
    if recent:
        for r in recent:
            st.write(f"Appointment #{r['id']}: {r['date']} {r['time']} — Dr. {r['doctor_name']} with {r['patient_name']} (Booked: {r['created_at']})")
    else:
        st.write("No recent activity.")

# ---------------------
# PATIENTS
# ---------------------
elif menu == "Patients":
    st.header("Patient Management")
    st.subheader("Add New Patient")
    with st.form("add_patient", clear_on_submit=True):
        name = st.text_input("Name", max_chars=100)
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
        contact = st.text_input("Contact")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Patient")
        if submitted:
            if not name.strip():
                st.error("Name is required.")
            else:
                pid = database.add_patient(name.strip(), int(age), gender or None, contact or None, notes or None)
                st.success(f"Patient added with id #{pid}")

    st.subheader("Patient List")
    patients = database.get_patients()
    if patients:
        for p in patients:
            with st.expander(f"{p['id']}: {p['name']}"):
                st.write(f"Age: {p['age']}, Gender: {p['gender']}")
                st.write(f"Contact: {p['contact']}")
                st.write(f"Notes: {p['notes']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Edit", key=f"edit_patient_{p['id']}"):
                        # show inline edit form
                        st.session_state.setdefault("editing_patient", p['id'])
                with col2:
                    if st.button("Delete", key=f"delete_patient_{p['id']}"):
                        database.delete_patient(p['id'])
                        st.experimental_rerun()

        # show edit form if requested
        if st.session_state.get("editing_patient"):
            pid = st.session_state["editing_patient"]
            patient = database.get_patient(pid)
            if patient:
                st.subheader(f"Edit Patient #{pid}")
                with st.form(f"edit_patient_form_{pid}"):
                    name = st.text_input("Name", value=patient["name"])
                    age = st.number_input("Age", min_value=0, max_value=120, value=int(patient["age"] or 0))
                    gender = st.selectbox("Gender", ["", "Male", "Female", "Other"], index=(["", "Male", "Female", "Other"].index(patient["gender"]) if patient["gender"] in ["Male","Female","Other"] else 0))
                    contact = st.text_input("Contact", value=patient["contact"] or "")
                    notes = st.text_area("Notes", value=patient["notes"] or "")
                    btn = st.form_submit_button("Save")
                    if btn:
                        database.update_patient(pid, name.strip(), int(age), gender or None, contact or None, notes or None)
                        st.success("Patient updated.")
                        del st.session_state["editing_patient"]
                        st.experimental_rerun()
    else:
        st.write("No patients found.")


# ---------------------
# DOCTORS
# ---------------------
elif menu == "Doctors":
    st.header("Doctor Management")
    st.subheader("Add New Doctor")
    with st.form("add_doctor", clear_on_submit=True):
        name = st.text_input("Name", max_chars=100)
        specialty = st.text_input("Specialty (e.g., Cardiology)")
        working_hours = st.text_input("Working hours (HH:MM-HH:MM)", placeholder="09:00-17:00")
        contact = st.text_input("Contact")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Doctor")
        if submitted:
            if not name.strip():
                st.error("Name is required.")
            else:
                # basic validation for working_hours
                if working_hours:
                    parts = working_hours.split("-")
                    if len(parts) != 2 or not utils.validate_time_str(parts[0].strip())[0] or not utils.validate_time_str(parts[1].strip())[0]:
                        st.error("Working hours must be in format HH:MM-HH:MM (24h).")
                    else:
                        did = database.add_doctor(name.strip(), specialty or None, working_hours.strip(), contact or None, notes or None)
                        st.success(f"Doctor added with id #{did}")
                else:
                    did = database.add_doctor(name.strip(), specialty or None, None, contact or None, notes or None)
                    st.success(f"Doctor added with id #{did}")

    st.subheader("Doctor List")
    doctors = database.get_doctors()
    if doctors:
        for d in doctors:
            with st.expander(f"{d['id']}: {d['name']} - {d['specialty'] or ''}"):
                st.write(f"Specialty: {d['specialty'] or '—'}")
                st.write(f"Working hours: {d['working_hours'] or 'Not set'}")
                st.write(f"Contact: {d['contact'] or '—'}")
                st.write(f"Notes: {d['notes'] or '—'}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Edit", key=f"edit_doctor_{d['id']}"):
                        st.session_state.setdefault("editing_doctor", d['id'])
                with col2:
                    if st.button("Delete", key=f"delete_doctor_{d['id']}"):
                        database.delete_doctor(d['id'])
                        st.experimental_rerun()

        # edit form
        if st.session_state.get("editing_doctor"):
            did = st.session_state["editing_doctor"]
            doc = database.get_doctor(did)
            if doc:
                st.subheader(f"Edit Doctor #{did}")
                with st.form(f"edit_doctor_form_{did}"):
                    name = st.text_input("Name", value=doc["name"])
                    specialty = st.text_input("Specialty", value=doc["specialty"] or "")
                    working_hours = st.text_input("Working hours (HH:MM-HH:MM)", value=doc["working_hours"] or "")
                    contact = st.text_input("Contact", value=doc["contact"] or "")
                    notes = st.text_area("Notes", value=doc["notes"] or "")
                    btn = st.form_submit_button("Save")
                    if btn:
                        # Basic working hours validation
                        if working_hours:
                            parts = working_hours.split("-")
                            if len(parts) != 2 or not utils.validate_time_str(parts[0].strip())[0] or not utils.validate_time_str(parts[1].strip())[0]:
                                st.error("Working hours must be in format HH:MM-HH:MM (24h).")
                            else:
                                database.update_doctor(did, name.strip(), specialty or None, working_hours.strip(), contact or None, notes or None)
                                st.success("Doctor updated.")
                                del st.session_state["editing_doctor"]
                                st.experimental_rerun()
                        else:
                            database.update_doctor(did, name.strip(), specialty or None, None, contact or None, notes or None)
                            st.success("Doctor updated.")
                            del st.session_state["editing_doctor"]
                            st.experimental_rerun()
    else:
        st.write("No doctors found.")


# ---------------------
# APPOINTMENTS
# ---------------------
elif menu == "Appointments":
    st.header("Appointment Management")

    st.subheader("Book Appointment")
    patients = database.get_patients()
    doctors = database.get_doctors()

    if not patients:
        st.info("Please add patients before booking appointments.")
    if not doctors:
        st.info("Please add doctors before booking appointments.")

    with st.form("book_appointment", clear_on_submit=True):
        patient_options = {f"{p['id']}: {p['name']}": p['id'] for p in patients}
        doctor_options = {f"{d['id']}: {d['name']} ({d['specialty'] or '—'})": d['id'] for d in doctors}

        selected_patient_label = st.selectbox("Select patient", options=list(patient_options.keys())) if patients else None
        selected_doctor_label = st.selectbox("Select doctor", options=list(doctor_options.keys())) if doctors else None
        appt_date = st.date_input("Date", value=date.today())
        appt_time = st.text_input("Time (HH:MM)", placeholder="14:30")
        reason = st.text_input("Reason / Notes (optional)")

        submitted = st.form_submit_button("Book Appointment")
        if submitted:
            if not patients or not doctors:
                st.error("Need at least one patient and one doctor to book.")
            else:
                pid = patient_options[selected_patient_label]
                did = doctor_options[selected_doctor_label]
                date_str = appt_date.strftime("%Y-%m-%d")
                time_str = appt_time.strip()

                # Validate date/time formats
                ok_date, err = utils.validate_date_str(date_str)
                if not ok_date:
                    st.error(err)
                ok_time, err = utils.validate_time_str(time_str)
                if not ok_time:
                    st.error(err)
                else:
                    # Check doctor's working hours
                    doctor = database.get_doctor(did)
                    within, msg = utils.time_in_working_hours(doctor["working_hours"], time_str)
                    if not within:
                        st.error(msg)
                    else:
                        # Check double booking
                        existing = database.get_appointments_by_doctor_date_time(did, date_str, time_str)
                        if existing:
                            st.error("Selected doctor already has an appointment at that time.")
                        else:
                            success, err = database.add_appointment(did, pid, date_str, time_str, reason or None)
                            if success:
                                st.success("Appointment booked.")
                            else:
                                st.error(f"Failed to book appointment: {err}")

    st.subheader("Upcoming Appointments")
    appts = database.get_appointments(limit=200)
    if appts:
        for a in appts:
            with st.expander(f"#{a['id']}: {a['date']} {a['time']} — Dr. {a['doctor_name']} with {a['patient_name']}"):
                st.write(f"Reason: {a['reason'] or '—'}")
                st.write(f"Booked at: {a['created_at']}")
                if st.button("Cancel Appointment", key=f"cancel_appt_{a['id']}"):
                    database.delete_appointment(a['id'])
                    st.experimental_rerun()
    else:
        st.write("No appointments found.")
