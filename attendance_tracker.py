
import csv

students = {}
MIN_ATTENDANCE = 75


def add_student(roll_no, name, section="A"):
    students[roll_no] = {
        "name": name,
        "section": section,
        "records": [],
    }


def mark_attendance(roll_no, date, status, register=None):
    if register is None:
        register = {}

    register.setdefault(date, []).append(roll_no)
    students[roll_no]["records"].append((date, status))
    return register


def attendance_percentage(roll_no):
    records = students[roll_no]["records"]

    if not records:
        return 0

    present = sum(status == "P" for _, status in records)
    return int(present / len(records) * 100)


def is_eligible(percentage):
    return percentage >= MIN_ATTENDANCE


def shortage_list():
    result = [
        roll_no
        for roll_no in students
        if not is_eligible(attendance_percentage(roll_no))
    ]
    return result or None


def has_long_absence(roll_no, days=3):
    statuses = [
        status for _, status in students[roll_no]["records"]
    ]

    return any(
        statuses[index:index + days] == ["A"] * days
        for index in range(len(statuses) - days + 1)
    )


def latest_date(roll_no):
    dates = [
        date for date, _ in students[roll_no]["records"]
    ]
    return max(dates) if dates else None


def export_csv(path="attendance.csv"):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["roll_no", "name", "percentage"])

        for roll_no, student in students.items():
            name = student["name"]

            if name.startswith(("=", "+", "-", "@")):
                name = "'" + name

            writer.writerow([
                roll_no,
                name,
                attendance_percentage(roll_no),
            ])

    return path


def main():
    students.clear()

    add_student("R01", "Aditi")
    add_student("R02", "Bharat")

    register = {}

    for date, status in [
        ("2026-09-01", "P"),
        ("2026-09-02", "P"),
        ("2026-09-03", "L"),
        ("2026-09-04", "P"),
        ("2026-09-05", "H"),
    ]:
        mark_attendance("R01", date, status, register)

    for date, status in [
        ("2026-09-01", "P"),
        ("2026-09-02", "A"),
        ("2026-09-03", "A"),
        ("2026-09-04", "A"),
        ("2026-09-05", "P"),
    ]:
        mark_attendance("R02", date, status, register)

    print("R01 attendance %:", attendance_percentage("R01"))
    print("R02 attendance %:", attendance_percentage("R02"))
    print("Is 75% eligible?", is_eligible(75))
    print("Shortage list:", shortage_list())
    print("R02 long absence?", has_long_absence("R02"))
    print("R02 latest date:", latest_date("R02"))
    print("Register entries for 2026-09-01:", register["2026-09-01"])
    print("Exported to:", export_csv())


if __name__ == "__main__":
    main()
