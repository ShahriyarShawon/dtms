from sqlalchemy.orm import Session
from dtms.prereq_parser import get_paths

from .models import DrexelClass, DrexelTMSClass

def get_prereqs_for_class(db: Session, class_number: str):
    prereq_str = (
        db.query(DrexelClass).filter(DrexelClass.number == class_number.replace(" ", "")).first().prereqs
    )
    return get_paths(prereq_str)

def get_postreqs_for_class(db: Session, class_number: str):
    postreq_classes = (
        db.query(DrexelClass).filter(DrexelClass.prereqs.like(f"%{class_number}%")).all()
    )
    return [postreq.number for postreq in postreq_classes]


def get_classes_for_term(
    db: Session,
    term: str,
    college: str = None,
    subject: str = None,
    credit_hours: int = None,
    prereq: str = None,
    instructor: str = None,
    writing_intensive: bool = False,
):
    tms_classes = db.query(DrexelTMSClass)
    course_catalogue = db.query(DrexelClass)

    if college:
        course_catalogue = course_catalogue.filter(DrexelClass.college == college)
    if subject:
        course_catalogue = course_catalogue.filter(DrexelClass.subject == subject)
    if credit_hours:
        course_catalogue = course_catalogue.filter(
            DrexelClass.high_credits == credit_hours
        )
    if prereq:
        course_catalogue = course_catalogue.filter(
            DrexelClass.prereqs.like(f"%{prereq}%")
        )
    course_catalogue = course_catalogue.filter(
        DrexelClass.writing_intensive == writing_intensive
    )

    if instructor:
        tms_classes = tms_classes.filter(DrexelTMSClass.instructors.like(f"%{instructor}%"))
    tms_classes = tms_classes.filter(
        DrexelTMSClass.term == term, 
    ).all()
    course_numbers = [course.id for course in course_catalogue.all()]
    final_result = [
        tmsc for tmsc in tms_classes if tmsc.drexel_class_id in course_numbers
    ]
    return final_result
