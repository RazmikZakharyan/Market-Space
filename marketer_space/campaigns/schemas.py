from pydantic import BaseModel


class ContactSchema(BaseModel):
    first_name: str
    last_name: str
    mail: str
    company_name: str
    job_title: str
