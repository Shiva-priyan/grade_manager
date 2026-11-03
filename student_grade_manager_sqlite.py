"""Student Grade Manager (SQLite version): store students in a database, show them in a table."""

import math
import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent / "students.db"

GRADE_BANDS = ((90, "A"), (80, "B"), (70, "C"), (60, "D"))


def get_grade(mark: float) -> str:
    for minimum, grade in GRADE_BANDS:
        if mark >= minimum:
            return grade
    return "E"


def init_db(conn: sqlite3.Connection) -> None:
    """Create the students table the first time the program runs."""
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT NOT NULL,
                mark  REAL NOT NULL CHECK (mark BETWEEN 0 AND 100),
                grade TEXT NOT NULL
            )
            """
        )


def add_student(conn: sqlite3.Connection) -> None:
    name = input("Enter student name: ").strip()
    if not name:
        print("Student name cannot be empty.")
        return

    try:
        mark = float(input("Enter student mark: "))
    except ValueError:
        print("Invalid input! Please enter a number.")
        return

    if not math.isfinite(mark):
        print("Invalid mark! Please enter a valid number.")
        return

    if not 0 <= mark <= 100:
        print("Marks must be between 0 and 100.")
        return

    try:
        with conn:  # commits on success, rolls back on error
            conn.execute(
                "INSERT INTO students (name, mark, grade) VALUES (?, ?, ?)",
                (name, mark, get_grade(mark)),
            )
    except sqlite3.Error as error:
        print(f"Could not save the student: {error}")
        return

    print(f"Student {name} added and saved successfully!")


def show_results(conn: sqlite3.Connection) -> bool:
    """Retrieve all students from the database and print them as a table."""
    rows = conn.execute("SELECT name, mark, grade FROM students ORDER BY id").fetchall()

    if not rows:
        print("No student records available.")
        return False

    line = "-" * 37
    print(f"\n{line}\n         STUDENT RESULTS\n{line}")
    print(f"{'Name':<15} {'Mark':<10} {'Grade':<10}")
    print(line)
    for name, mark, grade in rows:
        print(f"{name:<15} {mark:<10.1f} {grade:<10}")
    print(line)
    return True


def show_statistics(conn: sqlite3.Connection) -> None:
    average, highest, lowest = conn.execute(
        "SELECT AVG(mark), MAX(mark), MIN(mark) FROM students"
    ).fetchone()

    line = "-" * 37
    print(f"\n{line}\n         CLASS STATISTICS\n{line}")
    print(f"Class Average: {average:.1f}")
    print(f"Highest Mark:  {highest:.1f}")
    print(f"Lowest Mark:   {lowest:.1f}")
    print(line)


def main() -> None:
    try:
        conn = sqlite3.connect(DB_FILE)
        init_db(conn)
    except sqlite3.Error as error:
        print(f"Could not open the database: {error}")
        return

    try:
        while True:
            print("\n=====================================")
            print("       STUDENT GRADE MANAGER")
            print("=====================================")
            print("1. Add Student")
            print("2. Show Results")
            print("3. Quit")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                add_student(conn)
            elif choice == "2":
                if show_results(conn):
                    show_statistics(conn)
            elif choice == "3":
                print("Thank you for using Student Grade Manager!")
                break
            else:
                print("Invalid choice! Please select 1, 2 or 3.")
    except (EOFError, KeyboardInterrupt):
        print("\nExiting. All added students were already saved.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
    