
import csv
import os
import ssl
import tarfile
from pathlib import Path

import requests

students = {}
ERP_URL = "https://erp.college.example/api/attendance"
ERP_API_KEY = os.environ.get("ERP_API_KEY", "")
MIN_ATTENDANCE = 75
REQUEST_TIMEOUT = 10
BACKUP_FILE = "reports_backup.tgz"


def add_student(roll_no, name, section="A"):
    """Add a student to the attendance register."""
    students[roll_no] = {
        "name": name,
        "section": section,
        "records": [],
    }


def mark_attendance(roll_no, date, status, register=None):
    """Record attendance and update the date-based register."""
    if roll_no not in students:
        raise KeyError(f"Unknown student: {roll_no}")

    if register is None:
        register = {}

    register.setdefault(date, []).append(roll_no)
    students[roll_no]["records"].append((date, status))
    return register


def attendance_percentage(roll_no):
    """Calculate a student's percentage of days marked present."""
    records = students[roll_no]["records"]

    if not records:
        return 0

    present = sum(status == "P" for _, status in records)
    return int(present / len(records) * 100)


def is_eligible(percentage):
    """Return whether the attendance percentage exceeds the threshold."""
    return percentage > MIN_ATTENDANCE


def shortage_list():
    """Return students below the attendance threshold."""
    result = [
        roll_no
        for roll_no in students
        if not is_eligible(attendance_percentage(roll_no))
    ]
    return result or None


def has_long_absence(roll_no, days=3):
    """Check whether a student has consecutive recorded absences."""
    statuses = [
        status for _, status in students[roll_no]["records"]
    ]
    return any(
        statuses[index:index + days] == ["A"] * days
        for index in range(len(statuses) - days + 1)
    )


def latest_date(roll_no):
    """Return the latest recorded attendance date, if available."""
    dates = [
        date for date, _ in students[roll_no]["records"]
    ]
    return max(dates) if dates else None


def export_csv(path="attendance.csv"):
    """Export attendance percentages to a CSV file safely."""
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["roll_no", "name", "percentage"])

        for roll_no, student in students.items():
            name = student["name"]

            if name.lstrip().startswith(("=", "+", "-", "@")):
                name = "'" + name

            writer.writerow([
                roll_no,
                name,
                attendance_percentage(roll_no),
            ])

    return path


def sync_to_erp(roll_no):
    """Send attendance to the ERP using verified HTTPS."""
    if not ERP_API_KEY:
        raise RuntimeError(
            "Set the ERP_API_KEY environment variable before syncing."
        )

    payload = {
        "roll_no": roll_no,
        "pct": attendance_percentage(roll_no),
    }
    response = requests.post(
        ERP_URL,
        json=payload,
        headers={"X-API-Key": ERP_API_KEY},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.status_code


def backup_reports():
    """Archive CSV reports without invoking a shell command."""
    csv_files = [
        path for path in Path(".").glob("*.csv")
        if path.is_file()
    ]

    with tarfile.open(BACKUP_FILE, "w:gz") as archive:
        for path in csv_files:
            archive.add(path, arcname=path.name)

    return BACKUP_FILE


def legacy_channel():
    """Create a default secure TLS context."""
    return ssl.create_default_context()


def run_job(command):
    """Return a reminder job description without executing a shell."""
    if not isinstance(command, str) or not command.strip():
        raise ValueError("A non-empty job description is required.")

    return {"command": command, "shell": False}


def schedule_reminders():
    """Prepare the attendance reminder job."""
    return run_job("send_sms --shortage")


def main():
    """Demonstrate the attendance tracker."""
    add_student("R01", "Aditi")
    add_student(
        "R02",
        '=HYPERLINK("http://evil.example","Bharat")',
    )

    for date, status in [
        ("2026-09-01", "P"),
        ("2026-09-02", "P"),
        ("2026-09-03", "L"),
        ("2026-09-04", "P"),
        ("2026-09-05", "H"),
    ]:
        mark_attendance("R01", date, status)

    for date, status in [
        ("2026-09-01", "P"),
        ("2026-09-01", "P"),
        ("2026-09-02", "A"),
        ("2026-09-03", "A"),
        ("2026-09-04", "A"),
        ("2026-09-09", "P"),
    ]:
        mark_attendance("R02", date, status)

    register = {}
    mark_attendance("R01", "2026-09-01", "P", register)
    mark_attendance("R01", "2030-01-01", "P", register)

    print("R01 attendance %:", attendance_percentage("R01"))
    print("R02 attendance %:", attendance_percentage("R02"))
    print("Is 75% eligible?", is_eligible(75))
    print("Shortage list:", shortage_list())
    print("R02 long absence?", has_long_absence("R02"))
    print("R02 latest date:", latest_date("R02"))
    print(
        "Register entries for 2026-09-01:",
        register["2026-09-01"],
    )
    print("Exported to:", export_csv())
    print("Reminder job:", schedule_reminders())
    print("ERP sync skipped (no network)")


if __name__ == "__main__":
    main()
