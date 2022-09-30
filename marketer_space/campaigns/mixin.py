import csv

from marketer_space.settings import EMAIL_HOST_USER

from accounts.utils import send_mail
from .serializers import ContactSerializers


class UploadFileMixin:

    @staticmethod
    def create_contact(csv_path, contact_list, user_email):
        contacts = csv.DictReader(open(csv_path))
        content = "created contact data: \n {} \n " \
                  "not created due to validation: \n {}"
        errors = []
        data = []
        for row_id, item in enumerate(contacts):
            item['contact_list'] = contact_list
            serializer = ContactSerializers(data=item)
            if serializer.is_valid():
                serializer.save()
                data.append(serializer.data)
            else:
                error = serializer.errors
                error['row_id'] = row_id
                errors.append(error)

        print(content.format(data, errors))
        send_mail(
            'Marketer Space',
            content.format(data, errors),
            EMAIL_HOST_USER,
            [user_email]
        )
