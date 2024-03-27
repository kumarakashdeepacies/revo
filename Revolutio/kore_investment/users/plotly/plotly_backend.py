from ast import literal_eval
import base64

# Download csv format
import csv
from datetime import date, datetime
from io import BytesIO
import json
import logging
import os

from PIL import Image
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django_multitenant.utils import get_current_tenant
import pandas as pd
import plotly.express as px

from config.settings.base import MEDIA_ROOT

## Cache
from kore_investment.users import rules1
from kore_investment.users.computations import dynamic_model_create, standardised_functions
from kore_investment.users.computations.db_centralised_function import (
    app_engine_generator,
    data_handling,
    engine_geneartor,
    read_data_func,
)

from . import Table_Agg


def plotlyTrials(request, app_code=None, mode=None):

    if request.method == "POST":
        if request.POST["operation"] == "PlotCategory":
            plotCategory = request.POST["selectedValue"]
            if plotCategory == "Pivot Report":
                chartType = [
                    "Pivot Table",
                    "Table Barchart",
                    "Heatmap",
                    "Row Heatmap",
                    "Col Heatmap",
                    "Line Chart",
                    "Bar Chart",
                    "Stacked Bar Chart",
                    "Area Chart",
                    "Scatter Chart",
                ]
            if plotCategory == "Image":
                chartType = ["Image"]
            if plotCategory == "Scatter":
                chartType = ["Scatter", "Scatter with Straight Lines and Markers", "Horizontal Dot Plot"]
            if plotCategory == "Bar":
                chartType = [
                    "Vertical Bar",
                    "Vertical Bar Stacked",
                    "Vertical Bar Grouped",
                    "Horizontal Bar",
                    "Horizontal Bar Stacked",
                    "Horizontal Bar Grouped",
                ]
            if plotCategory == "Line":
                chartType = ["Line", "Vertical Line Stacked", "Stepped Line", "Multiple Line Chart"]
            if plotCategory == "Pie":
                chartType = ["Pie Chart", "Donut Chart"]
            if plotCategory == "Sunburst":
                chartType = ["Sunburst"]
            if plotCategory == "Area":
                chartType = [
                    "Vertical Area",
                    "Vertical Area Stacked",
                    "Horizontal Area",
                    "Horizontal Area Stacked",
                ]
            if plotCategory == "Waterfall":
                chartType = [
                    "Vertical Waterfall",
                    "Vertical Waterfall Grouped",
                    "Horizontal Waterfall",
                    "Horizontal Waterfall Grouped",
                ]
            if plotCategory == "Treemap":
                chartType = ["Treemap", "Nested Treemap"]
            if plotCategory == "Funnel":
                chartType = ["Funnel", "Funnel Area", "Funnel Stacked"]
            if plotCategory == "Bubble":
                chartType = ["Bubble Chart"]
            if plotCategory == "Boxplot":
                chartType = [
                    "Vertical Box",
                    "Vertical Grouped Box",
                    "Horizontal Box",
                    "Horizontal Grouped Box",
                ]
            if plotCategory == "Histogram":
                chartType = [
                    "Vertical Histogram",
                    "Cumulative Histogram",
                    "Horizontal Histogram",
                    "2D Histogram Contour",
                    "Stacked Histogram",
                ]
            if plotCategory == "Violin":
                chartType = [
                    "Vertical Violin",
                    "Horizontal Violin",
                    "Vertical Grouped Violin",
                    "Horizontal Grouped Violin",
                ]
            if plotCategory == "Heatmap":
                chartType = ["Heatmap"]
            if plotCategory == "Gauge":
                chartType = ["Angular Gauge", "Bullet Gauge"]
            if plotCategory == "Map":
                chartType = ["Bubble Map", "Chloropeth Map"]
            if plotCategory == "3D plots":
                chartType = ["3D Scatter", "3D Surface", "3D Ribbon", "3D Mesh"]
            if plotCategory == "Aggregation":
                chartType = [
                    "Sum",
                    "Maximum",
                    "Minimum",
                    "Count",
                    "Count Distinct",
                    "Average",
                    "Median",
                    "Variance",
                    "Skewness",
                    "Kurtosis",
                    "Standard Deviation",
                    "Top N",
                    "Bottom N",
                    "First",
                    "Last",
                ]
            if plotCategory == "Combo":
                chartType = ["Bar Grouped and Line", "Bar Stacked and Line", "Bar Stacked and Multiple Line"]
            if plotCategory == "Table":
                chartType = ["Table", "Nested Table"]
            dataReturn = {"chartType": chartType}
            return JsonResponse(dataReturn)


def drilldown_plot(request, app_code=None, mode=None):
    if request.method == "POST":
        if request.POST["operation"] == "drilldown_table":
            filterdata = request.POST.get("filter")
            filtercolumn = request.POST.get("filtercolumn")
            tablename = request.POST["tableName"]
            modelName = dynamic_model_create.get_model_class(tablename, request)
            condition_list = []
            condition_list.append(
                {
                    "column_name": filtercolumn,
                    "condition": "Equal to",
                    "input_value": str(filterdata),
                    "constraintName": "DrillDownDataFetch",
                    "ruleSet": "rule_set",
                    "and_or": "",
                }
            )
            if modelName.get_field(filtercolumn).get_internal_type() == "ForeignKey":
                primary_key = dynamic_model_create.get_model_class(
                    modelName.get_field(filtercolumn).parent, request
                ).pk.name
                input_value = read_data_func(
                    request,
                    config_dict={
                        "inputs": {
                            "Data_source": "Database",
                            "Table": modelName.get_field(filtercolumn).parent,
                            "Columns": [primary_key],
                        },
                        "condition": [
                            {
                                "column_name": filtercolumn,
                                "condition": "Equal to",
                                "input_value": str(filterdata),
                                "and_or": "",
                            },
                        ],
                    },
                )
                if not input_value.empty:
                    input_value = str(input_value.iloc[0, 0])
                else:
                    input_value = "0"
                condition_list[0]["input_value"] = input_value
            else:
                pass

            if request.user.is_superuser:
                hierarchy_dict = {}
                fk_columns = {}
                for field in modelName.concrete_fields:
                    if field.get_internal_type() == "HierarchyField":
                        hierarchy_dict.setdefault(field.hierarchy_group, []).append(field.name)
                    elif field.get_internal_type() == "ForeignKey":
                        actual_model_name_h = dynamic_model_create.get_model_class(
                            field.parent,
                            request,
                        )
                        if actual_model_name_h.get_field(field.name).get_internal_type() == "HierarchyField":
                            hierarchy_dict.setdefault(
                                actual_model_name_h.get_field(field.name).hierarchy_group, []
                            ).append(field.name)
                            fk_columns[field.name] = {
                                "field_class": field,
                                "primary_key": actual_model_name_h.pk.name,
                            }
                        else:
                            continue
                    else:
                        continue
                if hierarchy_dict:
                    perm_dict = rules1.data_hierarchy_access_list(request, hierarchy_dict)
                    for h_idx, h_group in enumerate(hierarchy_dict):
                        if perm_dict.get(h_group):
                            perm_list = tuple(perm_dict[h_group])
                            h_cols = hierarchy_dict[h_group]
                            perm_string = ", ".join("'" + i + "'" for i in perm_list)
                            if not perm_string.startswith("("):
                                perm_string = "(" + perm_string
                            if not perm_string.endswith(")"):
                                perm_string = perm_string + ")"

                            if h_idx != len(hierarchy_dict) - 1:
                                for c_idx, col in enumerate(h_cols):
                                    if col in fk_columns:
                                        fk_field = fk_columns[col]["field_class"]
                                        fk_data = read_data_func(
                                            request,
                                            config_dict={
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": fk_field.parent,
                                                    "Columns": [fk_columns[col]["primary_key"]],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": fk_field.name,
                                                        "condition": "IN",
                                                        "input_value": perm_string,
                                                        "and_or": "",
                                                    },
                                                ],
                                            },
                                        )[fk_columns[col]["primary_key"]].to_list()
                                        perm_string = ", ".join(f"'{i}'" for i in fk_data)
                                        if not perm_string.startswith("("):
                                            perm_string = "(" + perm_string
                                        if not perm_string.endswith(")"):
                                            perm_string = perm_string + ")"
                                        fk_data = None
                                        del fk_data
                                    else:
                                        pass
                                    if c_idx == 0:
                                        h_cond = {
                                            "column_name": f"{col}",
                                            "condition": "IN",
                                            "input_value": perm_string,
                                            "constraintName": "DrillDownDataFetch",
                                            "ruleSet": "rule_set",
                                            "and_or": "",
                                        }
                                    condition_list.append(h_cond)
                            else:
                                for c_idx, col in enumerate(h_cols):
                                    if col in fk_columns:
                                        fk_field = fk_columns[col]["field_class"]
                                        fk_data = read_data_func(
                                            request,
                                            config_dict={
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": fk_field.parent,
                                                    "Columns": [fk_columns[col]["primary_key"]],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": fk_field.name,
                                                        "condition": "IN",
                                                        "input_value": perm_string,
                                                        "and_or": "",
                                                    },
                                                ],
                                            },
                                        )[fk_columns[col]["primary_key"]].to_list()
                                        perm_string = ", ".join(f"'{i}'" for i in fk_data)
                                        if not perm_string.startswith("("):
                                            perm_string = "(" + perm_string
                                        if not perm_string.endswith(")"):
                                            perm_string = perm_string + ")"
                                        fk_data = None
                                        del fk_data
                                    else:
                                        pass
                                    if c_idx == 0:
                                        h_cond = {
                                            "column_name": f"{col}",
                                            "condition": "IN",
                                            "input_value": perm_string,
                                            "constraintName": "DrillDownDataFetch",
                                            "ruleSet": "rule_set",
                                            "and_or": "",
                                        }
                                    condition_list.append(h_cond)
                        else:
                            pass
                else:
                    pass
            else:
                pass

            table = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": tablename,
                        "Columns": ["*"],
                    },
                    "condition": condition_list,
                    "adv_condition": [],
                },
            )

            field_to_verbose = {field.name: field.verbose_name for field in modelName.concrete_fields}
            categorical_columns = [
                field.name
                for field in modelName.concrete_fields
                if field.get_internal_type() in ["DateTimeField", "DateField", "TimeField", "CharField"]
            ]
            exclude_list = [filtercolumn, "created_by", "created_date", "modified_by", "modified_date"]
            categorical_columns = [i for i in categorical_columns if i not in exclude_list]
            fk_columns = [i for i in modelName.concrete_fields if i.get_internal_type() == "ForeignKey"]
            for fk_col in fk_columns:
                if fk_col.name in table.columns:
                    __pmn__, table, __tableh__ = standardised_functions.nestedForeignKey(
                        fk_col, request, "", table, fk_col.name
                    )
                else:
                    continue
            table = multiSelectDetail(tablename, table, request, modelName)
            table.fillna("-", inplace=True)
            table.rename(columns=field_to_verbose, inplace=True)
            context = {}
            context["table_values"] = table.values.tolist()
            context["tableheaders"] = list(table.columns)
            context["tablevalues"] = table.to_dict("records")
            context["categorical_columns"] = categorical_columns
            context["mappingDict"] = field_to_verbose
            return JsonResponse(context)

        if request.POST["operation"] == "drilldown_plot":
            filterdata = request.POST.get("filter")
            filtercolumn = request.POST.get("filtercolumn")
            y_axis = request.POST.get("y_axis")
            x_axis = request.POST.get("categorydrilldown")
            tablename = request.POST["tableName"]
            modelName = dynamic_model_create.get_model_class(tablename, request)
            user_db_engine, db_type, schema = app_engine_generator(request)

            condition_list = []
            condition_list.append(
                {
                    "column_name": filtercolumn,
                    "condition": "Equal to",
                    "input_value": str(filterdata),
                    "constraintName": "DrillDownDataFetch",
                    "ruleSet": "rule_set",
                    "and_or": "",
                }
            )
            if modelName.get_field(filtercolumn).get_internal_type() == "ForeignKey":
                primary_key = dynamic_model_create.get_model_class(
                    modelName.get_field(filtercolumn).parent, request
                ).pk.name
                input_value = read_data_func(
                    request,
                    config_dict={
                        "inputs": {
                            "Data_source": "Database",
                            "Table": modelName.get_field(filtercolumn).parent,
                            "Columns": [primary_key],
                        },
                        "condition": [
                            {
                                "column_name": filtercolumn,
                                "condition": "Equal to",
                                "input_value": str(filterdata),
                                "and_or": "",
                            },
                        ],
                    },
                )
                if not input_value.empty:
                    input_value = str(input_value.iloc[0, 0])
                else:
                    input_value = "0"
                condition_list[0]["input_value"] = input_value
            else:
                pass

            if request.user.is_superuser:
                hierarchy_dict = {}
                fk_columns = {}
                for field in modelName.concrete_fields:
                    if field.get_internal_type() == "HierarchyField":
                        hierarchy_dict.setdefault(field.hierarchy_group, []).append(field.name)
                    elif field.get_internal_type() == "ForeignKey":
                        actual_model_name_h = dynamic_model_create.get_model_class(
                            field.parent,
                            request,
                        )
                        if actual_model_name_h.get_field(field.name).get_internal_type() == "HierarchyField":
                            hierarchy_dict.setdefault(
                                actual_model_name_h.get_field(field.name).hierarchy_group, []
                            ).append(field.name)
                            fk_columns[field.name] = {
                                "field_class": field,
                                "primary_key": actual_model_name_h.pk.name,
                            }
                        else:
                            continue
                    else:
                        continue
                if hierarchy_dict:
                    perm_dict = rules1.data_hierarchy_access_list(request, hierarchy_dict)
                    for h_idx, h_group in enumerate(hierarchy_dict):
                        if perm_dict.get(h_group):
                            perm_list = tuple(perm_dict[h_group])
                            h_cols = hierarchy_dict[h_group]
                            perm_string = ", ".join("'" + i + "'" for i in perm_list)
                            if not perm_string.startswith("("):
                                perm_string = "(" + perm_string
                            if not perm_string.endswith(")"):
                                perm_string = perm_string + ")"

                            if h_idx != len(hierarchy_dict) - 1:
                                for c_idx, col in enumerate(h_cols):
                                    if col in fk_columns:
                                        fk_field = fk_columns[col]["field_class"]
                                        fk_data = read_data_func(
                                            request,
                                            config_dict={
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": fk_field.parent,
                                                    "Columns": [fk_columns[col]["primary_key"]],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": fk_field.name,
                                                        "condition": "IN",
                                                        "input_value": perm_string,
                                                        "and_or": "",
                                                    },
                                                ],
                                            },
                                        )[fk_columns[col]["primary_key"]].to_list()
                                        perm_string = ", ".join(f"'{i}'" for i in fk_data)
                                        if not perm_string.startswith("("):
                                            perm_string = "(" + perm_string
                                        if not perm_string.endswith(")"):
                                            perm_string = perm_string + ")"
                                        fk_data = None
                                        del fk_data
                                    else:
                                        pass
                                    if c_idx == 0:
                                        h_cond = {
                                            "column_name": f"{col}",
                                            "condition": "IN",
                                            "input_value": perm_string,
                                            "constraintName": "DrillDownDataFetch",
                                            "ruleSet": "rule_set",
                                            "and_or": "",
                                        }
                                    condition_list.append(h_cond)
                            else:
                                for c_idx, col in enumerate(h_cols):
                                    if col in fk_columns:
                                        fk_field = fk_columns[col]["field_class"]
                                        fk_data = read_data_func(
                                            request,
                                            config_dict={
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": fk_field.parent,
                                                    "Columns": [fk_columns[col]["primary_key"]],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": fk_field.name,
                                                        "condition": "IN",
                                                        "input_value": perm_string,
                                                        "and_or": "",
                                                    },
                                                ],
                                            },
                                        )[fk_columns[col]["primary_key"]].to_list()
                                        perm_string = ", ".join(f"'{i}'" for i in fk_data)
                                        if not perm_string.startswith("("):
                                            perm_string = "(" + perm_string
                                        if not perm_string.endswith(")"):
                                            perm_string = perm_string + ")"
                                        fk_data = None
                                        del fk_data
                                    else:
                                        pass
                                    if c_idx == 0:
                                        h_cond = {
                                            "column_name": f"{col}",
                                            "condition": "IN",
                                            "input_value": perm_string,
                                            "constraintName": "DrillDownDataFetch",
                                            "ruleSet": "rule_set",
                                            "and_or": "",
                                        }
                                    condition_list.append(h_cond)
                        else:
                            pass
                else:
                    pass
            else:
                pass

            operation = request.POST.get("aggregation").lower()
            table = groupby_data_fetch(
                request,
                tablename,
                condition_list,
                [],
                x_axis,
                operation,
                y_axis,
                user_db_engine,
                db_type,
                modelName,
            )

            context = {}
            context["y_axis"] = y_axis
            context["x_axis"] = x_axis
            context["y_axisdata"] = list(table[y_axis])
            context["x_axisdata"] = list(table[x_axis])
            field_to_verbose = {field.name: field.verbose_name for field in modelName.concrete_fields}
            context["mappingDict"] = field_to_verbose
            return JsonResponse(context)


