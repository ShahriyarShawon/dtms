from bs4 import BeautifulSoup
import requests
import re

ROOT_URL = "https://termmasterschedule.drexel.edu/webtms_du/"

class TMSScraper:
    def __init__(self):
        self.session = requests.Session()

    def get_college_codes(self, term: str):
        content = self.session.get(f"https://termmasterschedule.drexel.edu/webtms_du/collegesSubjects/{term}?collCode=").content
        soup = BeautifulSoup(content, "html.parser")
        return [a["href"].split("=")[-1] for a in soup.find(id="sideLeft").find_all("a")]

    def get_courses_for_college(self, coll_code: str):
        content = self.session.get(ROOT_URL).content
        soup = BeautifulSoup(content, "html.parser")
        #url = [url for url in [a["href"] for a in soup.find_all("a")]][0]
        college_page = self.session.get(f"https://termmasterschedule.drexel.edu/webtms_du/collegesSubjects/202215?collCode={coll_code}").content
        soup = BeautifulSoup(college_page, "html.parser")
        course_codes = [a["href"].split("/")[-1] for a in soup.find_all(class_="collegePanel")[0].find_all("a")]
        return course_codes
        #content = self.session.get("https://termmasterschedule.drexel.edu/webtms_du/courseList/CS")

        #soup = BeautifulSoup(content.text, "html.parser")
        #print(soup.find_all("title")[0])
        #print(soup.find(id="sortableTable"))
        #print(content)

    def get_classes_for_course(self, course_code: str):
        content = self.session.get(f"https://termmasterschedule.drexel.edu/webtms_du/courseList/{course_code}")
        soup = BeautifulSoup(content.text, "html.parser")
        breakpoint()        

if __name__ == "__main__":
    tms = TMSScraper()
    college_codes = tms.get_college_codes("202235")
    for code in college_codes:
        tms.get_courses_for_college(code)
