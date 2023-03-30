from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/class/{course_number}")
def course_number(course_number: str, db: Session = Depends(get_db)):
    if class_found := crud.get_class(db, course_number):
        return class_found
    else:
        return HTTPException(status_code=404, detail=f"Course {course_number} not found, try with a space maybe?")


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
def prereqs_possbilities_for(
    course_number: str, db: Session = Depends(get_db)
) -> Any:
    return crud.get_prereqs_for_class(db, course_number)


@app.get("/postreq/{course_number}", response_model=list[str])
def postreq(
    course_number: str, subject_filter: str = None, db: Session = Depends(get_db)
):
    return crud.get_postreqs_for_class(db, course_number, subject_filter)