def filter_plot(request, app_code=None, mode=None):
    context = {}
    instance = get_current_tenant()
    tenant = instance.name
    app_code_ = request.POST.get("app_code")
    if app_code_ not in ["", None]:
        user_db_engine, db_type = engine_geneartor(app_code_, request, tenant=tenant)
    else:
        user_db_engine, db_type, schema = app_engine_generator(request, tenant=tenant)
    table = ""
    if len(request.POST["tableName"]) > 0 and (request.POST["tableName"]) != "Select table":
        tablename = request.POST["tableName"]
        "users_" + tablename.lower()
        modelName = dynamic_model_create.get_model_class(
            tablename, request, db_engine=user_db_engine, db_type=db_type
        )
        column_list = [field.name for field in modelName.concrete_fields]
        field_to_verbose = {field.name: field.verbose_name for field in modelName.concrete_fields}

        # Create list of conditions for data fetch:
        condition_list = []
        adv_condition_list = []
        if "slicerColumn" in request.POST:
            slicer_column = json.loads(request.POST["slicerColumn"])
            slicer_column_value = json.loads(request.POST.get("slicerColumnValue"))
            for slc_ind, i in enumerate(slicer_column):
                if i in column_list and slicer_column_value[slc_ind] not in [
                    "",
                    "All",
                    "all",
                    None,
                    [],
                    [""],
                    ["All"],
                    ["all"],
                ]:
                    if type(slicer_column_value[slc_ind]) == list:
                        input_value = slicer_column_value[slc_ind]
                        if modelName.get_field(i).internal_type == "ForeignKey":
                            master_identifier = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": modelName.get_field(i).parent,
                                        "Columns": ["id"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": i,
                                            "condition": "IN",
                                            "input_value": input_value,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                            if master_identifier.id.tolist():
                                input_value = master_identifier.id.tolist()
                            else:
                                input_value = [""]
                        else:
                            pass
                        slicer_condition = {
                            "column_name": i,
                            "condition": "IN",
                            "input_value": input_value,
                            "constraintName": "PlotDataFetchCons",
                            "ruleSet": "rule_set",
                            "and_or": "",
                        }
                    else:
                        input_value = slicer_column_value[slc_ind]
                        if modelName.get_field(i).internal_type == "ForeignKey":
                            master_identifier = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": modelName.get_field(i).parent,
                                        "Columns": ["id"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": i,
                                            "condition": "Equal to",
                                            "input_value": input_value,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                            if master_identifier.id.tolist():
                                input_value = str(master_identifier.id.iloc[0])
                            else:
                                input_value = ""
                        else:
                            pass
                        slicer_condition = {
                            "column_name": i,
                            "condition": "Equal to",
                            "input_value": input_value,
                            "constraintName": "PlotDataFetchCons",
                            "ruleSet": "rule_set",
                            "and_or": "",
                        }
                    condition_list.append(slicer_condition)
                else:
                    continue
        else:
            pass

        # Date range filter conditions
        context = {}
        drange_data = {}
        if "drange" in request.POST:
            drange_data = json.loads(request.POST["drange"])
            if drange_data:
                start_date = drange_data["start_date"]
                end_date = drange_data["end_date"]
                col_name = drange_data["col_name"]
                condition_list.append(
                    {
                        "column_name": col_name,
                        "condition": "Between",
                        "input_value_lower": start_date,
                        "input_value_upper": end_date,
                        "constraintName": "PlotDataFetchCons",
                        "ruleSet": "rule_set",
                        "and_or": "",
                    }
                )
                context["drange"] = drange_data
            else:
                pass
        else:
            pass

        filter_inputs = json.loads(request.POST.get("filter_input_final"))
        for filter in filter_inputs:
            filter_value = filter["filter_value"]
            if filter_value:
                if filter["data_category"] == "Categorical":
                    if "Latest" in filter_value:
                        adv_condition_list.append(
                            {
                                "column_name": filter["column_name"],
                                "agg_condition": "MAX",
                                "condition": "",
                                "input_value": "",
                                "constraintName": "PlotDataFetchCons",
                                "ruleSet": "rule_set",
                                "and_or": "",
                            }
                        )
                        if len(filter_value) > 1:
                            filter_value.remove("Latest")
                            condition_list.append(
                                {
                                    "column_name": filter["column_name"],
                                    "condition": "IN",
                                    "input_value": filter_value,
                                    "constraintName": "PlotDataFetchCons",
                                    "ruleSet": "rule_set",
                                    "and_or": "",
                                }
                            )
                        else:
                            pass
                    else:
                        condition_list.append(
                            {
                                "column_name": filter["column_name"],
                                "condition": "IN",
                                "input_value": filter_value,
                                "constraintName": "PlotDataFetchCons",
                                "ruleSet": "rule_set",
                                "and_or": "",
                            }
                        )
                elif filter["data_category"] == "Numerical" and filter["condition_name"] != "Top N":
                    condition_list.append(
                        {
                            "column_name": filter["column_name"],
                            "condition": filter["condition_name"],
                            "input_value": filter_value,
                            "constraintName": "PlotDataFetchCons",
                            "ruleSet": "rule_set",
                            "and_or": "",
                        }
                    )
                else:
                    continue
            else:
                continue

        # Data Hierarchy conditions
        if request.user.is_superuser:
            hierarchy_dict = {}
            fk_columns = {}
            for field in modelName.concrete_fields:
                if field.get_internal_type() == "HierarchyField":
                    hierarchy_dict.setdefault(field.hierarchy_group, []).append(field.name)
                elif field.get_internal_type() == "ForeignKey":
                    actual_model_name_h = dynamic_model_create.get_model_class(
                        field.parent,
                        request,
                        db_connection_name="",
                        db_engine=user_db_engine,
                        db_type=db_type,
                    )
                    if actual_model_name_h.get_field(field.name).get_internal_type() == "HierarchyField":
                        hierarchy_dict.setdefault(
                            actual_model_name_h.get_field(field.name).hierarchy_group, []
                        ).append(field.name)
                        fk_columns[field.name] = {
                            "field_class": field,
                            "primary_key": actual_model_name_h.pk.name,
                        }
                    else:
                        continue
                else:
                    continue
            if hierarchy_dict:
                perm_dict = rules1.data_hierarchy_access_list(request, hierarchy_dict)
                for h_idx, h_group in enumerate(hierarchy_dict):
                    if perm_dict.get(h_group):
                        perm_list = tuple(perm_dict[h_group])
                        h_cols = hierarchy_dict[h_group]
                        perm_string = ", ".join("'" + i + "'" for i in perm_list)
                        if not perm_string.startswith("("):
                            perm_string = "(" + perm_string
                        if not perm_string.endswith(")"):
                            perm_string = perm_string + ")"

                        if h_idx != len(hierarchy_dict) - 1:
                            for c_idx, col in enumerate(h_cols):
                                if col in fk_columns:
                                    fk_field = fk_columns[col]["field_class"]
                                    fk_data = read_data_func(
                                        request,
                                        config_dict={
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": fk_field.parent,
                                                "Columns": [fk_columns[col]["primary_key"]],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": fk_field.name,
                                                    "condition": "IN",
                                                    "input_value": perm_string,
                                                    "and_or": "",
                                                },
                                            ],
                                        },
                                    )[fk_columns[col]["primary_key"]].to_list()
                                    perm_string = ", ".join(f"'{i}'" for i in fk_data)
                                    if not perm_string.startswith("("):
                                        perm_string = "(" + perm_string
                                    if not perm_string.endswith(")"):
                                        perm_string = perm_string + ")"
                                    fk_data = None
                                    del fk_data
                                else:
                                    pass
                                if c_idx == 0:
                                    h_cond = {
                                        "column_name": f"{col}",
                                        "condition": "IN",
                                        "input_value": perm_string,
                                        "constraintName": "PlotDataFetchCons",
                                        "ruleSet": "rule_set",
                                        "and_or": "",
                                    }
                                condition_list.append(h_cond)
                        else:
                            for c_idx, col in enumerate(h_cols):
                                if col in fk_columns:
                                    fk_field = fk_columns[col]["field_class"]
                                    fk_data = read_data_func(
                                        request,
                                        config_dict={
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": fk_field.parent,
                                                "Columns": [fk_columns[col]["primary_key"]],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": fk_field.name,
                                                    "condition": "IN",
                                                    "input_value": perm_string,
                                                    "and_or": "",
                                                },
                                            ],
                                        },
                                    )[fk_columns[col]["primary_key"]].to_list()
                                    perm_string = ", ".join(f"'{i}'" for i in fk_data)
                                    if not perm_string.startswith("("):
                                        perm_string = "(" + perm_string
                                    if not perm_string.endswith(")"):
                                        perm_string = perm_string + ")"
                                    fk_data = None
                                    del fk_data
                                else:
                                    pass
                                if c_idx == 0:
                                    h_cond = {
                                        "column_name": f"{col}",
                                        "condition": "IN",
                                        "input_value": perm_string,
                                        "constraintName": "PlotDataFetchCons",
                                        "ruleSet": "rule_set",
                                        "and_or": "",
                                    }
                                condition_list.append(h_cond)
                    else:
                        pass
            else:
                pass
        else:
            pass

    graph_subtype = request.POST.get("graph_subtype")
    context["graph_subtype"] = graph_subtype
    x_axis = request.POST.get("x_axis")
    y_axis = request.POST.get("y_axis")
    chart_id = request.POST["chart_id"]
    context["drange"] = drange_data

    if graph_subtype == "Nested_Table":
        operation = request.POST.get("aggregation")
        if operation == "None" or operation == "undefined" or operation is None:
            operation = ["sum"]
        else:
            operation = request.POST.get("aggregation")
        if x_axis[0] == "[" and x_axis[-1] == "]":
            x_axis = json.loads(request.POST.get("x_axis"))
        else:
            x_axis = x_axis.split(",")
        if y_axis[0] == "[" and y_axis[-1] == "]":
            y_axis = json.loads(request.POST.get("y_axis"))
        else:
            y_axis = y_axis.split(",")

        x_axisdata = ""
        y_axisdata = ""
        x_axis_new = []
        y_axis_new = []
        for i in x_axis:
            x_axis_new.append(field_to_verbose[i])
        for i in y_axis:
            y_axis_new.append(field_to_verbose[i])

        fetch_columns_list = x_axis.copy()
        fetch_columns_list += y_axis
        filter_inputs = json.loads(request.POST.get("filter_input_final"))
        inputs1 = {
            "Data_source": "Database",
            "Table": tablename,
            "Columns": fetch_columns_list,
        }
        for filter in filter_inputs:
            if filter["filter_value"]:
                if filter["data_category"] == "Numerical":
                    if filter["condition_name"] == "Top N":
                        filter_value = filter["filter_value"]
                        column_name = filter["column_name"]
                        inputs1 = {
                            "Data_source": "Database",
                            "Table": tablename,
                            "Columns": fetch_columns_list,
                            "Order_Type": f"ORDER BY {column_name} desc",
                            "Agg_Type": f"TOP({filter_value})",
                        }
                    else:
                        continue
                else:
                    continue
            else:
                continue
        table = read_data_func(
            request,
            {
                "inputs": inputs1,
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        table.rename(columns=field_to_verbose, inplace=True)
        logging.warning(f">>>>>>>>>>>>>>>>operation{operation,type(operation)}")
        table_data = Table_Agg.PivotData(table, x_axis_new, y_axis_new, operation, modelName)
        context["headers"] = fetch_columns_list
        context["table_data"] = table_data
        context["table_view"] = table.fillna("-").to_dict("records")
        context["final_cols"] = ["Category"] + y_axis_new
        if request.POST.get("conditional_table") is not None:
            context["conditional_table"] = json.loads(request.POST.get("conditional_table"))
        else:
            context["conditional_table"] = ""

    elif graph_subtype == "Table":
        operation = request.POST.get("aggregation").lower()
        x_axisdata = ""
        y_axisdata = ""
        if x_axis != "":
            if x_axis[0] == "[" and x_axis[-1] == "]":
                x_axis = json.loads(request.POST.get("x_axis"))
            else:
                x_axis = x_axis.split(",")
        else:
            x_axis = []
        if y_axis != "":
            if y_axis[0] == "[" and y_axis[-1] == "]":
                y_axis = json.loads(request.POST.get("y_axis"))
            else:
                y_axis = y_axis.split(",")
        else:
            y_axis = []
        filter_inputs = json.loads(request.POST.get("filter_input_final"))
        inputs1 = {
            "Data_source": "Database",
            "Table": tablename,
            "Columns": x_axis,
        }
        for filter in filter_inputs:
            if filter["filter_value"]:
                if filter["data_category"] == "Numerical":
                    if filter["condition_name"] == "Top N":
                        filter_value = filter["filter_value"]
                        column_name = filter["column_name"]
                        inputs1 = {
                            "Data_source": "Database",
                            "Table": tablename,
                            "Columns": x_axis,
                            "Order_Type": f"ORDER BY {column_name} desc",
                            "Agg_Type": f"TOP({filter_value})",
                        }
                    else:
                        continue
                else:
                    continue
            else:
                continue
        table = read_data_func(
            request,
            {
                "inputs": inputs1,
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        for field in modelName.concrete_fields:
            if field in table.columns:
                if table[field].dtype == "datetime64[ns]":
                    if field.get_internal_type() == "DateTimeField":
                        column_name = field.name
                        table[column_name] = table[column_name].dt.strftime("%Y-%m-%d %H:%M:%S")
                    elif field.get_internal_type() == "DateField":
                        column_name = field.name
                        table[column_name] = table[column_name].dt.strftime("%Y-%m-%d")
                    else:
                        continue
                else:
                    continue
            else:
                continue

        table.fillna("None", inplace=True)
        table = multiSelectDetail(
            tablename, table, request, modelName, db_engine=user_db_engine, db_type=db_type
        )
        table.rename(columns=field_to_verbose, inplace=True)
        context["content"] = table.to_dict("records")
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["chartDivId"] = graph_subtype + "".join(x_axis)
        context["operation"] = request.POST.get("aggregation").lower()
        if request.POST.get("conditional_table") is not None:
            context["conditional_table"] = json.loads(request.POST.get("conditional_table"))
        else:
            context["conditional_table"] = ""

    elif graph_subtype == "Multiple_Line_Chart":
        operation = request.POST.get("aggregation").lower()

        if request.POST["y_axis"][0] == "[" and request.POST["y_axis"][-1] == "]":
            original_y_axis = json.loads(request.POST.get("y_axis"))
        else:
            original_y_axis = list(request.POST["y_axis"].split(","))
        new_y_axis = original_y_axis.copy()
        if x_axis in new_y_axis:
            new_y_axis.remove(x_axis)
            original_y_axis.remove(x_axis)
        y_axis = new_y_axis[0]
        y_axis_new = new_y_axis
        all_axis = new_y_axis
        agg_operation = {}
        for i in y_axis_new:
            agg_operation[i] = operation

        if x_axis not in all_axis:
            all_axis.append(x_axis)

        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            original_y_axis,
            user_db_engine,
            db_type,
            modelName,
        )

        x_axisdata = table[x_axis].tolist()
        y_axisdata = []
        for y in new_y_axis:
            if len(table) > 0:
                y_axisdata.append(table[y].tolist())
            else:
                y_axisdata.append([])
        context["x_axis"] = x_axis
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["chartDivId"] = y_axis + x_axis + graph_subtype
        if x_axis in new_y_axis:
            new_y_axis.remove(x_axis)

        context["new_y_axis"] = new_y_axis
        context["y_axis"] = new_y_axis

    elif graph_subtype == "Vertical_Bar":
        operation = request.POST.get("aggregation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            y_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])

    elif graph_subtype == "Bubble_Chart":
        second_column = request.POST.get("second_column").split("|")[0]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [x_axis, y_axis, second_column],
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        x_axisdata = list(table[x_axis].fillna(0))
        y_axisdata = list(table[y_axis].fillna(0))
        y_axisdata2 = list(table[second_column].fillna(0))
        context["second_columndata"] = y_axisdata2
        context["second_column"] = second_column

    elif graph_subtype == "Angular_Gauge" or graph_subtype == "Bullet_Gauge":
        second_column = request.POST.get("second_column").split("|")[0]
        x_axis = request.POST.get("x_axis").split("|")[0]
        operation = request.POST.get("aggregation").lower()
        value = aggregation_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            operation,
            second_column,
            user_db_engine,
            db_type,
            aggregation_config={},
        )
        if operation not in ["Top N", "Bottom N"]:
            context["title"] = f"{operation} {field_to_verbose[second_column]} - {field_to_verbose[y_axis]}"
        else:
            context["title"] = (
                f"{request.POST.get('operation_n')} of {operation.rstrip(' N')} {request.POST.get('computed_number')} {field_to_verbose[second_column]}"
            )
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [second_column],
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        y_axisdata2 = list(table[second_column])
        context["second_columndata"] = y_axisdata2
        context["second_column"] = second_column
        context["operation"] = operation
        context["value"] = value
        context["chartDivId"] = y_axis + x_axis + second_column + graph_subtype + operation

    if graph_subtype == "Donut_Chart":
        operation = request.POST.get("aggregation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            y_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = table[y_axis].tolist()

    elif graph_subtype == "Line" or graph_subtype == "Vertical_Area":
        operation = request.POST.get("aggregation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            y_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        x_axisdata = list(table[x_axis])
        if len(table) > 0:
            y_axisdata = list(table[y_axis])
        else:
            y_axisdata = list(table[y_axis])

    if (
        graph_subtype == "Vertical_Histogram"
        or graph_subtype == "Horizontal_Histogram"
        or graph_subtype == "Cumulative_Histogram"
    ):
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [x_axis],
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        x_axisdata = table[x_axis].tolist()
        y_axis = "none"
        y_axisdata = "none"

    elif graph_subtype == "Stacked_Histogram":
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [x_axis, y_axis],
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        x_axisdata = table[x_axis].tolist()
        y_axisdata = table[y_axis].tolist()

    elif graph_subtype in [
        "Pivot_Table",
        "Table_Barchart",
        "Heatmap",
        "Row_Heatmap",
        "Col_Heatmap",
        "Line_Chart",
        "Bar_Chart",
        "Stacked_Bar_Chart",
        "Area_Chart",
        "Scatter_Chart",
    ]:
        if x_axis != "":
            if x_axis[0] == "[" and x_axis[-1] == "]":
                x_axis = json.loads(request.POST.get("x_axis"))
            else:
                x_axis = x_axis.split(",")
        else:
            x_axis = []

        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": x_axis,
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        table.fillna("None", inplace=True)
        table = multiSelectDetail(
            tablename, table, request, modelName, db_engine=user_db_engine, db_type=db_type
        )
        table.rename(columns=field_to_verbose, inplace=True)
        context["content"] = table.to_dict("records")
        context["x_axis"] = x_axis
        context["chartDivId"] = graph_subtype + "".join(x_axis)
        context["operation"] = request.POST.get("aggregation")

    elif graph_subtype == "Stepped_Line":
        operation = request.POST.get("aggregation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            y_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])

    elif graph_subtype == "Aggregation":
        x_axis = request.POST.get("x_axis").split("|")[0]
        operation = request.POST.get("aggregation").split("|")[0]
        aggregation_config = {
            "agg_distinct": request.POST.get("agg_distinct"),
            "operation_n": request.POST.get("operation_n"),
            "computed_number": request.POST.get("computed_number"),
        }
        value = aggregation_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            operation,
            x_axis,
            user_db_engine,
            db_type,
            aggregation_config=aggregation_config,
        )
        if operation not in ["Top N", "Bottom N"]:
            context["title"] = f"{operation} of {field_to_verbose[x_axis]}"
        else:
            context["title"] = (
                f"{request.POST.get('operation_n')} of {operation.rstrip(' N')} {request.POST.get('computed_number')} {field_to_verbose[x_axis]}"
            )
        context["x_axis"] = x_axis
        context["y_axis"] = x_axis
        context["second_column"] = x_axis
        context["operation"] = operation
        context["value"] = value
        context["chartDivId"] = x_axis + graph_subtype + operation

    elif graph_subtype == "Pie_Chart" or graph_subtype == "Treemap":
        operation = request.POST.get("aggregation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            y_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = table[y_axis].tolist()

    elif graph_subtype in ["Vertical_Waterfall"]:
        operation = request.POST.get("aggregation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            y_axis,
            user_db_engine,
            db_type,
            modelName,
        )

        x_axisdata = list(table[x_axis])
        if table[y_axis].dtype == "float":
            y_axisdata = list(table[y_axis])
        else:
            y_axisdata = table[y_axis].tolist()

    elif graph_subtype in ["Horizontal_Bar", "Horizontal_Waterfall", "Funnel", "Horizontal_Area"]:
        operation = request.POST.get("aggregation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            y_axis,
            operation,
            x_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])

    elif graph_subtype == "Funnel_Area":
        operation = request.POST.get("aggregation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            y_axis,
            operation,
            x_axis,
            user_db_engine,
            db_type,
            modelName,
        )

        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])
        colors = px.colors.sequential.turbid
        colordata2 = []
        for i in colors:
            color = literal_eval(i.split("b")[1])
            color = "#%02x%02x%02x" % color
            colordata2.append(color)
        context["colordata"] = colordata2

    elif graph_subtype == "Scatter" or graph_subtype == "2D_Histogram_Contour":
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [x_axis, y_axis],
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])

    elif graph_subtype == "Vertical_Box" or graph_subtype == "Vertical_Violin":
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [x_axis, y_axis],
                    "Order_Type": f"ORDER BY {x_axis}",
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])

    elif graph_subtype == "Horizontal_Box" or graph_subtype == "Horizontal_Violin":
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [x_axis, y_axis],
                    "Order_Type": f"ORDER BY {y_axis}",
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])

    elif graph_subtype == "Horizontal_Dot_Plot":
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [x_axis, y_axis],
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])

    elif graph_subtype == "Scatter_with_Straight_Lines_and_Markers":
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [x_axis, y_axis],
                    "Order_Type": f"ORDER BY {x_axis}",
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        x_axisdata = list(table[x_axis].round(2))
        y_axisdata = list(table[y_axis].round(2))

    elif graph_subtype == "Vertical_Grouped_Box" or graph_subtype == "Vertical_Grouped_Violin":
        second_column = request.POST.get("second_column").split("|")[0]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [x_axis, y_axis, second_column],
                    "Order_Type": f"ORDER BY {x_axis}",
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])
        y_axisdata2 = list(table[second_column])
        context["second_column"] = second_column
        context["second_columndata"] = y_axisdata2

    elif graph_subtype == "Horizontal_Grouped_Box" or graph_subtype == "Horizontal_Grouped_Violin":
        second_column = request.POST.get("second_column").split("|")[0]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [x_axis, y_axis, second_column],
                    "Order_Type": "ORDER BY {y_axis}",
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])
        x_axisdata2 = list(table[second_column])
        context["second_column"] = second_column
        context["second_columndata"] = x_axisdata2

    elif graph_subtype == "Vertical_Waterfall_Grouped":
        second_column = request.POST.get("second_column").split("|")[0]
        operation = request.POST.get("aggregation").lower()
        agg_cols = [y_axis, second_column]
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            agg_cols,
            user_db_engine,
            db_type,
            modelName,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])
        y_axisdata2 = list(table[second_column])
        context["second_column"] = second_column
        context["second_columndata"] = y_axisdata2

    elif graph_subtype == "Vertical_Bar_Stacked" or graph_subtype == "Vertical_Bar_Grouped":
        second_column = request.POST.get("second_column").split("|")[0]
        operation = request.POST.get("aggregation").lower()
        if request.POST["y_axis"][0] == "[" and request.POST["y_axis"][-1] == "]":
            new_y_axis = json.loads(request.POST.get("y_axis"))
            total_y = request.POST.get("total_y")
        else:
            if second_column and second_column != "None":
                new_y_axis = []
                new_y_axis.append(y_axis)
                new_y_axis.append(second_column)
                total_y = 2
            else:
                new_y_axis = list(request.POST["y_axis"].split(","))
                total_y = request.POST.get("total_y")
        if x_axis in new_y_axis:
            new_y_axis.remove(x_axis)
        y_axis = new_y_axis[0]
        y_axis_new = new_y_axis
        all_axis = new_y_axis

        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            new_y_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        y_axisdata = []
        if x_axis in new_y_axis:
            new_y_axis.remove(x_axis)
        for y in new_y_axis:
            if len(table) > 0:
                y_axisdata.append(list(table[y]))
            else:
                y_axisdata.append([])

        x_axisdata = list(table[x_axis])

        # Change the bar mode
        context["x_axis"] = x_axis
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["chartDivId"] = y_axis + x_axis + graph_subtype
        context["new_y_axis"] = new_y_axis
        context["y_axis"] = new_y_axis
        context["total_y"] = total_y

    elif graph_subtype == "Bar_Grouped_and_Line" or graph_subtype == "Bar_Stacked_and_Line":
        second_column = request.POST.get("second_column").split("|")[0]
        line_column = request.POST.get("line_column")
        operation = request.POST.get("aggregation").lower()
        if request.POST["y_axis"][0] == "[" and request.POST["y_axis"][-1] == "]":
            new_y_axis = json.loads(request.POST.get("y_axis"))
            total_y = request.POST.get("total_y")
        else:
            if second_column and second_column != "None":
                new_y_axis = []
                new_y_axis.append(y_axis)
                new_y_axis.append(second_column)
                total_y = 2
            else:
                new_y_axis = list(request.POST["y_axis"].split(","))
                total_y = request.POST.get("total_y")
        if x_axis in new_y_axis:
            new_y_axis.remove(x_axis)
        y_axis = new_y_axis[0]
        y_axis_new = new_y_axis
        all_axis = new_y_axis
        if request.POST.get("operation_line"):
            operation_line = request.POST.get("operation_line").lower()
            table_1 = groupby_data_fetch(
                request,
                tablename,
                condition_list,
                adv_condition_list,
                x_axis,
                operation,
                all_axis,
                user_db_engine,
                db_type,
                modelName,
            )
            table_2 = groupby_data_fetch(
                request,
                tablename,
                condition_list,
                adv_condition_list,
                x_axis,
                operation_line,
                line_column,
                user_db_engine,
                db_type,
                modelName,
            )
            table = table_1.merge(table_2, how="outer", on=x_axis, suffixes=(None, "_table2")).fillna(0)
        else:
            all_axis.append(line_column)
            table = groupby_data_fetch(
                request,
                tablename,
                condition_list,
                adv_condition_list,
                x_axis,
                operation,
                all_axis,
                user_db_engine,
                db_type,
                modelName,
            )

        if (line_column + "_table2") in table:
            line_column_merge = line_column + "_table2"
        else:
            line_column_merge = line_column

        x_axisdata = list(table[x_axis])
        line_data = list(table[line_column_merge].round(2))
        y_axisdata = []
        for y in new_y_axis:
            if len(table) > 0:
                y_axisdata.append(list(table[y].round(2)))
            else:
                y_axisdata.append([])

        context["x_axis"] = x_axis
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["chartDivId"] = y_axis + x_axis + graph_subtype
        context["line_column"] = line_column
        context["line_columndata"] = line_data
        context["new_y_axis"] = new_y_axis
        context["y_axis"] = new_y_axis
        context["total_y"] = total_y

    elif graph_subtype == "Bar_Stacked_and_Multiple_Line":
        second_column = request.POST.get("second_column").split("|")[0]
        operation = request.POST.get("aggregation").lower()
        operation_line = request.POST.get("operation_line").lower()
        if request.POST["y_axis"][0] == "[" and request.POST["y_axis"][-1] == "]":
            new_y_axis = json.loads(request.POST.get("y_axis"))
            total_y = request.POST.get("total_y")
        else:
            if second_column and second_column != "None":
                new_y_axis = []
                new_y_axis.append(y_axis)
                new_y_axis.append(second_column)
                total_y = 2
            else:
                new_y_axis = list(request.POST["y_axis"].split(","))
                total_y = request.POST.get("total_y")
        if x_axis in new_y_axis:
            new_y_axis.remove(x_axis)
        y_axis = new_y_axis[0]
        y_axis_new = new_y_axis
        all_axis = new_y_axis
        if request.POST["line_column"][0] == "[" and request.POST["line_column"][-1] == "]":
            new_line_column = json.loads(request.POST.get("line_column"))
        else:
            new_line_column = list(request.POST["line_column"].split(","))
        if x_axis in new_line_column:
            new_line_column.remove(x_axis)
        line_column = new_line_column[0]
        all_axis_line = new_line_column
        table_1 = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            all_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        table_2 = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation_line,
            all_axis_line,
            user_db_engine,
            db_type,
            modelName,
        )
        table = table_1.merge(table_2, how="outer", on=x_axis, suffixes=(None, "_table2")).fillna(0)
        x_axisdata = list(table[x_axis])
        y_axisdata = []
        if x_axis in new_y_axis:
            new_y_axis.remove(x_axis)
        for y in new_y_axis:
            if len(table) > 0:
                y_axisdata.append(list(table[y]))
            else:
                y_axisdata.append(list(table[y]))

        line_data = []
        if x_axis in new_line_column:
            new_line_column.remove(x_axis)

        for line in new_line_column:
            if (line + "_table2") in table:
                line_merge = line + "_table2"
            else:
                line_merge = line
            if len(table) > 0:
                line_data.append(list(table[line_merge]))
            else:
                line_data.append(list(table[line_merge]))

        context["x_axis"] = x_axis
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["line_columndata"] = line_data
        context["chartDivId"] = y_axis + x_axis + graph_subtype
        context["line_column"] = new_line_column
        context["operation_line"] = operation_line
        context["new_y_axis"] = new_y_axis
        context["y_axis"] = new_y_axis
        context["total_y"] = total_y

    elif graph_subtype == "3D_Scatter" or graph_subtype == "3D_Mesh":
        second_column = request.POST.get("second_column").split("|")[0]
        operation = request.POST.get("aggregation").lower()
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [x_axis, y_axis, second_column],
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )

        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])
        y_axisdata2 = list(table[second_column])
        context["second_column"] = second_column
        context["second_columndata"] = y_axisdata2

    elif graph_subtype == "Sunburst":
        second_column = request.POST.get("second_column").split("|")[0]
        operation = request.POST.get("aggregation").lower()
        table2 = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            [x_axis, y_axis],
            operation,
            second_column,
            user_db_engine,
            db_type,
            modelName,
        )
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            [x_axis],
            operation,
            second_column,
            user_db_engine,
            db_type,
            modelName,
        )
        table[x_axis].fillna(" ", inplace=True)
        table2[x_axis].fillna(" ", inplace=True)
        table2[y_axis].fillna(" ", inplace=True)
        if table.empty:
            table2["sunburst_id"] = ""
        else:
            if table2.empty:
                table2["sunburst_id"] = ""
            else:
                table2["sunburst_id"] = table2[x_axis] + "" + "-" + "" + table2[y_axis]
        table = table.rename(columns={x_axis: y_axis})
        if len(table) > 0:
            table["sunburst_id"] = table[y_axis]
        table[x_axis] = ""
        table = table.append(table2)

        colordata2 = []
        colors = px.colors.sequential.turbid
        for i in colors:
            color = literal_eval(i.split("b")[1])
            color = "#%02x%02x%02x" % color
            colordata2.append(color)
        context["colordata"] = colordata2
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])
        y_axisdata2 = list(table[second_column])
        context["second_column"] = second_column
        context["second_columndata"] = y_axisdata2
        context["sunburst_id"] = list(table["sunburst_id"])

    elif graph_subtype == "Horizontal_Bar_Stacked" or graph_subtype == "Horizontal_Bar_Grouped":
        second_column = request.POST.get("second_column").split("|")[0]
        operation = request.POST.get("aggregation").lower()
        if request.POST["x_axis"][0] == "[" and request.POST["x_axis"][-1] == "]":
            new_x_axis = json.loads(request.POST.get("x_axis"))
            total_y = request.POST.get("total_y")
        else:
            if second_column and second_column != "None":
                new_x_axis = []
                new_x_axis.append(x_axis)
                new_x_axis.append(second_column)
                total_y = 2
            else:
                new_x_axis = list(request.POST["x_axis"].split(","))
                total_y = request.POST.get("total_y")
        if y_axis in new_x_axis:
            new_x_axis.remove(y_axis)
        x_axis = new_x_axis[0]
        x_axis_new = new_x_axis
        all_axis = new_x_axis
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            y_axis,
            operation,
            all_axis,
            user_db_engine,
            db_type,
            modelName,
        )

        x_axisdata = []
        if y_axis in new_x_axis:
            new_x_axis.remove(y_axis)
        for x in new_x_axis:
            if len(table) > 0:
                x_axisdata.append(list(table[x]))
            else:
                x_axisdata.append([])

        table = table.reset_index()
        y_axisdata = list(table[y_axis])

        # Change the bar mode
        table = table.to_dict("records")
        context["y_axis"] = y_axis
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["chartDivId"] = y_axis + x_axis + graph_subtype
        if y_axis in new_x_axis:
            new_x_axis.remove(y_axis)
        context["new_x_axis"] = new_x_axis
        context["x_axis"] = new_x_axis
        context["total_y"] = total_y

    elif graph_subtype in ["Horizontal_Area_Stacked", "Horizontal_Waterfall_Grouped", "Funnel_Stacked"]:
        second_column = request.POST.get("second_column").split("|")[0]
        operation = request.POST.get("aggregation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            y_axis,
            operation,
            [x_axis, second_column],
            user_db_engine,
            db_type,
            modelName,
        )
        if table[x_axis].dtype == "float":
            x_axisdata = list(table[x_axis])
        else:
            x_axisdata = list(table[x_axis])
        if table[second_column].dtype == "float":
            x_axisdata2 = list(table[second_column])
        else:
            x_axisdata2 = list(table[second_column])
        if table[y_axis].dtype == "float":
            y_axisdata = list(table[y_axis])
        else:
            y_axisdata = list(table[y_axis])
        table = table.to_dict("records")
        context["second_column"] = second_column
        context["second_columndata"] = x_axisdata2

    elif graph_subtype == "Bubble_Map" or graph_subtype == "Chloropeth_Map":
        second_column = request.POST.get("second_column").split("|")[0]
        operation = request.POST.get("aggregation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            y_axis,
            operation,
            [x_axis, second_column],
            user_db_engine,
            db_type,
            modelName,
        )
        x_axisdata = list(table[x_axis])
        x_axisdata2 = list(table[second_column])
        y_axisdata = list(table[y_axis])
        context["second_column"] = x_axisdata2
        context["second_columndata"] = x_axisdata2
    else:
        pass

    if graph_subtype == "Aggregation":
        context["x_axis"] = x_axis
        context["y_axis"] = x_axis
        context["chart_id_for_slicer"] = chart_id
    elif graph_subtype == "Image":
        context = {}
    elif graph_subtype in [
        "Pivot_Table",
        "Table_Barchart",
        "Heatmap",
        "Row_Heatmap",
        "Col_Heatmap",
        "Line_Chart",
        "Bar_Chart",
        "Stacked_Bar_Chart",
        "Area_Chart",
        "Scatter_Chart",
    ]:
        context["x_axis"] = x_axis
        context["chart_id_for_slicer"] = chart_id
    else:
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["chart_id_for_slicer"] = chart_id
    datatype_list = []
    for i in modelName.concrete_fields:
        type_dict = {"column_name": i.verbose_name, "data_type": i.get_internal_type(), "field_name": i.name}
        datatype_list.append(type_dict)
    context["datatype_list"] = datatype_list
    context["mappingDict"] = field_to_verbose
    return JsonResponse(context)


