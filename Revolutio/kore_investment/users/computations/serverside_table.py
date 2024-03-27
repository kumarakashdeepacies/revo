import logging
import re


class ServerSideTable:
    """
    Retrieves the values specified by Datatables in the request and processes
    the data that will be displayed in the table (filtering, sorting and
    selecting a subset of it).

    Attributes:
        request: Values specified by DataTables in the request.
        data: Data to be displayed in the table.
        column_list: Schema of the table that will be built. It contains
                     the name of each column (both in the data and in the
                     table), the default values (if available) and the
                     order in the HTML.
    """

    def __init__(
        self,
        request,
        data,
        column_list,
        r_len,
        allow_ids,
        allow_ids_resend,
        allow_ids_edit,
        table_name_column_verbose_name,
    ):
        self.result_data = None
        self.cardinality_filtered = 0
        self.cardinality = 0

        self.request_values = request.POST
        self.columns = sorted(column_list, key=lambda col: col["order"])

        rows = self._extract_rows_from_data(data)
        self.r_len = r_len
        self.allow_ids = allow_ids
        self.allow_ids_resend = allow_ids_resend
        self.allow_ids_edit = allow_ids_edit
        self.table_name_column_verbose_name = table_name_column_verbose_name
        self._run(rows)

    def _run(self, data):
        """
        Prepares the data, and values that will be generated as output.
        It does the actual filtering, sorting and paging of the data.

        Args:
            data: Data to be displayed by DataTables.
        """
        self.cardinality = len(data)  # Total num. of rows

        self.cardinality_filtered = len(data)  # Num. displayed rows

        sorted_data = self._custom_sort(data)
        self.result_data = self._custom_paging(sorted_data)

    def _extract_rows_from_data(self, data):
        """
        Extracts the value of each column from the original data using the
        schema of the table.

        Args:
            data: Data to be displayed by DataTables.

        Returns:
            List of dicts that represents the table's rows.
        """
        rows = []
        for x in data:
            row = {}
            for column in self.columns:
                default = column["default"]
                data_name = column["data_name"]
                column_name = column["column_name"]
                row[column_name] = x.get(data_name, default)
            rows.append(row)
        return rows

    def _custom_filter(self, data):
        """
        Filters out those rows that do not contain the values specified by the
        user using a case-insensitive regular expression.

        It takes into account only those columns that are 'searchable'.

        Args:
            data: Data to be displayed by DataTables.

        Returns:
            Filtered data.
        """
        #    ''' Checks whether a row should be displayed or not. '''

        def check_row(row, i):
            """Checks whether a row should be displayed or not."""
            if self.columns[i]["searchable"]:
                value = row[self.columns[i]["column_name"]]
                regex = "(?i)" + self.request_values["columns[" + str(i) + "][search][value]"]
                if re.compile(regex).search(str(value)):
                    return True

        try:
            for i in range(len(self.columns)):
                if self.request_values["columns[" + str(i) + "][search][value]"] not in ["", None, "None"]:
                    return [row for row in data if check_row(row, i)]
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
            return data

        return data

        # raise Exception

    def _custom_sort(self, data):
        """
        Sorts the rows taking in to account the column (or columns) that the
        user has selected.

        Args:
            data: Filtered data.

        Returns:
            Sorted data by the columns specified by the user.
        """

        def is_reverse(str_direction):
            """Maps the 'desc' and 'asc' words to True or False."""
            return True if str_direction == "desc" else False

        for i in reversed(self.request_values):
            if i.startswith("order") and i.endswith("][column]"):
                length_of_columns = int(i[6 : i.index("][column]")]) + 1
                break

        if (self.request_values["order[0][column]"] != "") and length_of_columns > 0:
            for i in range(0, length_of_columns):
                column_number = int(self.request_values["order[" + str(i) + "][column]"])
                column_name = self.columns[column_number]["column_name"]
                sort_direction = self.request_values["order[" + str(i) + "][dir]"]
                # When string is compared to int/float, catch error and
                # instead convert all values to string first
                try:
                    data = sorted(data, key=lambda x: x[column_name], reverse=is_reverse(sort_direction))
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    data = sorted(data, key=lambda x: str(x[column_name]), reverse=is_reverse(sort_direction))

            return data
        else:
            return data

    def _custom_paging(self, data):
        """
        Selects a subset of the filtered and sorted data based on if the table
        has pagination, the current page and the size of each page.

        Args:
            data: Filtered and sorted data.

        Returns:
            Subset of the filtered and sorted data that will be displayed by
            the DataTables if the pagination is enabled.
        """

        def requires_pagination():
            """Check if the table is going to be paginated"""
            if self.request_values["start"] != "":
                if int(self.request_values["length"]) != -1:
                    return True
            return False

        if not requires_pagination():
            return data

        return data

    def output_result(self):
        """
        Generates a dict with the content of the response. It contains the
        required values by DataTables (echo of the reponse and cardinality
        values) and the data that will be displayed.

        Return:
            Content of the response.
        """
        output = {}
        output["sEcho"] = str(int(self.request_values["draw"]))
        output["iTotalRecords"] = str(self.r_len)
        output["iTotalDisplayRecords"] = str(self.r_len)
        output["data"] = self.result_data
        output["allow_ids"] = self.allow_ids
        output["allow_ids_resend"] = self.allow_ids_resend
        output["allow_ids_edit"] = self.allow_ids_edit
        output["table_name_column_verbose_name"] = self.table_name_column_verbose_name
        return output
