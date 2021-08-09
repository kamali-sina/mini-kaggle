import csv

from django.conf import settings

DEFAULT_ROW_NO = 10


def read_csv_dataset(filename):
    with open(f'{settings.MEDIA_ROOT}/{filename}', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        header = next(csv_reader)

        rows = []
        for row in csv_reader:
            if csv_reader.line_num > DEFAULT_ROW_NO:
                break
            rows.append(row)

        return {'header': header,
                'rows': rows
                }
