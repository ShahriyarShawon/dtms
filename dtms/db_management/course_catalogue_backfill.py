import grequests
from bs4 import BeautifulSoup, ResultSet
from sqlalchemy.orm import Session
from yarl import URL

from dtms.database import Base, engine
from dtms.mappings import courses_to_col, subject_codes
from dtms.models import DrexelClass

url_base = URL("https://catalog.drexel.edu/coursedescriptions/quarter/")


def get_class_info_in_block(result: ResultSet, subject: str) -> DrexelClass:
    title_block = result.find_all(class_="courseblocktitle")[0]
    title_block_children = [child for child in title_block.find("strong").children]
    course_number = title_block_children[0].text.strip().replace("\xa0", " ")
    if "[WI]" in course_number:
        course_number = course_number.replace("[WI]", "").strip()
        writing_intensive = True
    else:
        writing_intensive = False
    course_name = title_block_children[1].text.strip().replace("\xa0", " ")
    course_credits = title_block_children[2].text.strip().replace("\xa0", "")
    if "-" in course_credits:
        creds = course_credits.split("-")
        min_credits = float(creds[0])
        max_credits = float(creds[1])
    elif "," in course_credits:
        creds = course_credits.split(",")
        min_credits = float(creds[0])
        max_credits = float(creds[1])
    else:
        try:
            min_credits = max_credits = float(course_credits)
        except ValueError:
            print(f"Could not get min max creds for {course_number}")
            raise

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


def get_classes_for_subject(response):
    subject = response.url.split("/")[-2].upper()
    content = response.content
    soup = BeautifulSoup(content, "html.parser")

    course_blocks = soup.find_all(class_="courseblock")
    return [get_class_info_in_block(block, subject) for block in course_blocks]


if __name__ == "__main__":
    Base.metadata.create_all(engine)

    all_classes = []
    with Session(engine) as session:
        session.query(DrexelClass).delete()
        urls = [
            url_base / "undergrad" / subject.lower() for subject in subject_codes.keys()
        ]
        urls.extend(
            [url_base / "grad" / subject.lower() for subject in subject_codes.keys()]
        )
        requests = (grequests.get(u) for u in urls)
        responses = [
            r for r in grequests.map(requests) if r is not None and r.status_code == 200
        ]
        for response in responses:
            all_classes.extend(get_classes_for_subject(response))
        session.add_all(all_classes)
        session.commit()