def render_plot(request, app_code=None):
    filter_column_list = "None"
    priv_field_list = []
    privacy_config = {}
    if (
        request.POST.get("tableName")
        and request.POST.get("tableName") != "12"
        and (request.POST.get("tableName")) != "Select table"
        and request.POST.get("graph_subtype") != "Image"
    ):
        instance = get_current_tenant()
        tenant = instance.name
        app_code_ = request.POST["app_code"]
        db_type = ""
        user_db_engine = ["", None]
        if app_code_ not in ["", None]:
            user_db_engine, db_type = engine_geneartor(app_code_, request, tenant=tenant)
        else:
            user_db_engine, db_type, schema = app_engine_generator(request, tenant=tenant)
        table = ""
        filter_column_list = []
        tablename = request.POST["tableName"]
        modelName = dynamic_model_create.get_model_class(
            tablename, request, db_connection_name="", db_engine=user_db_engine, db_type=db_type
        )
        column_list = [field.name for field in modelName.concrete_fields]

        # Create list of conditions for data fetch:
        condition_list = []
        adv_condition_list = []

        for field in modelName.concrete_fields:
            if field.get_internal_type() == "PrivacyField":
                priv_field_list.append(field.name)
                privacy_config[field.name] = json.loads(field.privacy_config)

        if len(priv_field_list) > 0:
            for priv_field, priv_conf in privacy_config.items():
                if priv_conf["privacy_option"] == "groups":
                    curr_user_group = list(request.user.groups.values_list("name", flat=True))
                    condition_list.append(
                        {
                            "column_name": f"{priv_field}",
                            "condition": "Equal to",
                            "input_value": f"[]",
                            "constraintName": "p2",
                            "ruleSet": "Blank",
                            "and_or": "",
                        }
                    )
                    for ug in curr_user_group:
                        condition_list.append(
                            {
                                "column_name": f"{priv_field}",
                                "condition": "Contains",
                                "input_value": f"""["]{ug}["]""",
                                "constraintName": "p2",
                                "ruleSet": f"{ug}",
                                "and_or": "",
                            }
                        )
                    condition_list.append(
                        {
                            "column_name": f"{priv_field}",
                            "condition": "Equal to",
                            "input_value": f"NULL",
                            "constraintName": "p2",
                            "ruleSet": "NULL",
                            "and_or": "",
                        }
                    )
                    condition_list.append(
                        {
                            "column_name": f"created_by",
                            "condition": "Equal to",
                            "input_value": request.user.username,
                            "constraintName": "p2",
                            "ruleSet": "Creator",
                            "and_or": "",
                        }
                    )
                    condition_list.append(
                        {
                            "column_name": priv_field,
                            "condition": "Contains",
                            "input_value": f"all",
                            "constraintName": "p2",
                            "ruleSet": "Restrict all",
                            "and_or": "",
                        }
                    )
                    condition_list.append(
                        {
                            "column_name": "created_by",
                            "condition": "Equal to",
                            "input_value": request.user.username,
                            "constraintName": "p2",
                            "ruleSet": "Restrict all",
                            "and_or": "",
                        }
                    )
                elif priv_conf["privacy_option"] == "master":
                    curr_grp_from_user = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Agg_Type": "DISTINCT",
                                "Table": priv_conf["master_table"],
                                "Columns": [priv_conf["group_field"]],
                            },
                            "condition": [
                                {
                                    "column_name": priv_conf["user_field"],
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "and_or": "",
                                },
                            ],
                        },
                    )
                    curr_grp_from_user = curr_grp_from_user[priv_conf["group_field"]].tolist()
                    condition_list.append(
                        {
                            "column_name": f"{priv_field}",
                            "condition": "Equal to",
                            "input_value": f"[]",
                            "constraintName": "p2",
                            "ruleSet": "Blank",
                            "and_or": "",
                        }
                    )
                    for ug in curr_grp_from_user:
                        condition_list.append(
                            {
                                "column_name": f"{priv_field}",
                                "condition": "Contains",
                                "input_value": f"""["]{ug}["]""",
                                "constraintName": "p2",
                                "ruleSet": f"{ug}",
                                "and_or": "",
                            }
                        )
                    condition_list.append(
                        {
                            "column_name": f"{priv_field}",
                            "condition": "Equal to",
                            "input_value": f"NULL",
                            "constraintName": "p2",
                            "ruleSet": "NULL",
                            "and_or": "",
                        }
                    )
                    condition_list.append(
                        {
                            "column_name": f"created_by",
                            "condition": "Equal to",
                            "input_value": request.user.username,
                            "constraintName": "p2",
                            "ruleSet": "Creator",
                            "and_or": "",
                        }
                    )
                    condition_list.append(
                        {
                            "column_name": priv_field,
                            "condition": "Contains",
                            "input_value": f"all",
                            "constraintName": "p2",
                            "ruleSet": "Restrict all",
                            "and_or": "",
                        }
                    )
                    condition_list.append(
                        {
                            "column_name": "created_by",
                            "condition": "Equal to",
                            "input_value": request.user.username,
                            "constraintName": "p2",
                            "ruleSet": "Restrict all",
                            "and_or": "",
                        }
                    )
                else:
                    condition_list.append(
                        {
                            "column_name": f"{priv_field}",
                            "condition": "Equal to",
                            "input_value": f"[]",
                            "constraintName": "p2",
                            "ruleSet": "Blank",
                            "and_or": "",
                        }
                    )
                    condition_list.append(
                        {
                            "column_name": f"{priv_field}",
                            "condition": "Contains",
                            "input_value": f"""["]{request.user.username}["]""",
                            "constraintName": "p2",
                            "ruleSet": f"{request.user.username}",
                            "and_or": "",
                        }
                    )
                    condition_list.append(
                        {
                            "column_name": f"{priv_field}",
                            "condition": "Equal to",
                            "input_value": f"NULL",
                            "constraintName": "p2",
                            "ruleSet": "NULL",
                            "and_or": "",
                        }
                    )
                    condition_list.append(
                        {
                            "column_name": f"created_by",
                            "condition": "Equal to",
                            "input_value": request.user.username,
                            "constraintName": "p2",
                            "ruleSet": "Creator",
                            "and_or": "",
                        }
                    )
                    condition_list.append(
                        {
                            "column_name": priv_field,
                            "condition": "Contains",
                            "input_value": f"all",
                            "constraintName": "p2",
                            "ruleSet": "Restrict all",
                            "and_or": "",
                        }
                    )
                    condition_list.append(
                        {
                            "column_name": "created_by",
                            "condition": "Equal to",
                            "input_value": request.user.username,
                            "constraintName": "p2",
                            "ruleSet": "Restrict all",
                            "and_or": "",
                        }
                    )

        # Slicer conditions
        if "slicerColumn" in request.POST:
            slicer_column = json.loads(request.POST["slicerColumn"])
            slicer_column_value = json.loads(request.POST.get("slicerColumnValue"))
            for slc_ind, i in enumerate(slicer_column):
                if i in column_list and slicer_column_value[slc_ind] not in [
                    "",
                    "All",
                    "all",
                    None,
                    [],
                    [""],
                    ["All"],
                    ["all"],
                ]:
                    if type(slicer_column_value[slc_ind]) == list:
                        input_value = slicer_column_value[slc_ind]
                        if modelName.get_field(i).internal_type == "ForeignKey":
                            master_identifier = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": modelName.get_field(i).parent,
                                        "Columns": ["id"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": i,
                                            "condition": "IN",
                                            "input_value": input_value,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                            if master_identifier.id.tolist():
                                input_value = master_identifier.id.tolist()
                            else:
                                input_value = [""]
                        else:
                            pass
                        slicer_condition = {
                            "column_name": i,
                            "condition": "IN",
                            "input_value": input_value,
                            "constraintName": "PlotDataFetchCons",
                            "ruleSet": "rule_set",
                            "and_or": "",
                        }
                    else:
                        input_value = slicer_column_value[slc_ind]
                        if modelName.get_field(i).internal_type == "ForeignKey":
                            master_identifier = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": modelName.get_field(i).parent,
                                        "Columns": ["id"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": i,
                                            "condition": "Equal to",
                                            "input_value": input_value,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                            if master_identifier.id.tolist():
                                input_value = str(master_identifier.id.iloc[0])
                            else:
                                input_value = ""
                        else:
                            pass
                        slicer_condition = {
                            "column_name": i,
                            "condition": "Equal to",
                            "input_value": input_value,
                            "constraintName": "PlotDataFetchCons",
                            "ruleSet": "rule_set",
                            "and_or": "",
                        }
                    condition_list.append(slicer_condition)
                else:
                    continue
        else:
            pass

        # Date range filter conditions
        drange_data = {}
        if "drange" in request.POST:
            drange_data = json.loads(request.POST["drange"])
            if drange_data:
                start_date = drange_data["start_date"]
                end_date = drange_data["end_date"]
                col_name = drange_data["col_name"]
                condition_list.append(
                    {
                        "column_name": col_name,
                        "condition": "Between",
                        "input_value_lower": start_date,
                        "input_value_upper": end_date,
                        "constraintName": "PlotDataFetchCons",
                        "ruleSet": "rule_set",
                        "and_or": "",
                    }
                )
            else:
                pass
        else:
            pass

        # Filter conditions
        filter_inputs = json.loads(request.POST.get("filter_inputs"))
        for filter in filter_inputs:
            filter_value = filter["filter_value"]
            if filter_value:
                if filter["data_category"] == "Categorical":
                    if "Latest" in filter_value:
                        adv_condition_list.append(
                            {
                                "column_name": filter["column_name"],
                                "agg_condition": "MAX",
                                "condition": "",
                                "input_value": "",
                                "constraintName": "PlotDataFetchCons",
                                "ruleSet": "rule_set",
                                "and_or": "",
                            }
                        )
                        if len(filter_value) > 1:
                            filter_value.remove("Latest")
                            condition_list.append(
                                {
                                    "column_name": filter["column_name"],
                                    "condition": "IN",
                                    "input_value": filter_value,
                                    "constraintName": "PlotDataFetchCons",
                                    "ruleSet": "rule_set",
                                    "and_or": "",
                                }
                            )
                        else:
                            pass
                    else:
                        condition_list.append(
                            {
                                "column_name": filter["column_name"],
                                "condition": "IN",
                                "input_value": filter_value,
                                "constraintName": "PlotDataFetchCons",
                                "ruleSet": "rule_set",
                                "and_or": "",
                            }
                        )
                elif filter["data_category"] == "Numerical" and filter["condition_name"] != "Top N":
                    condition_list.append(
                        {
                            "column_name": filter["column_name"],
                            "condition": filter["condition_name"],
                            "input_value": filter_value,
                            "constraintName": "PlotDataFetchCons",
                            "ruleSet": "rule_set",
                            "and_or": "",
                        }
                    )
                else:
                    continue
            else:
                continue

        # Data Hierarchy conditions
        if request.user.is_superuser:
            hierarchy_dict = {}
            fk_columns = {}
            for field in modelName.concrete_fields:
                if field.get_internal_type() == "HierarchyField":
                    hierarchy_dict.setdefault(field.hierarchy_group, []).append(field.name)
                elif field.get_internal_type() == "ForeignKey":
                    actual_model_name_h = dynamic_model_create.get_model_class(
                        field.parent,
                        request,
                        db_connection_name="",
                        db_engine=user_db_engine,
                        db_type=db_type,
                    )
                    if actual_model_name_h.get_field(field.name).get_internal_type() == "HierarchyField":
                        hierarchy_dict.setdefault(
                            actual_model_name_h.get_field(field.name).hierarchy_group, []
                        ).append(field.name)
                        fk_columns[field.name] = {
                            "field_class": field,
                            "primary_key": actual_model_name_h.pk.name,
                        }
                    else:
                        continue
                else:
                    continue
            if hierarchy_dict:
                perm_dict = rules1.data_hierarchy_access_list(request, hierarchy_dict)
                for h_idx, h_group in enumerate(hierarchy_dict):
                    if perm_dict.get(h_group):
                        perm_list = tuple(perm_dict[h_group])
                        h_cols = hierarchy_dict[h_group]
                        perm_string = ", ".join("'" + i + "'" for i in perm_list)
                        if not perm_string.startswith("("):
                            perm_string = "(" + perm_string
                        if not perm_string.endswith(")"):
                            perm_string = perm_string + ")"

                        if h_idx != len(hierarchy_dict) - 1:
                            for c_idx, col in enumerate(h_cols):
                                if col in fk_columns:
                                    fk_field = fk_columns[col]["field_class"]
                                    fk_data = read_data_func(
                                        request,
                                        config_dict={
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": fk_field.parent,
                                                "Columns": [fk_columns[col]["primary_key"]],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": fk_field.name,
                                                    "condition": "IN",
                                                    "input_value": perm_string,
                                                    "and_or": "",
                                                },
                                            ],
                                        },
                                    )[fk_columns[col]["primary_key"]].to_list()
                                    perm_string = ", ".join(f"'{i}'" for i in fk_data)
                                    if not perm_string.startswith("("):
                                        perm_string = "(" + perm_string
                                    if not perm_string.endswith(")"):
                                        perm_string = perm_string + ")"
                                    fk_data = None
                                    del fk_data
                                else:
                                    pass
                                if c_idx == 0:
                                    h_cond = {
                                        "column_name": f"{col}",
                                        "condition": "IN",
                                        "input_value": perm_string,
                                        "constraintName": "PlotDataFetchCons",
                                        "ruleSet": "rule_set",
                                        "and_or": "",
                                    }
                                condition_list.append(h_cond)
                        else:
                            for c_idx, col in enumerate(h_cols):
                                if col in fk_columns:
                                    fk_field = fk_columns[col]["field_class"]
                                    fk_data = read_data_func(
                                        request,
                                        config_dict={
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": fk_field.parent,
                                                "Columns": [fk_columns[col]["primary_key"]],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": fk_field.name,
                                                    "condition": "IN",
                                                    "input_value": perm_string,
                                                    "and_or": "",
                                                },
                                            ],
                                        },
                                    )[fk_columns[col]["primary_key"]].to_list()
                                    perm_string = ", ".join(f"'{i}'" for i in fk_data)
                                    if not perm_string.startswith("("):
                                        perm_string = "(" + perm_string
                                    if not perm_string.endswith(")"):
                                        perm_string = perm_string + ")"
                                    fk_data = None
                                    del fk_data
                                else:
                                    pass
                                if c_idx == 0:
                                    h_cond = {
                                        "column_name": f"{col}",
                                        "condition": "IN",
                                        "input_value": perm_string,
                                        "constraintName": "PlotDataFetchCons",
                                        "ruleSet": "rule_set",
                                        "and_or": "",
                                    }
                                condition_list.append(h_cond)
                    else:
                        pass
            else:
                pass
        else:
            pass

        field_to_verbose = {field.name: field.verbose_name for field in modelName.concrete_fields}

        if "filters" in request.POST:
            filter_columns = json.loads(request.POST["filters"])
            data_type_dict = {
                i.name: i.get_internal_type() for i in modelName.concrete_fields if i.name in filter_columns
            }

            if filter_columns:
                filtered_input_data = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": tablename,
                            "Columns": filter_columns,
                            "Agg_Type": "DISTINCT",
                        },
                        "condition": [],
                        "adv_condition": [],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )

            for i in filter_columns:
                final_dict = {
                    "column_name": field_to_verbose[i],
                    "data_type": data_type_dict[i],
                    "field_name": i,
                }
                if data_type_dict[i] not in ["AutoField", "IntegerField", "BigIntegerField", "FloatField"]:
                    if data_type_dict[i] in ["DateField"]:
                        unique_data = (
                            pd.to_datetime(filtered_input_data[i])
                            .dropna()
                            .sort_values(ascending=False)
                            .dt.strftime("%Y-%m-%d")
                            .unique()
                            .tolist()
                        )
                        unique_data.insert(0, "Latest")
                    elif data_type_dict[i] == "DateTimeField":
                        unique_data = (
                            pd.to_datetime(filtered_input_data[i])
                            .dropna()
                            .sort_values(ascending=False)
                            .dt.strftime("%Y-%m-%d %H:%M:%S")
                            .unique()
                            .tolist()
                        )
                        unique_data.insert(0, "Latest")
                    elif data_type_dict[i] == "TimeField":
                        unique_data = (
                            pd.to_datetime(filtered_input_data[i])
                            .dropna()
                            .sort_values(ascending=False)
                            .dt.strftime("%H:%M:%S")
                            .unique()
                            .tolist()
                        )
                        unique_data.insert(0, "Latest")
                    else:
                        unique_data = filtered_input_data[i].fillna("NULL").unique().tolist()
                    final_dict["unique_data"] = unique_data
                else:
                    pass
                filter_column_list.append(final_dict)
        else:
            pass
    else:
        drange_data = {}
        field_to_verbose = {}

    context = {}
    if request.POST.get("graph_type") is None:
        graph_type = request.POST.get("graph_type")
        graph_subtype = request.POST.get("graph_subtype")
        if graph_subtype == "Nested_Table" or graph_subtype == "Table":
            y_axis = json.loads(request.POST.get("y_axis"))
            x_axis = json.loads(request.POST.get("x_axis"))
            second_column = request.POST.get("second_column")
        elif graph_subtype in [
            "Pivot_Table",
            "Table_Barchart",
            "Heatmap",
            "Row_Heatmap",
            "Col_Heatmap",
            "Line_Chart",
            "Bar_Chart",
            "Stacked_Bar_Chart",
            "Area_Chart",
            "Scatter_Chart",
        ]:
            x_axis = json.loads(request.POST.get("x_axis"))
        else:
            x_axis = request.POST.get("x_axis")
            y_axis = request.POST.get("y_axis")
            second_column = request.POST.get("second_column")
        plotDict = json.loads(request.POST.get("plotDict"))
    else:
        graph_type = request.POST.get("graph_type")
        graph_type = request.POST.get("graph_type").split("|")[0]
        graph_subtype = request.POST.get("graph_subtype").split("|")[0]
        if graph_type == "Table":
            y_axis = json.loads(request.POST.get("y_axis"))
            x_axis = json.loads(request.POST.get("x_axis"))
            second_column = request.POST.get("second_column")
        elif graph_subtype in [
            "Pivot Table",
            "Table Barchart",
            "Heatmap",
            "Row Heatmap",
            "Col Heatmap",
            "Line Chart",
            "Bar Chart",
            "Stacked Bar Chart",
            "Area Chart",
            "Scatter Chart",
        ]:
            x_axis = json.loads(request.POST.get("x_axis"))
        else:
            x_axis = request.POST.get("x_axis")
            y_axis = request.POST.get("y_axis").split("|")[0]
            second_column = request.POST.get("second_column").split("|")[0]
    if graph_subtype:
        graph_subtype = graph_subtype.replace(" ", "_")

    if filter_column_list != "None":
        context["filter_input_final"] = filter_column_list
    else:
        context["filter_input_final"] = []

    context["drange"] = drange_data

    if graph_subtype == "Image":
        pr_code = request.POST.get("second_column")
        filename = request.POST.get("operation") + "_" + x_axis
        instance = get_current_tenant()
        tenant = instance.name
        folder_path = f"{MEDIA_ROOT}/{tenant}/{app_code}/plotly_files/uploaded_images_plotly/"
        data_of_file = folder_path + pr_code + "/" + filename
        resultplot = ""
        if os.path.exists(folder_path + pr_code + "/" + filename):
            temp_image = Image.open(data_of_file)
            figfile = BytesIO()
            image_format = x_axis.rsplit(".", 1)[-1].lower()
            if image_format == "jpg":
                image_format = "jpeg"
            temp_image.save(figfile, format=image_format)
            temp_image.close()
            figfile.seek(0)
            figdata_png = figfile.getvalue()
            figdata_png = base64.b64encode(figdata_png)
            resultplot = figdata_png.decode("utf8")
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["e_id"] = request.POST.get("operation")
        context["second_column"] = request.POST.get("second_column")
        context["line_column"] = resultplot
        context["chartDivId"] = graph_subtype + "".join(y_axis) + request.POST.get("operation")

    if graph_subtype == "Nested_Table":
        operation = request.POST.get("operation")
        if operation == "None" or operation == "undefined" or operation is None:
            operation = ["sum"] * len(y_axis)
        else:
            if operation.startswith("["):
                operation = json.loads(operation)
            else:
                operation = [operation] * len(y_axis)
        x_axis_new = []
        y_axis_new = []
        for i in x_axis:
            x_axis_new.append(field_to_verbose[i])
        for i in y_axis:
            y_axis_new.append(field_to_verbose[i])

        fetch_columns_list = x_axis.copy()
        fetch_columns_list += y_axis
        filter_inputs = json.loads(request.POST.get("filter_inputs"))
        inputs2 = {
            "Data_source": "Database",
            "Table": tablename,
            "Columns": fetch_columns_list,
        }
        for filter in filter_inputs:
            if filter["filter_value"]:
                if filter["data_category"] == "Numerical":
                    if filter["condition_name"] == "Top N":
                        filter_value = filter["filter_value"]
                        column_name = filter["column_name"]
                        inputs2 = {
                            "Data_source": "Database",
                            "Table": tablename,
                            "Columns": fetch_columns_list,
                            "Order_Type": f"ORDER BY {column_name} desc",
                            "Agg_Type": f"TOP({filter_value})",
                        }
                    else:
                        continue
                else:
                    continue
            else:
                continue
        table = read_data_func(
            request,
            {
                "inputs": inputs2,
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        table.rename(columns=field_to_verbose, inplace=True)
        table_data = Table_Agg.PivotData(table, x_axis_new, y_axis_new, operation, modelName)

        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["headers"] = fetch_columns_list
        context["table_data"] = table_data
        context["table_view"] = table.fillna("-").to_dict("records")
        context["final_cols"] = ["Category"] + y_axis_new
        context["chartDivId"] = graph_subtype + "".join(y_axis) + "".join(x_axis)
        if request.POST.get("conditional_table") is not None:
            context["conditional_table"] = json.loads(request.POST.get("conditional_table"))
        else:
            context["conditional_table"] = ""

    if graph_subtype in [
        "Pivot_Table",
        "Table_Barchart",
        "Heatmap",
        "Row_Heatmap",
        "Col_Heatmap",
        "Line_Chart",
        "Bar_Chart",
        "Stacked_Bar_Chart",
        "Area_Chart",
        "Scatter_Chart",
    ]:
        operation = request.POST.get("operation")

        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": x_axis,
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )

        table.fillna("None", inplace=True)
        table = multiSelectDetail(
            tablename, table, request, modelName, db_engine=user_db_engine, db_type=db_type
        )
        table.rename(columns=field_to_verbose, inplace=True)
        content = table.to_dict("records")
        context["content"] = content
        context["x_axis"] = x_axis
        context["chartDivId"] = graph_subtype + "".join(x_axis)
        context["operation"] = request.POST.get("operation")
        if request.POST.get("conditional_table"):
            context["conditional_table"] = json.loads(request.POST.get("conditional_table"))
        else:
            context["conditional_table"] = ""

    if graph_subtype == "Table":
        operation = request.POST.get("operation").lower()
        filter_inputs = json.loads(request.POST.get("filter_inputs"))
        inputs2 = {
            "Data_source": "Database",
            "Table": tablename,
            "Columns": x_axis,
        }
        for filter in filter_inputs:
            if filter["filter_value"]:
                if filter["data_category"] == "Numerical":
                    if filter["condition_name"] == "Top N":
                        filter_value = filter["filter_value"]
                        column_name = filter["column_name"]
                        inputs2 = {
                            "Data_source": "Database",
                            "Table": tablename,
                            "Columns": x_axis,
                            "Order_Type": f"ORDER BY {column_name} desc",
                            "Agg_Type": f"TOP({filter_value})",
                        }
                    else:
                        continue
                else:
                    continue
            else:
                continue
        table = read_data_func(
            request,
            {
                "inputs": inputs2,
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        for field in modelName.concrete_fields:
            if field in table.columns:
                if table[field].dtype == "datetime64[ns]":
                    if field.get_internal_type() == "DateTimeField":
                        column_name = field.name
                        table[column_name] = table[column_name].dt.strftime("%Y-%m-%d %H:%M:%S")
                    elif field.get_internal_type() == "DateField":
                        column_name = field.name
                        table[column_name] = table[column_name].dt.strftime("%Y-%m-%d")
                    else:
                        continue
                else:
                    continue
            else:
                continue

        table.fillna("None", inplace=True)
        table = multiSelectDetail(
            tablename, table, request, modelName, db_engine=user_db_engine, db_type=db_type
        )
        table.rename(columns=field_to_verbose, inplace=True)
        content = table.to_dict("records")
        context["content"] = content
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["chartDivId"] = graph_subtype + "".join(x_axis)
        context["operation"] = request.POST.get("operation").lower()
        if request.POST.get("conditional_table") is not None:
            context["conditional_table"] = json.loads(request.POST.get("conditional_table"))
        else:
            context["conditional_table"] = ""

    if graph_subtype in ["Bubble_Chart", "3D_Scatter", "3D_Mesh"]:
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        fetch_columns_list = [x_axis, y_axis, second_column]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": fetch_columns_list,
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        if graph_subtype == "Bubble_Chart":
            x_axisdata = table[x_axis].fillna(0).to_list()
            y_axisdata = table[y_axis].fillna(0).to_list()
            y_axisdata2 = table[second_column].fillna(0).to_list()
        else:
            x_axisdata = table[x_axis].to_list()
            y_axisdata = table[y_axis].to_list()
            y_axisdata2 = table[second_column].to_list()
        table = table.to_dict("records")
        context["second_columndata"] = y_axisdata2
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["second_column"] = second_column
        operation = "None"
        context["chartDivId"] = y_axis + x_axis + second_column + graph_subtype

    if graph_subtype in ["Vertical_Bar", "Vertical_Waterfall"]:
        operation = request.POST.get("operation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            y_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])
        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["chartDivId"] = y_axis + x_axis + graph_subtype

    if graph_subtype in ["Vertical_Histogram", "Horizontal_Histogram", "Cumulative_Histogram"]:
        fetch_columns_list = [x_axis]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": fetch_columns_list,
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        context["x_axis"] = x_axis
        context["x_axisdata"] = list(table[x_axis])
        y_axis = "none"
        table = table.to_dict("records")
        context["chartDivId"] = x_axis + graph_subtype

    if graph_subtype == "Stacked_Histogram":
        fetch_columns_list = [x_axis, y_axis]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": fetch_columns_list,
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                table.loc[table[x_axis] == key, x_axis] = value

        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        x_axis2 = list(table[x_axis])
        y_axis2 = list(table[y_axis])
        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["x_axisdata"] = x_axis2

        context["y_axisdata"] = y_axis2
        context["chartDivId"] = y_axis + x_axis + graph_subtype
    if graph_subtype in ["Horizontal_Waterfall", "Funnel", "Horizontal_Bar", "Horizontal_Area"]:
        operation = request.POST.get("operation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            y_axis,
            operation,
            x_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[y_axis] == key, y_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        y_axisdata = list(table[y_axis])
        x_axisdata = list(table[x_axis])
        if len(table) > 0:
            table[x_axis] = table[x_axis].round(2)
            if table[x_axis].dtype == "float":
                x_axisdata = list(table[x_axis].round(2))
            else:
                x_axisdata = list(table[x_axis])

        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["chartDivId"] = y_axis + x_axis + graph_subtype

    if graph_subtype == "Funnel_Area":
        operation = request.POST.get("operation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            y_axis,
            operation,
            x_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])
        if len(table) > 0:
            table[x_axis] = table[x_axis].round(2)
            x_axisdata = list(table[x_axis].round(2))
        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["x_axisdata"] = x_axisdata
        colors = px.colors.sequential.turbid
        colordata2 = []
        for i in colors:
            color = literal_eval(i.split("b")[1])
            color = "#%02x%02x%02x" % color
            colordata2.append(color)
        context["colordata"] = colordata2
        context["y_axisdata"] = y_axisdata
        context["chartDivId"] = y_axis + x_axis + graph_subtype

    if graph_type == "Aggregation" or graph_subtype == "Aggregation":
        x_axis = request.POST.get("x_axis").split("|")[0]
        operation = request.POST.get("operation")
        aggregation_config = {
            "agg_distinct": request.POST.get("agg_distinct"),
            "operation_n": request.POST.get("operation_n"),
            "computed_number": request.POST.get("computed_number"),
        }
        value = aggregation_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            operation,
            x_axis,
            user_db_engine,
            db_type,
            aggregation_config=aggregation_config,
        )
        if operation not in ["Top N", "Bottom N"]:
            context["title"] = f"{operation} of {field_to_verbose[x_axis]}"
        else:
            context["title"] = (
                f"{request.POST.get('operation_n')} of {operation.rstrip(' N')} {request.POST.get('computed_number')} {field_to_verbose[x_axis]}"
            )
        context["x_axis"] = x_axis
        context["y_axis"] = x_axis
        context["second_column"] = x_axis
        context["operation"] = operation
        context["value"] = value
        context["chartDivId"] = x_axis + graph_subtype + operation
        if graph_type == "Aggregation":
            graph_subtype = graph_type
        else:
            pass

    if graph_subtype in ["Angular_Gauge", "Bullet_Gauge"]:
        if graph_subtype is not None:
            x_axis = request.POST.get("x_axis").split("|")[0]
        else:
            pass
        operation = request.POST.get("operation").lower()
        value = aggregation_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            operation,
            second_column,
            user_db_engine,
            db_type,
            aggregation_config={},
        )
        if operation not in ["Top N", "Bottom N"]:
            context["title"] = f"{operation} {field_to_verbose[second_column]} - {field_to_verbose[y_axis]}"
        else:
            context["title"] = (
                f"{request.POST.get('operation_n')} of {operation.rstrip(' N')} {request.POST.get('computed_number')} {field_to_verbose[second_column]}"
            )
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": [second_column],
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        y_axisdata2 = table[second_column].tolist()
        context["second_columndata"] = y_axisdata2
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["second_column"] = second_column
        context["operation"] = operation
        context["value"] = value
        context["chartDivId"] = y_axis + x_axis + second_column + graph_subtype + operation

    elif graph_subtype in ["Scatter", "2D_Histogram_Contour"]:
        fetch_columns_list = [x_axis, y_axis]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": fetch_columns_list,
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        if len(table) > 0:
            if table[x_axis].dtype == "float":
                table[x_axis] = table[x_axis].round(2)
            else:
                pass
            if table[y_axis].dtype == "float":
                table[y_axis] = table[y_axis].round(2)
            else:
                pass
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["x_axisdata"] = list(table[x_axis])
        context["y_axisdata"] = list(table[y_axis])
        table = table.to_dict("records")
        colors = px.colors.sequential.turbid
        colordata2 = []
        for i in colors:
            color = literal_eval(i.split("b")[1])
            color = "#%02x%02x%02x" % color
            colordata2.append(color)
        context["colordata"] = colordata2
        context["chartDivId"] = y_axis + x_axis + graph_subtype

    elif graph_subtype in ["Vertical_Box", "Vertical_Violin"]:
        fetch_columns_list = [x_axis, y_axis]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": fetch_columns_list,
                    "Order_Type": f"ORDER BY {x_axis}",
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")

        if table.empty is True:
            table[y_axis] = 0
        else:
            table[y_axis] = table[y_axis].round(2)

        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["x_axisdata"] = list(table[x_axis])
        context["y_axisdata"] = table[y_axis].tolist()
        table = table.to_dict("records")
        context["chartDivId"] = y_axis + x_axis + graph_subtype

    elif graph_subtype in ["Vertical_Grouped_Box", "Vertical_Grouped_Violin"]:
        fetch_columns_list = [x_axis, y_axis, second_column]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": fetch_columns_list,
                    "Order_Type": f"ORDER BY {x_axis}",
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        x_axisdata = list(table[x_axis])
        y_axisdata2 = list(table[second_column])
        if table.empty is True:
            table[y_axis] = 0
        else:
            table[y_axis] = table[y_axis].round(2)

        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["second_column"] = second_column
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = list(table[y_axis])
        context["second_columndata"] = y_axisdata2
        table = table.to_dict("records")
        context["chartDivId"] = y_axis + x_axis + second_column + graph_subtype

    elif graph_subtype in ["Horizontal_Grouped_Box", "Horizontal_Grouped_Violin"]:
        fetch_columns_list = [x_axis, y_axis, second_column]
        x_axis = request.POST.get("x_axis").split("|")[0]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": fetch_columns_list,
                    "Order_Type": f"ORDER BY {y_axis}",
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                table.loc[table[y_axis] == key, y_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")

        y_axisdata = list(table[y_axis])
        x_axisdata2 = list(table[second_column])
        if table.empty is True:
            table[x_axis] = 0
        else:
            table[x_axis] = table[x_axis].round(2)
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["second_column"] = second_column
        context["x_axisdata"] = list(table[x_axis])
        context["y_axisdata"] = table[y_axis].tolist()
        context["second_columndata"] = table[second_column].tolist()
        table = table.to_dict("records")
        context["chartDivId"] = y_axis + x_axis + second_column + graph_subtype

    elif graph_subtype in ["Horizontal_Box", "Horizontal_Violin"]:
        fetch_columns_list = [x_axis, y_axis]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": fetch_columns_list,
                    "Order_Type": f"ORDER BY {y_axis}",
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[y_axis] == key, y_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        x_axis2 = list(table[x_axis])
        y_axis2 = list(table[y_axis])
        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["x_axisdata"] = x_axis2
        context["y_axisdata"] = y_axis2
        context["chartDivId"] = y_axis + x_axis + graph_subtype

    elif graph_subtype == "Horizontal_Dot_Plot":
        fetch_columns_list = [x_axis, y_axis]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": fetch_columns_list,
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                table.loc[table[y_axis] == key, y_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")

        if len(table) > 0:
            if table[x_axis].dtype == "float":
                table[x_axis] = table[x_axis].round(2)
            else:
                pass
            if table[y_axis].dtype == "float":
                table[y_axis] = table[y_axis].round(2)
            else:
                pass
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["x_axisdata"] = list(table[x_axis])
        context["y_axisdata"] = list(table[y_axis])
        table = table.to_dict("records")
        context["chartDivId"] = y_axis + x_axis + graph_subtype

    elif graph_subtype == "Scatter_with_Straight_Lines_and_Markers":
        fetch_columns_list = [x_axis, y_axis]
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": fetch_columns_list,
                    "Order_Type": f"ORDER BY {x_axis}",
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        if table[x_axis].dtype == "float":
            table[x_axis] = table[x_axis].round(2)
        else:
            pass
        if table[y_axis].dtype == "float":
            table[y_axis] = table[y_axis].round(2)
        else:
            pass
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["x_axisdata"] = list(table[x_axis])
        context["y_axisdata"] = list(table[y_axis])
        table = table.to_dict("records")
        context["chartDivId"] = y_axis + x_axis + graph_subtype

    elif graph_subtype in ["Line", "Vertical_Area"]:
        operation = request.POST.get("operation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            y_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        y_axis2 = list(table[y_axis])
        if len(table) > 0:
            y_axis2 = list(table[y_axis].round(2))
        context["x_axis"] = x_axis
        context["x_axisdata"] = list(table[x_axis])
        context["y_axisdata"] = y_axis2
        context["chartDivId"] = y_axis + x_axis + graph_subtype
        context["y_axis"] = y_axis
        table = table.to_dict("records")

    elif graph_subtype == "Multiple_Line_Chart":
        operation = request.POST.get("operation").lower()
        if request.POST["y_axis"][0] == "[" and request.POST["y_axis"][-1] == "]":
            original_y_axis = json.loads(request.POST.get("y_axis"))
        else:
            original_y_axis = list(request.POST["y_axis"].split(","))
        new_y_axis = original_y_axis.copy()
        if x_axis in new_y_axis:
            new_y_axis.remove(x_axis)
        y_axis = new_y_axis[0]
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            original_y_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        y_axisdata = []
        for y in new_y_axis:
            if len(table) > 0:
                y_axisdata.append(list(table[y].round(2)))
            else:
                y_axisdata.append([])
        context["x_axis"] = x_axis
        context["x_axisdata"] = list(table[x_axis])
        context["y_axisdata"] = y_axisdata
        context["chartDivId"] = y_axis + x_axis + graph_subtype
        context["y_axis"] = new_y_axis
        table = table.to_dict("records")

    elif graph_subtype == "Stepped_Line":
        operation = request.POST.get("operation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            y_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        if len(table) > 0:
            table[y_axis] = table[y_axis].round(2)
        context["x_axis"] = x_axis
        context["x_axisdata"] = list(table[x_axis])
        context["y_axisdata"] = list(table[y_axis])
        context["chartDivId"] = y_axis + x_axis + graph_subtype
        context["y_axis"] = y_axis
        table = table.to_dict("records")

    elif graph_subtype in ["Pie_Chart", "Treemap", "Donut_Chart"]:
        operation = request.POST.get("operation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            y_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        if len(table) > 0:
            table[y_axis] = table[y_axis].round(2)
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["x_axisdata"] = list(table[x_axis])
        context["y_axisdata"] = list(table[y_axis])
        table = table.to_dict("records")
        colors = px.colors.sequential.turbid
        colordata2 = []
        for i in colors:
            color = literal_eval(i.split("b")[1])
            color = "#%02x%02x%02x" % color
            colordata2.append(color)
        context["colordata"] = colordata2
        context["chartDivId"] = y_axis + x_axis + graph_subtype

    elif graph_subtype == "Vertical_Waterfall_Grouped":
        operation = request.POST.get("operation").lower()
        agg_cols = [y_axis, second_column]
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            agg_cols,
            user_db_engine,
            db_type,
            modelName,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        x_axisdata = list(table[x_axis])
        if len(table) > 0:
            if table[y_axis].dtype == "float":
                y_axisdata = list(table[y_axis].round(2))
            else:
                y_axisdata = list(table[y_axis])
            if table[second_column].dtype == "float":
                y_axisdata2 = list(table[second_column].round(2))
            else:
                y_axisdata2 = list(table[second_column])
            table[y_axis] = table[y_axis].round(2)
            table[second_column] = table[second_column].round(2)
        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["second_column"] = second_column
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["second_columndata"] = y_axisdata2
        context["chartDivId"] = y_axis + x_axis + second_column + graph_subtype

    elif graph_subtype == "Vertical_Bar_Stacked" or graph_subtype == "Vertical_Bar_Grouped":
        operation = request.POST.get("operation").lower()
        if request.POST["y_axis"][0] == "[" and request.POST["y_axis"][-1] == "]":
            new_y_axis = json.loads(request.POST.get("y_axis"))
            total_y = request.POST.get("total_y")
        else:
            if second_column and second_column != "None":
                new_y_axis = []
                new_y_axis.append(y_axis)
                new_y_axis.append(second_column)
                total_y = 2
            else:
                new_y_axis = list(request.POST["y_axis"].split(","))
                total_y = request.POST.get("total_y")
        if x_axis in new_y_axis:
            new_y_axis.remove(x_axis)
        y_axis = new_y_axis[0]
        y_axis_new = new_y_axis
        all_axis = new_y_axis
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            new_y_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        x_axisdata = list(table[x_axis])
        y_axisdata = []
        for y in new_y_axis:
            if len(table) > 0:
                if table[y].dtype == "float":
                    y_axisdata.append(list(table[y].round(2)))
                else:
                    y_axisdata.append(list(table[y]))
            else:
                y_axisdata.append([])

        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["chartDivId"] = y_axis + x_axis + graph_subtype
        context["new_y_axis"] = new_y_axis
        context["y_axis"] = new_y_axis
        context["total_y"] = total_y

    elif graph_subtype == "Bar_Grouped_and_Line" or graph_subtype == "Bar_Stacked_and_Line":
        line_column = request.POST.get("line_column")
        operation = request.POST.get("operation").lower()
        if request.POST["y_axis"][0] == "[" and request.POST["y_axis"][-1] == "]":
            new_y_axis = json.loads(request.POST.get("y_axis"))
            total_y = request.POST.get("total_y")
        else:
            if second_column and second_column != "None":
                new_y_axis = []
                new_y_axis.append(y_axis)
                new_y_axis.append(second_column)
                total_y = 2
            else:
                new_y_axis = list(request.POST["y_axis"].split(","))
                total_y = request.POST.get("total_y")
        if x_axis in new_y_axis:
            new_y_axis.remove(x_axis)
        y_axis = new_y_axis[0]
        y_axis_new = new_y_axis
        all_axis = new_y_axis
        if request.POST.get("operation_line"):
            operation_line = request.POST.get("operation_line").lower()
            table_1 = groupby_data_fetch(
                request,
                tablename,
                condition_list,
                adv_condition_list,
                x_axis,
                operation,
                all_axis,
                user_db_engine,
                db_type,
                modelName,
            )
            table_2 = groupby_data_fetch(
                request,
                tablename,
                condition_list,
                adv_condition_list,
                x_axis,
                operation_line,
                line_column,
                user_db_engine,
                db_type,
                modelName,
            )
            table = table_1.merge(table_2, how="outer", on=x_axis, suffixes=(None, "_table2")).fillna(0)
        else:
            all_axis.append(line_column)
            table = groupby_data_fetch(
                request,
                tablename,
                condition_list,
                adv_condition_list,
                x_axis,
                operation,
                all_axis,
                user_db_engine,
                db_type,
                modelName,
            )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        if (line_column + "_table2") in table:
            line_column_merge = line_column + "_table2"
        else:
            line_column_merge = line_column
        x_axisdata = list(table[x_axis])
        line_data = list(table[line_column_merge])
        y_axisdata = []
        for y in new_y_axis:
            if len(table) > 0:
                y_axisdata.append(list(table[y].round(2)))
            else:
                y_axisdata.append([])
        if len(table) > 0:
            line_data = list(table[line_column_merge].round(2))
            table[y_axis] = table[y_axis].round(2)
            table[line_column_merge] = table[line_column_merge].round(2)
        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["line_column"] = line_column
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["line_columndata"] = line_data
        context["chartDivId"] = y_axis + x_axis + graph_subtype
        context["new_y_axis"] = new_y_axis
        context["y_axis"] = new_y_axis
        context["total_y"] = total_y

    elif graph_subtype == "Bar_Stacked_and_Multiple_Line":
        operation = request.POST.get("operation").lower()
        operation_line = request.POST.get("operation_line").lower()
        if request.POST["y_axis"][0] == "[" and request.POST["y_axis"][-1] == "]":
            new_y_axis = json.loads(request.POST.get("y_axis"))
            total_y = request.POST.get("total_y")
        else:
            if second_column and second_column != "None":
                new_y_axis = []
                new_y_axis.append(y_axis)
                new_y_axis.append(second_column)
                total_y = 2
            else:
                new_y_axis = list(request.POST["y_axis"].split(","))
                total_y = request.POST.get("total_y")
        if x_axis in new_y_axis:
            new_y_axis.remove(x_axis)
        y_axis = new_y_axis[0]
        y_axis_new = new_y_axis
        all_axis = new_y_axis
        if request.POST["line_column"][0] == "[" and request.POST["line_column"][-1] == "]":
            new_line_column = json.loads(request.POST.get("line_column"))
        else:
            new_line_column = list(request.POST["line_column"].split(","))
        if x_axis in new_line_column:
            new_line_column.remove(x_axis)
        line_column = new_line_column[0]
        all_axis_line = new_line_column

        table_1 = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation,
            all_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        table_2 = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            x_axis,
            operation_line,
            all_axis_line,
            user_db_engine,
            db_type,
            modelName,
        )
        table = table_1.merge(table_2, how="outer", on=x_axis, suffixes=(None, "_table2")).fillna(0)
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        x_axisdata = list(table[x_axis])
        y_axisdata = []
        for y in new_y_axis:
            if len(table) > 0:
                y_axisdata.append(list(table[y].round(2)))
            else:
                y_axisdata.append([])
        line_data = []
        for line in new_line_column:
            if (line + "_table2") in table:
                line_merge = line + "_table2"
            else:
                line_merge = line
            if len(table) > 0:
                line_data.append(list(table[line_merge].round(2)))
            else:
                line_data.append([])
        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["line_columndata"] = line_data
        context["chartDivId"] = y_axis + x_axis + graph_subtype
        context["line_column"] = new_line_column
        context["operation_line"] = operation_line
        context["new_y_axis"] = new_y_axis
        context["y_axis"] = new_y_axis
        context["total_y"] = total_y

    elif graph_subtype == "Sunburst":
        operation = request.POST.get("operation").lower()
        table2 = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            [x_axis, y_axis],
            operation,
            second_column,
            user_db_engine,
            db_type,
            modelName,
        )
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            [x_axis],
            operation,
            second_column,
            user_db_engine,
            db_type,
            modelName,
        )
        table[x_axis].fillna(" ", inplace=True)
        table2[x_axis].fillna(" ", inplace=True)
        table2[y_axis].fillna(" ", inplace=True)
        if table.empty is True:
            table2 = pd.DataFrame()
            table2["sunburst_id"] = ""
        else:
            if table2.empty is True:
                table2 = pd.DataFrame()
                table2["sunburst_id"] = ""
            else:
                table2["sunburst_id"] = table2[x_axis] + "" + "-" + "" + table2[y_axis]
        table = table.rename(columns={x_axis: y_axis})
        table[x_axis] = ""
        if len(table) > 0:
            table["sunburst_id"] = table[y_axis]
            table = table.append(table2)
            table[second_column] = table[second_column].round(2)
            sunburst_id = list(table["sunburst_id"])
        else:
            sunburst_id = ""
        colors = px.colors.sequential.turbid
        colordata2 = []
        for i in colors:
            color = literal_eval(i.split("b")[1])
            color = "#%02x%02x%02x" % color
            colordata2.append(color)
        context["colordata"] = colordata2
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])
        y_axisdata2 = list(table[second_column])
        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["second_column"] = second_column
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["sunburst_id"] = sunburst_id
        context["second_columndata"] = y_axisdata2
        context["chartDivId"] = y_axis + x_axis + second_column + graph_subtype

    elif graph_subtype in ["Vertical_Line_Stacked", "Vertical_Area_Stacked"]:
        operation = request.POST.get("operation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            [x_axis],
            operation,
            [y_axis, second_column],
            user_db_engine,
            db_type,
            modelName,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[x_axis] == key, x_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        x_axisdata = list(table[x_axis])
        y_axisdata = list(table[y_axis])
        y_axisdata2 = list(table[second_column])
        if len(table) > 0:
            y_axisdata = list(table[y_axis].round(2))
            y_axisdata2 = list(table[second_column].round(2))
            table[y_axis] = table[y_axis].round(2)
            table[second_column] = table[second_column].round(2)
        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["second_column"] = second_column
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["second_columndata"] = y_axisdata2
        context["chartDivId"] = y_axis + x_axis + second_column + graph_subtype

    elif graph_subtype in ["Horizontal_Bar_Stacked", "Horizontal_Bar_Grouped"]:
        operation = request.POST.get("operation").lower()
        if request.POST["x_axis"][0] == "[" and request.POST["x_axis"][-1] == "]":
            new_x_axis = json.loads(request.POST.get("x_axis"))
            total_y = request.POST.get("total_y")
        else:
            if second_column and second_column != "None":
                new_x_axis = []
                new_x_axis.append(x_axis)
                new_x_axis.append(second_column)
                total_y = 2
            else:
                new_x_axis = list(request.POST["x_axis"].split(","))
                total_y = request.POST.get("total_y")
        if y_axis in new_x_axis:
            new_x_axis.remove(y_axis)
        x_axis = new_x_axis[0]
        x_axis_new = new_x_axis
        all_axis = new_x_axis
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            y_axis,
            operation,
            all_axis,
            user_db_engine,
            db_type,
            modelName,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[y_axis] == key, y_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        x_axisdata = []
        for x in new_x_axis:
            if len(table) > 0:
                x_axisdata.append(list(table[x].round(2)))
            else:
                x_axisdata.append([])
        table = table.reset_index()
        y_axisdata = list(table[y_axis])
        table = table.to_dict("records")
        context["y_axis"] = y_axis
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["chartDivId"] = y_axis + x_axis + graph_subtype
        context["new_x_axis"] = new_x_axis
        context["x_axis"] = new_x_axis
        context["total_y"] = total_y

    elif graph_subtype in ["Horizontal_Area_Stacked", "Horizontal_Waterfall_Grouped", "Funnel_Stacked"]:
        x_axis = request.POST.get("x_axis").split("|")[0]
        operation = request.POST.get("operation").lower()
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            y_axis,
            operation,
            [x_axis, second_column],
            user_db_engine,
            db_type,
            modelName,
        )
        try:
            changed_text = plotDict["changed_text"]
            for i in changed_text:
                key = list(i.keys())[0]
                value = i[key]
                if len(table) > 0:
                    table.loc[table[y_axis] == key, y_axis] = value
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        if len(table) > 0:
            if table[x_axis].dtype == "float":
                x_axisdata = list(table[x_axis].round(2))
            else:
                x_axisdata = list(table[x_axis])
            if table[second_column].dtype == "float":
                x_axisdata2 = list(table[second_column].round(2))
            else:
                x_axisdata2 = list(table[second_column])
            if table[y_axis].dtype == "float":
                y_axisdata = list(table[y_axis].round(2))
            else:
                y_axisdata = list(table[y_axis])
            table[x_axis] = table[x_axis].round(2)
            table[second_column] = table[second_column].round(2)
        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["second_column"] = second_column
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["second_columndata"] = x_axisdata2
        context["chartDivId"] = y_axis + x_axis + second_column + graph_subtype

    elif graph_subtype in ["Bubble_Map", "Chloropeth_Map"]:
        operation = request.POST.get("operation")
        colors = px.colors.sequential.turbid
        colordata2 = []
        for i in colors:
            color = literal_eval(i.split("b")[1])
            color = "#%02x%02x%02x" % color
            colordata2.append(color)
        context["colordata"] = colordata2
        table = groupby_data_fetch(
            request,
            tablename,
            condition_list,
            adv_condition_list,
            y_axis,
            operation,
            [x_axis, second_column],
            user_db_engine,
            db_type,
            modelName,
        )
        x_axisdata = list(table[x_axis])
        x_axisdata2 = list(table[second_column])
        y_axisdata = list(table[y_axis])
        context["second_column"] = x_axisdata2
        context["x_axisdata"] = x_axisdata
        context["y_axisdata"] = y_axisdata
        context["second_columndata"] = x_axisdata2
        table = table.to_dict("records")
        context["x_axis"] = x_axis
        context["y_axis"] = y_axis
        context["chartDivId"] = str(date) + y_axis + x_axis + second_column + graph_subtype
    else:
        pass

    if (
        graph_subtype != "Aggregation"
        and graph_subtype != "Nested_Table"
        and graph_subtype != "Angular_Gauge"
        and graph_subtype != "Bullet_Gauge"
        and graph_subtype != "Bubble_Chart"
        and graph_subtype != "Image"
        and graph_subtype != "Table"
        and graph_subtype
        not in [
            "Pivot_Table",
            "Table_Barchart",
            "Heatmap",
            "Row_Heatmap",
            "Col_Heatmap",
            "Line_Chart",
            "Bar_Chart",
            "Stacked_Bar_Chart",
            "Area_Chart",
            "Scatter_Chart",
        ]
    ):
        context["table"] = table
    context["graph_subtype"] = graph_subtype
    try:
        context["operation"] = operation
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")

        context["operation"] = "None"
    datatype_list = []
    if graph_subtype != "Image" and graph_type != "Image":
        for i in modelName.concrete_fields:
            type_dict = {
                "column_name": i.verbose_name,
                "data_type": i.get_internal_type(),
                "field_name": i.name,
            }
            datatype_list.append(type_dict)
    context["datatype_list"] = datatype_list
    if graph_subtype == "Table":
        context["chartHeader"] = "Table"
        context["operation"] = operation
    elif graph_subtype in [
        "Pivot_Table",
        "Table_Barchart",
        "Heatmap",
        "Row_Heatmap",
        "Col_Heatmap",
        "Line_Chart",
        "Bar_Chart",
        "Stacked_Bar_Chart",
        "Area_Chart",
        "Scatter_Chart",
    ]:
        context["chartHeader"] = "Pivot Report"
    elif graph_subtype == "Nested_Table":
        context["chartHeader"] = "Nested Table"
    elif graph_type == "Aggregation":
        context["chartHeader"] = "Aggregation"
    elif graph_type == "Image" or graph_subtype == "Image":
        context["chartHeader"] = "Image"
    else:
        x_axis_verbose = field_to_verbose[x_axis]
        if y_axis in list(field_to_verbose.keys()):
            y_axis_verbose = field_to_verbose[y_axis]
        if graph_subtype in ["Vertical_Histogram", "Horizontal_Histogram", "Cumulative_Histogram"]:
            context["chartHeader"] = x_axis_verbose
            context["tableDivId"] = x_axis + y_axis + "table"
        elif graph_subtype == "Nested_Table":
            context["chartHeader"] = "Nested Table"
        elif graph_subtype == "Table":
            context["chartHeader"] = "Table"
        elif graph_subtype == "Multiple_Line_Chart":
            context["chartHeader"] = "Multi-Line Chart"
        else:
            context["chartHeader"] = x_axis_verbose + " " + "v" + " " + y_axis_verbose
            context["tableDivId"] = x_axis + y_axis + "table"
    if request.POST.get("plotDict") is None:
        pass
    else:
        context["plotDict"] = json.loads(request.POST.get("plotDict"))

    context["mappingDict"] = field_to_verbose
    return context


def save_plot(request):
    dashboard_data = pd.DataFrame(
        {
            "graph_data": request.POST.get("plotDataList"),
            "tab_id": request.POST.get("tab_id"),
            "tab_name": request.POST.get("tab_name"),
            "tabheight": request.POST.get("tabheight"),
            "changed_by_fk": request.user.id,
            "created_by_fk": request.user.id,
            "created_on": datetime.now(),
            "changed_on": datetime.now(),
        },
        index=[0],
    )
    dashboard_data["created_on"] = dashboard_data["created_on"].astype("datetime64[s]")
    dashboard_data["changed_on"] = dashboard_data["changed_on"].astype("datetime64[s]")

    data_handling(request, dashboard_data, "Dashboard_data")
    context = []

    ret_json = json.dumps(context, indent=4, sort_keys=True, default=str)

    response = {"Content - Type": "application/json", "response_status": 200, " response_content": ret_json}

    return JsonResponse(response)


def create_filter_inputs(request, app_code=None, mode=None):
    if request.POST["operation"] == "filter_data":
        context = {}
        if len(request.POST["tableName"]) > 0:
            tablename = request.POST["tableName"]
            modelName = dynamic_model_create.get_model_class(tablename, request)
            field_to_verbose = {field.name: field.verbose_name for field in modelName.concrete_fields}

            if "filters" in request.POST:
                filter_columns = json.loads(request.POST["filters"])

                data_type_dict = {
                    i.name: i.get_internal_type()
                    for i in modelName.concrete_fields
                    if i.name in filter_columns
                }
                fetch_filter_data_for_columns = [
                    i
                    for i in filter_columns
                    if data_type_dict[i] not in ["AutoField", "IntegerField", "BigIntegerField", "FloatField"]
                ]
                if fetch_filter_data_for_columns:
                    filter_data = []
                    table = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": tablename,
                                "Columns": fetch_filter_data_for_columns,
                                "Agg_Type": "DISTINCT",
                            },
                            "condition": [],
                            "adv_condition": [],
                        },
                    )

                    for i in filter_columns:
                        final_dict = {
                            "column_name": field_to_verbose[i],
                            "data_type": data_type_dict[i],
                            "field_name": i,
                        }
                        if data_type_dict[i] not in [
                            "AutoField",
                            "IntegerField",
                            "BigIntegerField",
                            "FloatField",
                        ]:
                            if data_type_dict[i] in ["DateField"]:
                                unique_data = (
                                    table[i]
                                    .dropna()
                                    .sort_values(ascending=False)
                                    .dt.strftime("%Y-%m-%d")
                                    .unique()
                                    .tolist()
                                )
                                unique_data.insert(0, "Latest")
                            elif data_type_dict[i] == "DateTimeField":
                                unique_data = (
                                    table[i]
                                    .dropna()
                                    .sort_values(ascending=False)
                                    .dt.strftime("%Y-%m-%d %H:%M:%S")
                                    .unique()
                                    .tolist()
                                )
                                unique_data.insert(0, "Latest")
                            elif data_type_dict[i] == "TimeField":
                                unique_data = (
                                    table[i]
                                    .dropna()
                                    .sort_values(ascending=False)
                                    .dt.strftime("%H:%M:%S")
                                    .unique()
                                    .tolist()
                                )
                                unique_data.insert(0, "Latest")
                            else:
                                unique_data = table[i].fillna("NULL").unique().tolist()
                            final_dict["unique_data"] = unique_data
                        else:
                            pass
                        filter_data.append(final_dict)
                    context["filter_inputs"] = filter_data
                    context["mappingDict"] = field_to_verbose
                else:
                    pass
            else:
                pass
        else:
            pass
        return JsonResponse(context)


