import json

from kore_investment.users.computations import dynamic_model_create
from kore_investment.users.computations.db_centralised_function import (
    data_handling,
    delete_data_func,
    read_data_func,
)


def create_replica_table(
    request, table_name_replica, db_connection_name="", engine2=[], db_type=None, engine_override=False
):
    modelName = dynamic_model_create.get_model_class(
        table_name_replica, request, db_connection_name=db_connection_name
    )
    model_status = "Success"
    audit_fields = [
        "created_by",
        "modified_by",
        "created_date",
        "modified_date",
        "active_to",
        "active_from",
        "approved_by",
        "approval_status",
        "transaction_id",
        "is_active_flag",
        modelName.pk.name,
    ]
    multisel_field_list = [
        field.name for field in modelName.concrete_fields if field.get_internal_type() in ["MultiselectField"]
    ]
    field_df = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": ["fields"],
            },
            "condition": [
                {
                    "column_name": "model_type",
                    "condition": "Equal to",
                    "input_value": "user defined",
                    "and_or": "and",
                },
                {
                    "column_name": "tablename",
                    "condition": "Equal to",
                    "input_value": table_name_replica,
                    "and_or": "",
                },
            ],
        },
        engine2=engine2,
        db_type=db_type,
        engine_override=engine_override,
    )
    if not field_df.empty:
        field_dict = field_df.to_dict("records")
        field_dict = json.loads(field_dict[0]["fields"])

        table_dict = []
        table_dict.append(
            {
                "field name": "id",
                "field data type": "AutoField (Primary key)",
                "field header": "id",
                "nullable?": "No",
                "computed value": "Select",
                "unique": "Yes",
            }
        )
        table_dict.append(
            {
                "field name": "mulselect_id",
                "field data type": "CharField (Text,numbers,special characters,etc.)",
                "field header": "MultiSelect id",
                "nullable?": "Yes",
                "maximum length*": "255",
                "unique": "select",
            }
        )

        f_dict = {
            "internal_type": "field data type",
            "verbose_name": "field header",
            "null": "nullable?",
            "unique": "unique",
            "max_length": "maximum length*",
            "auto_now": "auto now?",
            "editable": "editable?",
            "divider": "divider",
            "choices": "choices",
            "columns": "columns",
            "default": "default",
        }
        valDict_dtype = {
            "AutoField": "AutoField (Primary key)",
            "CharField": "CharField (Text,numbers,special characters,etc.)",
            "ConcatenationField": "ConcatenationField",
            "TextField": "TextField (Large text)",
            "BooleanField": "BooleanField (Yes or No,True or False,etc.",
            "FileField": "FileField (File/Document upload)",
            "VideoField": "VideoField",
            "ImageField": "ImageField (image upload)",
            "IntegerField": "IntegerField (Integer numbers)",
            "BigIntegerField": "BigIntegerField (Big Integer numbers)",
            "FloatField": "FloatField (Integer or decimal numbers)",
            "DateField": "DateField (Date)",
            "DateTimeField": "DateTimeField (Date and Time)",
            "TimeField": "TimeField (Time)",
            "TimeRangeField": "TimeRangeField",
            "DateTimeRangeField": "DateTimeRangeField",
            "DateRangeField": "DateRangeField",
            "UniqueIDField": "UniqueIDField",
            "URLField": "URLField (URL Link)",
            "ForeignKey": "ForeignKey",
            "CardField": "CardField (Credit card/Debit card)",
            "CardCvvField": "CardCvvField",
            "CardExpiryField": "CardExpiryField",
            "CardTypeField": "CardTypeField (Identifies the type of card)",
            "EmailTypeField": "EmailTypeField",
            "MultiselectField": "MultiselectField",
            "UserField": "UserField",
            "TableField": "TableField",
            "PrivacyField": "PrivacyField",
            "RTFField": "RTFField",
            "HierarchyField": "HierarchyField",
        }
        for key, value in field_dict.items():
            if key not in audit_fields:
                temp = {}
                temp["field name"] = key
                for k, v in value.items():
                    if k == "internal_type":
                        if key in multisel_field_list:
                            temp[f_dict[k]] = valDict_dtype["CharField"]
                            temp[f_dict["max_length"]] = "1026"
                        else:
                            temp[f_dict[k]] = valDict_dtype[v]
                    elif k in ["verbose_name", "max_length", "columns", "default"]:
                        temp[f_dict[k]] = str(v)
                    elif k == "divider":
                        temp[f_dict[k]] = v
                    elif k in ["null", "editable", "auto_now"]:
                        if v in [0, "0", False]:
                            v = "No"
                        elif v in [1, "1", True]:
                            v = "Yes"
                        temp[f_dict[k]] = v
                    elif k == "choices":
                        temp[f_dict[k]] = [i[0] for i in v]
                    elif k == "unique":
                        temp[f_dict[k]] = "No"
                    elif k == "parent":
                        temp["parent table"] = v
                    else:
                        temp[k] = v
                table_dict.append(temp)

    model_status = dynamic_model_create.create_table_sql(
        table_name_replica + "_mul", table_dict, request, db_connection_name=db_connection_name
    )
    return model_status


