from pydantic import BaseModel  # pylint: disable=no-name-in-module


class DrexelCourseCatalogueClassBase(BaseModel):
    college: str
    subject: str
    number: str
    name: str
    low_credits: float
    high_credits: float
    writing_intensive: bool
    prereqs: str
    desc: str


class DrexelCourseCatalogueClassCreate(DrexelCourseCatalogueClassBase):
    pass


class DrexelCourseCatalogue(DrexelCourseCatalogueClassBase):
    id: int

    class Config:
        orm_mode = True


class DrexelTMSClassBase(BaseModel):
    term: str
    subject: str
    course_number: str
    instruction_type: str
    instruction_method: str
    section: str
    crn: str
    days_time: str
    instructors: str


class DrexelTMSClassCreate(DrexelTMSClassBase):
    pass


class DrexelTMS(DrexelTMSClassBase):
    id: int
    drexel_class: DrexelCourseCatalogue

    class Config:
        orm_mode = True