def plotly_interaction(request, app_code=None, mode=None):
    if request.POST["operation"] == "interaction":

        table = request.POST["table"]
        col = request.POST["column"]
        val = json.loads(request.POST["val"])
        modelName = dynamic_model_create.get_model_class(table, request)
        field_name = [field.name for field in modelName.concrete_fields]
        verbose = {field.verbose_name: field.name for field in modelName.concrete_fields}
        fieldn = {field.name: field.verbose_name for field in modelName.concrete_fields}
        cond = []
        for i in val:
            cond.append(
                {
                    "column_name": col,
                    "condition": "Equal to",
                    "input_value": str(i),
                    "and_or": "OR",
                }
            )
        cond[len(cond) - 1]["and_or"] = ""
        selVal = read_data_func(
            request,
            {
                "inputs": {"Data_source": "Database", "Table": table, "Columns": field_name},
                "condition": cond,
            },
        )
        valToSent = selVal.rename(columns=fieldn).fillna("").to_dict("list")
        return JsonResponse({"data": valToSent, "data2": verbose})


def export_data(request, app_code=None, mode=None):
    curr_app_code, db_connection_name = standardised_functions.current_app_db_extractor(request)
    if len(request.POST["tableName"]) > 0:
        tablename = request.POST["tableName"]
        sql_table_name = "users_" + tablename.lower()
        modelName = dynamic_model_create.get_model_class(tablename, request)
        column_list = [field.name for field in modelName.concrete_fields]

        table = standardised_functions.get_data_from_cache(sql_table_name, request, tablename)
        field_to_verbose = {field.name: field.verbose_name for field in modelName.concrete_fields}
        column_type = {field.name: field.get_internal_type() for field in modelName.concrete_fields}
        hierarchy_dict = {}
        Hierarchy_fields = []

        for field in modelName.concrete_fields:
            if field.get_internal_type() == "HierarchyField":
                Hierarchy_fields.append(field.name)
                hierarchy_dict.setdefault(field.hierarchy_group, []).append(field.name)
            elif field.get_internal_type() == "ForeignKey":
                parent_model_name, table, table_h = standardised_functions.nestedForeignKey(
                    field, request, db_connection_name, table, field.name
                )
                actual_model_name_h = dynamic_model_create.get_model_class(parent_model_name, request)
                if actual_model_name_h.get_field(field.name).get_internal_type() == "HierarchyField":
                    Hierarchy_fields.append(field.name)
                    hierarchy_dict.setdefault(
                        actual_model_name_h.get_field(field.name).hierarchy_group, []
                    ).append(field.name)

        if not table.empty:
            if Hierarchy_fields != []:
                id_key = modelName.pk.name
                Hierarchy_fields.append(f"{id_key}")
                table1 = pd.DataFrame(table, columns=Hierarchy_fields)
                table1.columns = Hierarchy_fields
                table1["Hierarchy_dict"] = f"{hierarchy_dict}"
                perm_list = rules1.has_data_hierarchy_access(request, table1)
                table = table[perm_list]

        # Create list of conditions for data fetch:
        condition_list = []
        adv_condition_list = []

        # Slicer conditions
        if "slicerColumn" in request.POST:
            slicer_column = json.loads(request.POST["slicerColumn"])
            slicer_column_value = json.loads(request.POST.get("slicerColumnValue"))
            for slc_ind, i in enumerate(slicer_column):
                if i in column_list and slicer_column_value[slc_ind] not in [
                    "",
                    "All",
                    "all",
                    None,
                    [],
                    [""],
                    ["All"],
                    ["all"],
                ]:
                    if type(slicer_column_value[slc_ind]) == list:
                        slicer_condition = {
                            "column_name": i,
                            "condition": "IN",
                            "input_value": slicer_column_value[slc_ind],
                            "constraintName": "PlotDataFetchCons",
                            "ruleSet": "rule_set",
                            "and_or": "",
                        }
                    else:
                        slicer_condition = {
                            "column_name": i,
                            "condition": "Equal to",
                            "input_value": slicer_column_value[slc_ind],
                            "constraintName": "PlotDataFetchCons",
                            "ruleSet": "rule_set",
                            "and_or": "",
                        }
                    condition_list.append(slicer_condition)
                else:
                    continue
        else:
            pass

    graph_subtype = request.POST.get("graph_subtype")
    x_axis = request.POST.get("x_axis")
    y_axis = request.POST.get("y_axis")
    second_column = request.POST.get("second_column")
    line_column = request.POST.get("line_column")

    if x_axis == "" or x_axis == "null" or x_axis == "None":
        x_axis = None
    if y_axis == "" or y_axis == "null" or y_axis == "None":
        y_axis = None
    if second_column == "" or second_column == "null" or second_column == "None":
        second_column = None
    if line_column == "" or line_column == "null" or line_column == "None":
        line_column = None

    # Date range filter conditions
    drange_data = {}
    if "drange" in request.POST:
        drange_data = json.loads(request.POST["drange"])
        if drange_data:
            start_date = drange_data["start_date"]
            end_date = drange_data["end_date"]
            col_name = drange_data["col_name"]
            condition_list.append(
                {
                    "column_name": col_name,
                    "condition": "Between",
                    "input_value_lower": start_date,
                    "input_value_upper": end_date,
                    "constraintName": "PlotDataFetchCons",
                    "ruleSet": "rule_set",
                    "and_or": "",
                }
            )
        else:
            pass
    else:
        pass

    # Filter conditions
    filter_inputs = json.loads(request.POST.get("filter_input_final"))
    for filter in filter_inputs:
        filter_value = filter["filter_value"]
        if filter_value:
            if filter["data_category"] == "Categorical":
                if "Latest" in filter_value:
                    adv_condition_list.append(
                        {
                            "column_name": filter["column_name"],
                            "agg_condition": "MAX",
                            "condition": "",
                            "input_value": "",
                            "constraintName": "PlotDataFetchCons",
                            "ruleSet": "rule_set",
                            "and_or": "",
                        }
                    )
                    if len(filter_value) > 1:
                        filter_value.remove("Latest")
                        condition_list.append(
                            {
                                "column_name": filter["column_name"],
                                "condition": "IN",
                                "input_value": filter_value,
                                "constraintName": "PlotDataFetchCons",
                                "ruleSet": "rule_set",
                                "and_or": "",
                            }
                        )
                    else:
                        pass
                else:
                    condition_list.append(
                        {
                            "column_name": filter["column_name"],
                            "condition": "IN",
                            "input_value": filter_value,
                            "constraintName": "PlotDataFetchCons",
                            "ruleSet": "rule_set",
                            "and_or": "",
                        }
                    )
            elif filter["data_category"] == "Numerical":
                condition_list.append(
                    {
                        "column_name": filter["column_name"],
                        "condition": filter["condition_name"],
                        "input_value": filter_value,
                        "constraintName": "PlotDataFetchCons",
                        "ruleSet": "rule_set",
                        "and_or": "",
                    }
                )
            else:
                continue
        else:
            continue

    # Data Hierarchy conditions
    if request.user.is_superuser:
        hierarchy_dict = {}
        fk_columns = {}
        for field in modelName.concrete_fields:
            if field.get_internal_type() == "HierarchyField":
                hierarchy_dict.setdefault(field.hierarchy_group, []).append(field.name)
            elif field.get_internal_type() == "ForeignKey":
                actual_model_name_h = dynamic_model_create.get_model_class(
                    field.parent,
                    request,
                )
                if actual_model_name_h.get_field(field.name).get_internal_type() == "HierarchyField":
                    hierarchy_dict.setdefault(
                        actual_model_name_h.get_field(field.name).hierarchy_group, []
                    ).append(field.name)
                    fk_columns[field.name] = {
                        "field_class": field,
                        "primary_key": actual_model_name_h.pk.name,
                    }
                else:
                    continue
            else:
                continue
        if hierarchy_dict:
            perm_dict = rules1.data_hierarchy_access_list(request, hierarchy_dict)
            for h_idx, h_group in enumerate(hierarchy_dict):
                if perm_dict.get(h_group):
                    perm_list = tuple(perm_dict[h_group])
                    h_cols = hierarchy_dict[h_group]
                    perm_string = ", ".join("'" + i + "'" for i in perm_list)
                    if not perm_string.startswith("("):
                        perm_string = "(" + perm_string
                    if not perm_string.endswith(")"):
                        perm_string = perm_string + ")"

                    if h_idx != len(hierarchy_dict) - 1:
                        for c_idx, col in enumerate(h_cols):
                            if col in fk_columns:
                                fk_field = fk_columns[col]["field_class"]
                                fk_data = read_data_func(
                                    request,
                                    config_dict={
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": fk_field.parent,
                                            "Columns": [fk_columns[col]["primary_key"]],
                                        },
                                        "condition": [
                                            {
                                                "column_name": fk_field.name,
                                                "condition": "IN",
                                                "input_value": perm_string,
                                                "and_or": "",
                                            },
                                        ],
                                    },
                                )[fk_columns[col]["primary_key"]].to_list()
                                perm_string = ", ".join(f"'{i}'" for i in fk_data)
                                if not perm_string.startswith("("):
                                    perm_string = "(" + perm_string
                                if not perm_string.endswith(")"):
                                    perm_string = perm_string + ")"
                                fk_data = None
                                del fk_data
                            else:
                                pass
                            if c_idx == 0:
                                h_cond = {
                                    "column_name": f"{col}",
                                    "condition": "IN",
                                    "input_value": perm_string,
                                    "constraintName": "PlotDataFetchCons",
                                    "ruleSet": "rule_set",
                                    "and_or": "",
                                }
                            condition_list.append(h_cond)
                    else:
                        for c_idx, col in enumerate(h_cols):
                            if col in fk_columns:
                                fk_field = fk_columns[col]["field_class"]
                                fk_data = read_data_func(
                                    request,
                                    config_dict={
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": fk_field.parent,
                                            "Columns": [fk_columns[col]["primary_key"]],
                                        },
                                        "condition": [
                                            {
                                                "column_name": fk_field.name,
                                                "condition": "IN",
                                                "input_value": perm_string,
                                                "and_or": "",
                                            },
                                        ],
                                    },
                                )[fk_columns[col]["primary_key"]].to_list()
                                perm_string = ", ".join(f"'{i}'" for i in fk_data)
                                if not perm_string.startswith("("):
                                    perm_string = "(" + perm_string
                                if not perm_string.endswith(")"):
                                    perm_string = perm_string + ")"
                                fk_data = None
                                del fk_data
                            else:
                                pass
                            if c_idx == 0:
                                h_cond = {
                                    "column_name": f"{col}",
                                    "condition": "IN",
                                    "input_value": perm_string,
                                    "constraintName": "PlotDataFetchCons",
                                    "ruleSet": "rule_set",
                                    "and_or": "",
                                }
                            condition_list.append(h_cond)
                else:
                    pass
        else:
            pass
    else:
        pass

    if graph_subtype == "Multiple_Line_Chart":
        if request.POST["y_axis"][0] == "[" and request.POST["y_axis"][-1] == "]":
            new_y_axis = json.loads(request.POST.get("y_axis"))
        else:
            new_y_axis = list(request.POST["y_axis"].split(","))

        all_axis = new_y_axis
        if x_axis not in all_axis:
            all_axis.insert(0, x_axis)

        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": all_axis,
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
        )

    elif graph_subtype == "Vertical_Bar_Stacked" or graph_subtype == "Vertical_Bar_Grouped":
        if request.POST["y_axis"][0] == "[" and request.POST["y_axis"][-1] == "]":
            new_y_axis = json.loads(request.POST.get("y_axis"))
        else:
            if second_column and second_column != "None":
                new_y_axis = []
                new_y_axis.append(y_axis)
                new_y_axis.append(second_column)
            else:
                new_y_axis = list(request.POST["y_axis"].split(","))

        all_axis = new_y_axis
        if x_axis not in all_axis:
            all_axis.insert(0, x_axis)

        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": all_axis,
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
        )

    elif graph_subtype == "Horizontal_Bar_Stacked" or graph_subtype == "Horizontal_Bar_Grouped":
        if request.POST["x_axis"][0] == "[" and request.POST["x_axis"][-1] == "]":
            new_x_axis = json.loads(request.POST.get("x_axis"))
        else:
            if second_column and second_column != "None":
                new_x_axis = []
                new_x_axis.append(x_axis)
                new_x_axis.append(second_column)
            else:
                new_x_axis = list(request.POST["x_axis"].split(","))

        all_axis = new_x_axis
        if y_axis not in all_axis:
            all_axis.append(y_axis)

        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": all_axis,
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
        )

    elif graph_subtype == "Bar_Stacked_and_Multiple_Line":
        if request.POST["y_axis"][0] == "[" and request.POST["y_axis"][-1] == "]":
            new_y_axis = json.loads(request.POST.get("y_axis"))
        else:
            if second_column and second_column != "None":
                new_y_axis = []
                new_y_axis.append(y_axis)
                new_y_axis.append(second_column)
            else:
                new_y_axis = list(request.POST["y_axis"].split(","))

        if request.POST["line_column"][0] == "[" and request.POST["line_column"][-1] == "]":
            new_line_column = json.loads(request.POST.get("line_column"))
        else:
            new_line_column = list(request.POST["line_column"].split(","))

        all_axis = new_y_axis
        if x_axis not in all_axis:
            all_axis.insert(0, x_axis)
        for axis in new_line_column:
            all_axis.append(axis)

        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": all_axis,
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
        )

    elif graph_subtype == "Bar_Grouped_and_Line" or graph_subtype == "Bar_Stacked_and_Line":
        if request.POST["y_axis"][0] == "[" and request.POST["y_axis"][-1] == "]":
            new_y_axis = json.loads(request.POST.get("y_axis"))
        else:
            if second_column and second_column != "None":
                new_y_axis = []
                new_y_axis.append(y_axis)
                new_y_axis.append(second_column)
            else:
                new_y_axis = list(request.POST["y_axis"].split(","))

        all_axis = new_y_axis
        if x_axis not in all_axis:
            all_axis.insert(0, x_axis)
        if line_column not in all_axis:
            all_axis.append(line_column)

        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": tablename,
                    "Columns": all_axis,
                },
                "condition": condition_list,
                "adv_condition": adv_condition_list,
            },
        )

    else:
        if (
            line_column is not None
            and second_column is not None
            and x_axis is not None
            and y_axis is not None
        ):

            table = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": tablename,
                        "Columns": [x_axis, y_axis, line_column, second_column],
                    },
                    "condition": condition_list,
                    "adv_condition": adv_condition_list,
                },
            )

        elif line_column is None and second_column is not None and x_axis is not None and y_axis is not None:
            table = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": tablename,
                        "Columns": [x_axis, y_axis, second_column],
                    },
                    "condition": condition_list,
                    "adv_condition": adv_condition_list,
                },
            )

        elif line_column is None and second_column is None and x_axis is not None and y_axis is not None:
            table = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": tablename,
                        "Columns": [x_axis, y_axis],
                    },
                    "condition": condition_list,
                    "adv_condition": adv_condition_list,
                },
            )

        elif line_column is None and second_column is None and x_axis is None and y_axis is not None:
            table = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": tablename,
                        "Columns": [y_axis],
                    },
                    "condition": condition_list,
                    "adv_condition": adv_condition_list,
                },
            )

        elif line_column is None and second_column is None and x_axis is not None and y_axis is None:
            table = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": tablename,
                        "Columns": [x_axis],
                    },
                    "condition": condition_list,
                    "adv_condition": adv_condition_list,
                },
            )

        else:
            table = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": tablename,
                        "Columns": [x_axis, y_axis],
                    },
                    "condition": condition_list,
                    "adv_condition": adv_condition_list,
                },
            )

        columnList = table.columns
        if len(columnList) > 0:
            table = table.loc[:, columnList]
        fileName = graph_subtype + "_underlying_data.csv"
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={fileName}"
        field_names = table.columns.to_list()
        out_data = table.to_dict("records")
        writer = csv.DictWriter(response, field_names)
        writer.writerow({fn: fn for fn in field_names})
        writer.writerows(out_data)
        return response


