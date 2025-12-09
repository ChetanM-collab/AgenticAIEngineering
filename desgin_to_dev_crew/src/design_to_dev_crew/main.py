#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from design_to_dev_crew.crew import DesignToDevCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the DesignToDev Builder crew.

    It will:
    - Take high-level requirements
    - Produce a design
    - Generate backend & frontend skeletons
    - Create a test plan
    - Perform a peer review
    """
    
    print("=== DesignToDev Crew ===")
    print("This crew turns your requirements into design + code skeletons + tests.\n")

    # ---- Collect inputs for the YAML variables -----------------------------

    requirements = """
    Build a small web application called "Tutoring Session Manager" that allows a tutor to manage students, sessions, and basic payments.

    1. Student Management
    - The tutor can create a new student with: first name, last name, parent/guardian name, contact email, contact phone, school year, and optional notes.
    - The tutor can view a list of all students, including name, school year, and the number of upcoming sessions.
    - The tutor can edit student details.
    - The tutor can archive (soft delete) a student so they no longer appear in active lists, but their historical sessions are preserved.

    2. Session Management
    - The tutor can create a tutoring session linked to an existing student.
    - A session includes: student, date, start time, end time, subject, session type (Online or In-person), status (Scheduled, Completed, Cancelled), hourly rate, and optional notes.
    - The system should automatically calculate the session duration in minutes/hours and the total fee (duration × hourly rate).
    - The tutor can view upcoming sessions sorted by date/time.
    - The tutor can filter sessions by student, date range, and status.
    - The tutor can mark a session as Completed and record: attendance (Attended, No-show, Late) and payment status (Paid, Unpaid, Partially paid).
    - The tutor can cancel a session and optionally record a cancellation reason.

    3. Payment Tracking
    - For each session, store payment status (Paid, Unpaid, Partially paid), payment method (optional), and payment date if paid.
    - Provide a simple “Outstanding Payments” view showing all unpaid or partially paid sessions with student name, date, total fee, and amount outstanding.
    - The tutor can update payment status from this view.

    4. Summary / Reports
    - Provide a summary for any date range including: total sessions, completed sessions, cancelled sessions, total fees for completed sessions, and total amount paid vs unpaid.
    - The tutor must be able to select a date range (e.g. last 30 days, current month, or custom range).

    5. Frontend Requirements
    - The frontend must be a modern JavaScript single-page application (e.g. React).
    - Must include pages for: Students, Sessions, Outstanding Payments, and Summary.
    - Forms must include basic validation such as required fields, valid email, and ensuring end time is after start time.
    - The frontend communicates with the backend via REST APIs.

    6. Backend Requirements
    - The backend must be a Spring Boot REST API.
    - Expose endpoints for CRUD operations on Students and Sessions.
    - Provide endpoints for filtering sessions by student, date range, and status.
    - Provide endpoints for outstanding payments and summary statistics.
    - Use a relational data model (e.g. Student, Session, Payment or embedded payment fields).
    - Backend must be structured so authentication and more reports can be added later.
    """

    if not requirements:
        print("You must provide some requirements. Exiting.")
        return

    app_name = (
        input("App name [tutoring-session-manager]: ").strip() or "tutoring-session-manager"
    )

    frontend_module_name = (
        input("\nFrontend module name [frontend-app]: ").strip() or "frontend-app"
    )
    backend_module_name = (
        input("Backend module name [backend-service]: ").strip() or "backend-service"
    )
    package_name_prefix = (
        input("Backend package prefix [com.example.app]: ").strip() or "com.example.app"
    )

    inputs = {
        "requirements": requirements,
        "app_name": app_name,
        "frontend_module_name": frontend_module_name,
        "backend_module_name": backend_module_name,
        "package_name_prefix": package_name_prefix,
    }

    print("\nKicking off crew with:")
    for k, v in inputs.items():
        print(f"  {k}: {v}")
    print("\nRunning crew... this may take a little while.\n" + "-" * 60)

    # ---- Run the crew ------------------------------------------------------

    crew = DesignToDevCrew().crew()
    result = crew.kickoff(inputs=inputs)

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(result)
    print("\nDone.")


def train() -> None:
    """
    Optional: training entrypoint if you want to use crew.train(...)
    Not strictly required for your demo, but left here for completeness.
    """
    print("Training is not configured yet. Add crew.train(...) logic here if needed.")


if __name__ == "__main__":
    run()