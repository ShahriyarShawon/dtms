from bs4 import BeautifulSoup
import requests
from attrs import define

@define 
class DrexelClass:
    course_category: str
    course_number: str
    instruction_type: str
    instruction_method: str
    section: str
    crn: str
    course_title: str
    days_time: str
    instructor_string: str
    #max_enroll: str
    #enroll: str

@define 
class DrexelCourse:
    course_name: str
    course_code: str 
    classes: list[DrexelClass]

@define 
class DrexelCollege:
    college_code: str
    courses: list[DrexelCourse]

ROOT_URL = "https://termmasterschedule.drexel.edu/webtms_du/"

class TMSScraper:
    def __init__(self):
        self.session = requests.Session()
        self.term = None

    def select_term(self, term: str):
        self.term = term

    def get_college_codes(self):
        content = self.session.get(f"https://termmasterschedule.drexel.edu/webtms_du/collegesSubjects/{self.term}?collCode=").content
        soup = BeautifulSoup(content, "html.parser")
        return [a["href"].split("=")[-1] for a in soup.find(id="sideLeft").find_all("a")]

    def get_courses_for_college(self, coll_code: str):
        content = self.session.get(ROOT_URL).content
        soup = BeautifulSoup(content, "html.parser")
        college_page = self.session.get(f"https://termmasterschedule.drexel.edu/webtms_du/collegesSubjects/{self.term}?collCode={coll_code}").content
        soup = BeautifulSoup(college_page, "html.parser")
        course_codes = [a["href"].split("/")[-1] for a in soup.find_all(class_="collegePanel")[0].find_all("a")]
        return course_codes

    def get_classes_for_course(self, course_code: str):
        content = self.session.get(f"https://termmasterschedule.drexel.edu/webtms_du/courseList/{course_code}")
        soup = BeautifulSoup(content.text, "html.parser")
        table = soup.find(id="sortableTable")
        body = table.find_all("tbody")[0]
        rows = [row.contents for row in body.contents if row != "\n"]
        classes = [self.get_info_from_class_row(row) for row in rows]
        return classes

    def get_info_from_class_row(self, row) -> list[DrexelClass]:
        row = [item for item in row if item != "\n"]
        subject_code = row[0].text
        course_number = row[1].text
        instruction_type = row[2].text
        instruction_method = row[3].text
        section = row[4].text
        crn = row[5].text
        course_title = row[6].text
        days_time = row[7].find_all(class_="table-day-time")[0].find_all("tr")[0].text.strip().replace("\n", " ")
        instructors = row[8].text
        drexel_class = DrexelClass(
            subject_code,
            course_number,
            instruction_type,
            instruction_method,
            section,
            crn,
            course_title,
            days_time,
            instructors,
        )
        return drexel_class
    
    #def get_info_from_crn(self, crn, course_number):
    #    url = f"https://termmasterschedule.drexel.edu/webtms_du/courseDetails/{crn}?crseNumb={course_number}"
    #    content = self.session.get(url).content
    #    soup = BeautifulSoup(content, "html.parser")
    #    breakpoint()

if __name__ == "__main__":
    tms = TMSScraper()
    # optimal workflow
    tms.select_term("202235")
    colleges = tms.get_college_codes()
    classes: list[DrexelClass] = [] 
    for college in colleges:
        courses = tms.get_courses_for_college(college)
        for course in courses:
            classes.extend(tms.get_classes_for_course(course))
    print("Course Category, Course Number, Instr Type, Instr Method, Section, CRN, Course Title, Days Time, Instructor(s)")
    for c in classes:
        print(f"{c.course_category},{c.course_number},{c.instruction_type},{c.instruction_method},{c.section},{c.crn},{c.course_title},{c.days_time},{c.instructor_string}")