# Input data files are available in the read-only "/datasets/" directory
# For example, running this (by clicking run) will read a csv dataset under the name 'my_dataset' into header and rows

import csv

with open('/datasets/my_dataset.csv', 'r', encoding="utf8") as csv_file:
    csv_reader = csv.reader(csv_file)

    header = next(csv_reader)

    rows = []
    for row in csv_reader:
        rows.append(row)
