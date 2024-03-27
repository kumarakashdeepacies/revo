import pandas as pd

from kore_investment.users.computations.file_storage import read_diskstorage


def create_mapped_data(mapping_data, col_mapping):

    data = pd.DataFrame()
    data = mapping_data

    cols_map_list = []
    for i in col_mapping:
        cols_map_list.append(i["col"])

    ori_data = data[data.columns.difference(cols_map_list)]

    for con in col_mapping:
        data2 = pd.DataFrame()
        d = read_diskstorage(con["data"])
        m_col = d[con["field"]].to_list()
        data2[con["col"]] = m_col
        ori_data = pd.concat([ori_data, data2], axis=1)

    return ori_data
