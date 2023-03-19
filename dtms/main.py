from typing import Any
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/classes/term/", response_model=list[schemas.DrexelTMS])
def classes_for_term(
    term: str,
    subject: str = None,
    college: str = None,
    credit_hours: int = None,
    prereq: str = None,
    instructor: str = None,
    writing_intensive: bool = False,
    db: Session = Depends(get_db),
):
    return crud.get_classes_for_term(
        db, term, college, subject, credit_hours, prereq, instructor, writing_intensive
    )


@app.get("/prereqs_for/{course_number}", response_model=list[str])
def prereqs_possbilities_for(course_number: str, db: Session = Depends(get_db)) -> Any:
    return crud.get_prereqs_for_class(db, course_number)


# @app.get(
#    "/classes_in/{subject}", response_model=list[schemas.DrexelCourseCatalogue]
# )
# def index(subject: str, db: Session = Depends(get_db)):
#    return crud.get_classes_by_subject(db, subject)
#
#
# @app.get("/classes/")
# def classes(credits: int = None, db: Session = Depends(get_db)):
#    return crud.get_classes(db, credits=credits)
