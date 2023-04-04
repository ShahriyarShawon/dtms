import sys

import click
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from dtms.database import Base, SessionLocal, engine
from dtms.mappings import col_to_courses
from dtms.models import DrexelClass, DrexelTMSClass

ROOT_URL = "https://termmasterschedule.drexel.edu/webtms_du/"
db = SessionLocal()


class TMSScraper:
    def __init__(self):
        self.session = requests.Session()
        self.term = None

    def select_term(self, term: str):
        self.term = term

    def _get_college_codes(self):
        content = self.session.get(
            f"https://termmasterschedule.drexel.edu/webtms_du/collegesSubjects/{self.term}?collCode="
        ).content
        soup = BeautifulSoup(content, "html.parser")
        return [
            a["href"].split("=")[-1] for a in soup.find(id="sideLeft").find_all("a")
        ]

    def _get_courses_for_college(self, coll_code: str):
        content = self.session.get(ROOT_URL).content
        soup = BeautifulSoup(content, "html.parser")
        college_page = self.session.get(
            f"https://termmasterschedule.drexel.edu/webtms_du/collegesSubjects/{self.term}?collCode={coll_code}"
        ).content
        soup = BeautifulSoup(college_page, "html.parser")
        course_codes = [
            a["href"].split("/")[-1]
            for a in soup.find_all(class_="collegePanel")[0].find_all("a")
        ]
        return course_codes

    def get_college_to_course_mapping(self):
        col_to_courses = {}
        courses_to_col = {}

        for col in self._get_college_codes():
            col_to_courses[col] = []
            for course in self._get_courses_for_college(col):
                col_to_courses[col].append(course)
                courses_to_col[course] = col
        print(f"col_to_courses = {col_to_courses}")
        print(f"courses_to_col = {courses_to_col}")

    def get_classes_for_course(self, course_code: str):
        content = self.session.get(
            f"https://termmasterschedule.drexel.edu/webtms_du/courseList/{course_code}"
        )
        soup = BeautifulSoup(content.text, "html.parser")
        table = soup.find(id="sortableTable")
        try:
            body = table.find_all("tbody")[0]
        except AttributeError:
            print(f"So far no classes for {course_code}")
            return []
        rows = [row.contents for row in body.contents if row != "\n"]
        classes = [self.get_info_from_class_row(row) for row in rows]
        return classes

    def mock_term_college_selection(self, college: str):
        self.session.get(
            f"https://termmasterschedule.drexel.edu/webtms_du/collegesSubjects/{self.term}?collCode={college}"
        )

    def get_info_from_class_row(self, row) -> list[DrexelClass]:
        row = [item for item in row if item != "\n"]
        subject_code = row[0].text
        course_number = subject_code + " " + row[1].text
        instruction_type = row[2].text
        instruction_method = row[3].text
        section = row[4].text
        crn = row[5].text
        days_time = (
            row[7]
            .find_all(class_="table-day-time")[0]
            .find_all("tr")[0]
            .text.strip()
            .replace("\n", " ")
        )
        instructors = row[8].text
        try:
            drexel_catalogue_id = (
                db.query(DrexelClass)
                .filter(DrexelClass.number == course_number)
                .first()
                .id
            )
        except AttributeError:
            print(
                f"Missing '{course_number}' from Drexel Course Catalogue",
                file=sys.stderr,
            )
            drexel_catalogue_id = None
        drexel_class = DrexelTMSClass(
            term=self.term,
            subject=subject_code,
            course_number=course_number,
            instruction_type=instruction_type,
            instruction_method=instruction_method,
            section=section,
            crn=crn,
            days_time=days_time,
            instructors=instructors,
            drexel_class_id=drexel_catalogue_id,
        )
        return drexel_class


@click.command()
@click.option(
    "--term",
    default="202235",
    help="Term in YYYYQQ format QQ => quarter format. eg 15 25 35 45",
)
def main(term: str):
    Base.metadata.create_all(engine)
    tms = TMSScraper()
    tms.select_term(term)
    classes: list[DrexelTMSClass] = []
    for coll_code, courses in list(col_to_courses.items()):
        # print(f"College: {coll_code}")
        tms.mock_term_college_selection(coll_code)
        for course in courses:
            # print(f"Course: {course}")
            classes.extend(tms.get_classes_for_course(course))
    with Session(engine) as session:
        session.query(DrexelTMSClass).filter(DrexelTMSClass.term == term).delete()
        session.add_all(classes)
        session.commit()
        db.close()


if __name__ == "__main__":
    main()
