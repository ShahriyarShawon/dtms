import requests
from bs4 import BeautifulSoup
import click
from mappings import college_code_mapping, subject_codes

def get_courses_in_subject():
    pass

def get_subject_urls_in_college(college_url: str):
    college_page = requests.get(college_url).content
    college_page_soup = BeautifulSoup(college_page, "html.parser")  
    college_subjects = college_page_soup.find_all(class_="collegePanel")[0].find_all("a")
    for subject in college_subjects:
        print(subject["href"], subject.text)

@click.command()
@click.option("-t", "--term")
def main(term: str):
    TMS_ROOT = "https://termmasterschedule.drexel.edu/webtms_du/collegesSubjects"
    TMS_URL = f"{TMS_ROOT}/{term}"

    cookies = "82551D59C874AE30834E4A52A16C8DA8"
    for subject, name in [list(subject_codes.items())[9]]:
        course_site = f"https://termmasterschedule.drexel.edu/webtms_du/courseList/{subject}"
        print(course_site)
        course_soup = BeautifulSoup(requests.get(course_site, cookies={"JSESSIONID":cookies}).content, "html.parser")
        rows = course_soup.find(id="sortableTable").find_all("tbody")[0].find_all("tr")
        print(rows)

if __name__ == "__main__":
    main()