def insert_delimited_data(
    elementID,
    request,
    table_name_replica,
    multi_select_tables,
    mutli_select_cols,
    mutli_select_attr,
    existingData,
    delete="no",
):
    if isinstance(request, dict):

        class AttrDict:
            def __init__(self, i_dict):
                for key, value in i_dict.items():
                    if key not in ["password", "last_login", "date_joined"]:
                        setattr(self, key, value)
                if i_dict.get("username"):
                    setattr(self, "is_anonymous", False)
                else:
                    setattr(self, "is_anonymous", True)

            def get_host(self):
                return self.host

        request["user"] = AttrDict(request["user"])
        request = AttrDict(request)

    modelName = dynamic_model_create.get_model_class(table_name_replica, request)

    def value_converter(value):
        if value and type(value) == str:
            if value.startswith("{") and value.endswith("}"):
                value = [int(i) for i in json.loads(value).keys()]
            else:
                value = None
        else:
            value = None
        return value

    for m_col in mutli_select_attr:
        if m_col in existingData.columns:
            existingData[m_col] = existingData[m_col].apply(value_converter)
            existingData = existingData.explode(m_col)
        else:
            existingData[m_col] = None

    for m_idx, m_table in enumerate(multi_select_tables):
        m_entered_values = existingData[mutli_select_attr[m_idx]].dropna().unique().tolist()
        if m_entered_values:
            m_entered_values = str(tuple(m_entered_values)).replace(",)", ")")
            value_mapping = (
                read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": m_table,
                            "Columns": ["id", mutli_select_cols[m_idx]],
                        },
                        "condition": [
                            {
                                "column_name": "id",
                                "condition": "IN",
                                "input_value": m_entered_values,
                                "and_or": "",
                            }
                        ],
                    },
                )
                .set_index("id")[mutli_select_cols[m_idx]]
                .to_dict()
            )
            existingData[mutli_select_attr[m_idx]] = existingData[mutli_select_attr[m_idx]].replace(
                value_mapping
            )
        else:
            pass
    existingData.rename(columns={modelName.pk.name: "mulselect_id"}, inplace=True)

    if delete == "yes":
        ids = existingData["mulselect_id"].to_list()
        ids_to_be_deleted = str(tuple(ids)).replace(",)", ")")
        delete_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": table_name_replica + "_mul",
                },
                "condition": [
                    {
                        "column_name": "mulselect_id",
                        "condition": "IN",
                        "input_value": ids_to_be_deleted,
                        "and_or": "",
                    }
                ],
            },
        )
    if len(existingData) > 0:
        data_handling(request, existingData, table_name_replica + "_mul")
    return None


def check_replica_data(request, table_name_replica):
    existingData = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": table_name_replica + "_mul",
                "Agg_Type": "Count(id)",
                "Columns": [],
            },
            "condition": [],
        },
    )
    return existingData
