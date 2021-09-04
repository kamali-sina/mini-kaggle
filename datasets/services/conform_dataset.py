import pandas as pd
from datasets.models import DataSource


def conform_dataset(file, data_source: DataSource):
    if not data_source:
        return
    data_frame = pd.read_csv(file)
    columns = data_source.column_set.all()
    for column in columns:
        if column.title not in data_frame:
            error_message = "Conformation Error:\nColumn not found!\nExpected column: {}".format(column.title)
            raise Exception(error_message)
        if data_frame[column.title].dtypes != column.type:
            error_message = \
                "Conformation Error:\nTypes do not match!\nExpected type: {extype}.\nReceived type: {gottype}.".format(
                    extype=column.type, gottype=data_frame[column.title].dtypes)
            raise Exception(error_message)