def upload_image(request, app_code=None, mode=None):
    context = {}
    folder_name = request.POST["folder_name"]
    element_id = request.POST["elementid"]
    file_data = request.FILES["upload_image"]
    instance = get_current_tenant()
    tenant = instance.name
    folder_path = f"{MEDIA_ROOT}/{tenant}/{app_code}/plotly_files/uploaded_images_plotly/"
    fs = FileSystemStorage(folder_path + folder_name)
    fs.save(element_id + "_" + file_data.name, file_data)
    return JsonResponse(context)


def upload_bg_image(request, app_code=None, mode=None):
    context = {}
    folder_name = request.POST["folder_name"]
    element_id = request.POST["elementid"]
    file_data = request.FILES["upload_bg_image"]
    instance = get_current_tenant()
    tenant = instance.name
    folder_path = f"{MEDIA_ROOT}/{tenant}/{app_code}/plotly_files/uploaded_bg_images_plotly/"
    fs = FileSystemStorage(folder_path + folder_name)
    fs.save(element_id + "_" + file_data.name, file_data)
    filename = element_id + "_" + file_data.name
    data_of_file = folder_path + folder_name + "/" + filename
    resultplot = ""
    if os.path.exists(folder_path + folder_name + "/" + filename):
        temp_image = Image.open(data_of_file)
        figfile = BytesIO()
        image_format = file_data.name.rsplit(".", 1)[-1].lower()
        if image_format == "jpg":
            image_format = "jpeg"
        temp_image.save(figfile, format=image_format)
        temp_image.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        resultplot = figdata_png.decode("utf8")
    context["image_url"] = resultplot
    context["image_name"] = filename
    return JsonResponse(context)


