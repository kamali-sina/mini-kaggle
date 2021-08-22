import csv

from django.conf import settings

DEFAULT_ROW_NO = 10


def read_csv_dataset(filename, row_number=None):
    if row_number is None:
        row_number = DEFAULT_ROW_NO

    with open(f'{settings.MEDIA_ROOT}/{filename}', 'r', encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file)

        header = next(csv_reader)

        rows = []
        for row in csv_reader:
            if csv_reader.line_num > row_number:
                break
            rows.append(row)

        return {'header': header,
                'rows': rows
                }
