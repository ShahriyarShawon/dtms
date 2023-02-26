import sys

import requests
from bs4 import BeautifulSoup, ResultSet
from dtms.database import Base, engine
from dtms.mappings import subject_codes, courses_to_col
from dtms.models import DrexelClass
from sqlalchemy.orm import Session
from yarl import URL

url_base = URL("https://catalog.drexel.edu/coursedescriptions/quarter/undergrad/")


def get_class_info_in_block(result: ResultSet, subject: str) -> DrexelClass:
    title_block = result.find_all(class_="courseblocktitle")[0]
    title_block_children = [child for child in title_block.find("strong").children]
    course_number = title_block_children[0].text.strip().replace("\xa0", "")
    if "[WI]" in course_number:
        course_number = course_number.replace("[WI]", "").strip()
        writing_intensive = True
    else:
        writing_intensive = False
    course_name = title_block_children[1].text.strip().replace("\xa0", "")
    course_credits = title_block_children[2].text.strip().replace("\xa0", "")
    if "-" in course_credits:
        creds = course_credits.split("-")
        min_credits = float(creds[0])
        max_credits = float(creds[1])
    else:
        min_credits = max_credits = float(course_credits)

    desc = result.find_all(class_="courseblockdesc")[0].text.strip().replace("\xa0", "")
    children = [child for child in result.children]

    prereqs = ""
    for idx, child in enumerate(children):
        if "Prerequisites" in child.text.strip().replace("\xa0", ""):
            prereqs = children[idx + 1].text.strip().replace("\xa0", "").strip()
            break
    c = DrexelClass(
        college=courses_to_col[subject],
        subject=subject,
        number=course_number,
        name=course_name,
        low_credits=min_credits,
        high_credits=max_credits,
        prereqs=prereqs,
        desc=desc,
        writing_intensive=writing_intensive,
    )
    return c


def get_classes_for_subject(subject: str):
    print(f"Getting classses for {subject}", file=sys.stderr)
    url = url_base / subject.lower()
    content = requests.get(url).content #pylint: disable=missing-timeout
    soup = BeautifulSoup(content, "html.parser")

    course_blocks = soup.find_all(class_="courseblock")
    return [get_class_info_in_block(block, subject) for block in course_blocks]


if __name__ == "__main__":
    Base.metadata.create_all(engine)

    all_classes = []
    with Session(engine) as session:
        for subject in subject_codes.keys():
            all_classes.extend(get_classes_for_subject(subject))
            session.add_all(all_classes)
            session.commit()