def reload_bg_image(request, app_code=None, mode=None):
    context = {}
    folder_name = request.POST["folder_name"]
    filename = request.POST["filename"]
    instance = get_current_tenant()
    tenant = instance.name
    folder_path = f"{MEDIA_ROOT}/{tenant}/{app_code}/plotly_files/uploaded_bg_images_plotly/"
    data_of_file = folder_path + folder_name + "/" + filename
    resultplot = ""
    if os.path.exists(folder_path + folder_name + "/" + filename):
        temp_image = Image.open(data_of_file)
        figfile = BytesIO()
        image_format = filename.rsplit(".", 1)[-1].lower()
        if image_format == "jpg":
            image_format = "jpeg"
        temp_image.save(figfile, format=image_format)
        temp_image.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        resultplot = figdata_png.decode("utf8")
    context["image_url"] = resultplot
    context["image_name"] = filename
    return JsonResponse(context)


def delete_image(request, app_code=None, mode=None):
    context = {}
    folder_name = request.POST["folder_name"]
    name = request.POST["name"]
    instance = get_current_tenant()
    tenant = instance.name
    folder_path = f"{MEDIA_ROOT}/{tenant}/{app_code}/plotly_files/uploaded_images_plotly/"
    if os.path.exists(folder_path + folder_name + "/" + name):
        os.remove(folder_path + folder_name + "/" + name)
    else:
        pass
    return JsonResponse(context)


def multiSelectDetail(tablename, table, request, modelName, db_engine=["", {}], db_type=""):
    multi_select_field_dict = {}
    is_multi_select_field = False
    for field in modelName.concrete_fields:
        if field.get_internal_type() == "MultiselectField":
            is_multi_select_field = True
            temp_mul_config = json.loads(field.mulsel_config)
            for attri, conf_val in temp_mul_config.items():
                if (
                    attri == "value"
                    or attri == "masterColumn"
                    or attri == "master"
                    or attri == "add"
                    or attri == "def_MulVal"
                    or attri == "checkBox"
                    or attri == "condition"
                ):
                    if attri in multi_select_field_dict:
                        multi_select_field_dict[attri].append(conf_val[0])
                    else:
                        multi_select_field_dict[attri] = conf_val
                elif attri == "plusBtn" or attri == "popUpOption":
                    if attri in multi_select_field_dict:
                        multi_select_field_dict[attri].update(conf_val)
                    else:
                        multi_select_field_dict[attri] = conf_val
                else:
                    multi_select_field_dict[attri] = conf_val

    if is_multi_select_field:
        data = {}
        master = multi_select_field_dict["master"]

        if multi_select_field_dict.get("condition") not in [None]:
            data["cond"] = multi_select_field_dict["condition"]
        else:
            data["cond"] = []
        data["masterTable"] = multi_select_field_dict["value"]
        data["masterColumn"] = multi_select_field_dict["masterColumn"]
        data["tableColumn"] = multi_select_field_dict["char_column"]
        data["master"] = multi_select_field_dict["master"]
        data["add"] = multi_select_field_dict["add"]
        data["checkBox"] = multi_select_field_dict["checkBox"]

        for ind, row in table.iterrows():
            for col in master:
                index = master.index(col)
                if col in row and row[col] is not None:
                    if row[col].startswith("{") and row[col].endswith("}"):
                        table[col][ind] = (
                            f"""<button data-mastertable='{data["masterTable"][index]}' data-mastercolumn="{data['masterColumn'][index]}" data-add='{json.dumps(data["add"][index])}' onclick='viewDetailMulti.call(this)' style='background-color:transparent; border:transparent;' data-name='"""
                            + row[col]
                            + "'>View Details</button>"
                        )
                    else:
                        table[col][ind] = (
                            f"<p style='cursor: pointer;margin-bottom:0px;' data-name='"
                            + row[col]
                            + "'>No Details Configured</p>"
                        )
                else:
                    continue
    return table


def groupby_data_fetch(
    request,
    table_name,
    condition_list,
    adv_condition_list,
    groupby_col,
    operation,
    aggregation_cols,
    user_db_engine,
    db_type,
    modelName,
):
    if type(aggregation_cols) == str:
        aggregation_cols = [aggregation_cols]
    if type(groupby_col) == str:
        groupby_col = [groupby_col]
    if operation in [
        "sum",
        "average",
        "variance",
        "standard deviation",
        "count",
        "count distinct",
        "maximum",
        "minimum",
        "percentage of total",
    ]:
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": table_name,
                    "Columns": groupby_col.copy(),
                    "group_by": groupby_col.copy(),
                    "group_by_aggregation": {i: operation for i in aggregation_cols},
                },
                "condition": condition_list.copy(),
                "adv_condition": adv_condition_list.copy(),
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        try:
            table[aggregation_cols] = table[aggregation_cols].astype("float")
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
    else:
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": table_name,
                    "Columns": [*groupby_col.copy(), *aggregation_cols.copy()],
                },
                "condition": condition_list.copy(),
                "adv_condition": adv_condition_list.copy(),
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        if operation == "skewness":
            table = table.groupby(groupby_col.copy()).skew().fillna(0)
        elif operation == "median":
            table = table.groupby(groupby_col.copy()).median().fillna(0)
        elif operation == "kurtosis":
            table = table.groupby(groupby_col.copy()).apply(pd.DataFrame.kurt).fillna(0)
        elif operation == "first":
            table = table.groupby(groupby_col.copy()).first()
        elif operation == "last":
            table = table.groupby(groupby_col.copy()).last()
        else:
            pass
        table = table.reset_index()
    fk_columns = [i for i in modelName.concrete_fields if i.get_internal_type() == "ForeignKey"]
    for fk_col in fk_columns:
        if fk_col.name in table.columns:
            __pmn__, table, __tableh__ = standardised_functions.nestedForeignKey(
                fk_col, request, "", table, fk_col.name
            )
        else:
            continue
    return table


def aggregation_data_fetch(
    request,
    table_name,
    condition,
    adv_condition,
    operation,
    aggregation_col,
    user_db_engine,
    db_type,
    aggregation_config={},
):
    operation = operation.lower()
    if operation in [
        "sum",
        "average",
        "variance",
        "standard deviation",
        "count",
        "count distinct",
        "maximum",
        "minimum",
        "percentage of total",
    ]:
        value = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": table_name,
                    "Columns": [],
                    "group_by_aggregation": {aggregation_col: operation},
                },
                "condition": condition,
                "adv_condition": adv_condition,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
    else:
        table = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": table_name,
                    "Columns": [aggregation_col],
                },
                "condition": condition,
                "adv_condition": adv_condition,
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        if operation == "skewness":
            value = table[aggregation_col].skew().fillna(0)
        elif operation == "median":
            value = table[aggregation_col].median().fillna(0)
        elif operation == "kurtosis":
            value = table[aggregation_col].kurtosis().fillna(0)
        elif operation == "first":
            value = table[aggregation_col].head(1)
        elif operation == "last":
            value = table[aggregation_col].tail(1)
        elif operation in ["top n", "bottom n"]:
            agg_distinct = aggregation_config["agg_distinct"]
            operation_n = aggregation_config["operation_n"].lower()
            computed_number = int(aggregation_config["computed_number"])
            fetch_config_dict = {
                "inputs": {
                    "Data_source": "Database",
                    "Table": table_name,
                    "Columns": [aggregation_col],
                },
                "condition": condition,
                "adv_condition": adv_condition,
            }
            if agg_distinct == "true":
                fetch_config_dict["inputs"]["Agg_Type"] = "DISTINCT"
            else:
                pass
            table = read_data_func(
                request,
                fetch_config_dict,
                engine2=user_db_engine,
                db_type=db_type,
                engine_override=True,
            )
            if operation == "top n":
                table = table.sort_values(aggregation_col, ascending=False).head(computed_number)
            else:
                table = table.sort_values(aggregation_col, ascending=True).head(computed_number)
            if operation_n == "sum":
                value = table[aggregation_col].sum()
            elif operation_n == "average":
                value = table[aggregation_col].mean()
            elif operation_n == "maximum":
                value = table[aggregation_col].max()
            elif operation_n == "minimum":
                value = table[aggregation_col].min()
            elif operation_n == "variance":
                value = table[aggregation_col].var()
            elif operation_n == "median":
                value = table[aggregation_col].median()
            elif operation_n == "kurtosis":
                value = table[aggregation_col].kurtosis()
            elif operation_n == "skewness":
                value = table[aggregation_col].skew()
            elif operation_n == "standard deviation":
                value = table[aggregation_col].std()
            else:
                value = table[aggregation_col].count()
        else:
            pass
    if isinstance(value, pd.DataFrame):
        value = value.iloc[0, 0]
    elif isinstance(value, pd.Series):
        value = value.iloc[0]
    else:
        pass
    if not value:
        value = 0
    else:
        pass
    if type(value) == float:
        value = str(round(value, 2))
    else:
        value = str(value)
    return value
