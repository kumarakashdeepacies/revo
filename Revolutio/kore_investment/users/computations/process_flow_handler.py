from datetime import datetime
import json

import pandas as pd

from kore_investment.users.computations.db_centralised_function import (
    data_handling,
    read_data_func,
    update_data_func,
)


def master_complete_flow(
    result,
    data,
    transaction_id,
    is_aug,
    element_id,
    item_code,
    request,
    e_id1=[],
    status="pass",
    exceptions="",
    transaction_id_=[],
    t_info=[],
    total_batch_data="0",
    cond_data_len=None,
    tree=False,
    element_id_contain="",
    element_id_not_contain="",
    fail=False,
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
    if transaction_id not in ["NULL", None]:
        if not fail:
            if True in list(result.values()):
                if transaction_id not in ["NULL", None]:
                    for t_id in json.loads(transaction_id):
                        if data.get(t_id).get("element_id__") not in [None]:
                            if result[t_id] in [True]:
                                if is_aug:
                                    if total_batch_data == "0":
                                        completeFlow(
                                            element_id,
                                            item_code,
                                            request,
                                            "skip",
                                            "",
                                            [],
                                            [],
                                            "1",
                                            element_id_contain=data[t_id]["element_id__"],
                                            element_id_not_contain=e_id1,
                                            tree=True,
                                        )
                                    else:
                                        completeFlow(
                                            element_id,
                                            item_code,
                                            request,
                                            "skip",
                                            "",
                                            [],
                                            [],
                                            total_batch_data=total_batch_data,
                                            cond_data_len=cond_data_len,
                                            element_id_contain=data[t_id]["element_id__"],
                                            element_id_not_contain=e_id1,
                                            tree=True,
                                        )
                                else:
                                    if total_batch_data == "0":
                                        completeFlow(
                                            element_id,
                                            item_code,
                                            request,
                                            "pass",
                                            "",
                                            [],
                                            [],
                                            "1",
                                            element_id_contain=data[t_id]["element_id__"],
                                            element_id_not_contain=e_id1,
                                            tree=True,
                                        )
                                    else:
                                        completeFlow(
                                            element_id,
                                            item_code,
                                            request,
                                            status,
                                            "",
                                            [],
                                            [],
                                            total_batch_data=total_batch_data,
                                            cond_data_len=cond_data_len,
                                            element_id_contain=data[t_id]["element_id__"],
                                            element_id_not_contain=e_id1,
                                            tree=True,
                                        )

                            else:
                                completeFlow(
                                    element_id,
                                    item_code,
                                    request,
                                    "fail",
                                    f"{result[t_id]}",
                                    element_id_contain=data[t_id]["element_id__"],
                                )
            else:
                for t_id in json.loads(transaction_id):
                    completeFlow(
                        element_id,
                        item_code,
                        request,
                        "fail",
                        f"{result[t_id]}",
                    )
        else:
            completeFlow(
                element_id,
                item_code,
                request,
                "fail",
                result,
            )
    return None


def process_flow_monitor(
    element_id,
    subprocess_code,
    app_code,
    request,
    data=None,
    transaction_id=None,
    current_element_status="pass",
    current_element_message="Success",
    total_data="0",
    passed_data="0",
    computation_data_pass_on={},
    run_time=None,
):
    """
    Records the status of user actions on the elements in configured process flow

    Parameters:
        element_id (str): Element id of the process tab/ block.
        subprocess_code (str): Id of the sub-process where this element is in.
        app_code (str): Id of the application where this sub-process is in.
        request (AsgiRequest): Django request object.
        data (pandas Dataframe): Data pertaining to the current element (default is None).
        transaction_id (str): Id of the existing transaction (default is None).
        current_element_status (str): Status of the action on the current element (default is Pass).
        current_element_message (str): Status message of the current element's execution (default is Success).
        computation_data_pass_on (dict): Data from current element to be passed to subsequent element (default is {}).
        run_time (str): run time of specific transaction is recorded
    """
    transaction_details = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Process_flow_model",
                "Columns": ["flow", "transaction_id", "current_status"],
            },
            "condition": [
                {
                    "column_name": "subprocess",
                    "condition": "Equal to",
                    "input_value": subprocess_code,
                    "and_or": "AND",
                },
                {
                    "column_name": "app_code",
                    "condition": "Equal to",
                    "input_value": app_code,
                    "and_or": "AND",
                },
                {
                    "column_name": "element_id",
                    "condition": "Equal to",
                    "input_value": element_id,
                    "and_or": "AND",
                },
                {
                    "column_name": "transaction_id",
                    "condition": "Equal to",
                    "input_value": transaction_id,
                    "and_or": "AND",
                },
                {
                    "column_name": "(current_status",
                    "condition": "Equal to",
                    "input_value": "Not started",
                    "and_or": "OR",
                },
                {
                    "column_name": "current_status",
                    "condition": "Equal to",
                    "input_value": "Ongoing",
                    "and_or": ")",
                },
            ],
        },
    )
    username = request.user.username
    if not transaction_details.empty:
        # Existing Transaction: update transaction details
        if current_element_status == "pass":
            if total_data != passed_data:
                # All records in the transaction passed
                update_data_func(
                    request,
                    config_dict={
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "Process_flow_model",
                            "Columns": [
                                {
                                    "column_name": "current_status",
                                    "input_value": "Ongoing",
                                    "separator": ",",
                                },
                                {
                                    "column_name": "modified_date",
                                    "input_value": datetime.now(),
                                    "separator": ",",
                                },
                                {
                                    "column_name": "total_batch_data",
                                    "input_value": str(total_data),
                                    "separator": ",",
                                },
                                {
                                    "column_name": "pass_batch_data",
                                    "input_value": str(passed_data),
                                    "separator": ",",
                                },
                                {
                                    "column_name": "detailed_status",
                                    "input_value": f"{total_data - passed_data} record(s) is pending out of {total_data}",
                                    "separator": ",",
                                },
                                {
                                    "column_name": "modified_by",
                                    "input_value": username,
                                    "separator": "",
                                },
                                {
                                    "column_name": "run_time",
                                    "input_value": run_time,
                                    "separator": "",
                                },
                            ],
                        },
                        "condition": [
                            {
                                "column_name": "element_id",
                                "condition": "Equal to",
                                "input_value": element_id,
                                "and_or": "AND",
                            },
                            {
                                "column_name": "transaction_id",
                                "condition": "Equal to",
                                "input_value": transaction_id,
                                "and_or": "AND",
                            },
                            {
                                "column_name": "app_code",
                                "condition": "Equal to",
                                "input_value": app_code,
                                "and_or": "AND",
                            },
                            {
                                "column_name": "subprocess",
                                "condition": "Equal to",
                                "input_value": subprocess_code,
                                "and_or": "",
                            },
                        ],
                    },
                )
            else:
                # All records in the transaction passed
                transaction_flow = json.loads(transaction_details.flow.iloc[0])
                flow_from_current_element = transaction_flow[transaction_flow.index(element_id) :]
                last_element_status = current_element_status
                for flow_index, flow_ele in enumerate(flow_from_current_element):
                    if flow_ele == element_id or (
                        last_element_status == "pass"
                        and (flow_ele.startswith("process") or flow_ele.startswith("ellipse"))
                    ):
                        if last_element_status == "pass":
                            status = "Pass"
                            detailed_status = "Success"
                            redirect_status = "Active"
                        else:
                            status = "Not started"
                            detailed_status = "Not started"
                            redirect_status = "Not active"
                        update_data_func(
                            request,
                            config_dict={
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "Process_flow_model",
                                    "Columns": [
                                        {
                                            "column_name": "current_status",
                                            "input_value": status,
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "modified_date",
                                            "input_value": datetime.now(),
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "total_batch_data",
                                            "input_value": str(total_data),
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "pass_batch_data",
                                            "input_value": str(passed_data),
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "detailed_status",
                                            "input_value": detailed_status,
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "redirect_status",
                                            "input_value": redirect_status,
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "modified_by",
                                            "input_value": username,
                                            "separator": "",
                                        },
                                        {
                                            "column_name": "run_time",
                                            "input_value": run_time,
                                            "separator": "",
                                        },
                                    ],
                                },
                                "condition": [
                                    {
                                        "column_name": "element_id",
                                        "condition": "Equal to",
                                        "input_value": element_id,
                                        "and_or": "AND",
                                    },
                                    {
                                        "column_name": "transaction_id",
                                        "condition": "Equal to",
                                        "input_value": transaction_id,
                                        "and_or": "AND",
                                    },
                                    {
                                        "column_name": "app_code",
                                        "condition": "Equal to",
                                        "input_value": app_code,
                                        "and_or": "AND",
                                    },
                                    {
                                        "column_name": "subprocess",
                                        "condition": "Equal to",
                                        "input_value": subprocess_code,
                                        "and_or": "",
                                    },
                                ],
                            },
                        )
                        if len(flow_from_current_element) > flow_index + 1:
                            next_element = flow_from_current_element[flow_index + 1]
                            element_connector_detail = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "TabScreens",
                                        "Columns": ["tab_body_content"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "related_item_code",
                                            "condition": "Equal to",
                                            "input_value": subprocess_code,
                                            "and_or": "AND",
                                        },
                                        {
                                            "column_name": "tab_body_content",
                                            "condition": "Contains",
                                            "input_value": f'"child": "{next_element}"',
                                            "and_or": "AND",
                                        },
                                        {
                                            "column_name": "tab_body_content",
                                            "condition": "Contains",
                                            "input_value": f'"autoRun": true',
                                            "and_or": "AND",
                                        },
                                        {
                                            "column_name": "tab_type",
                                            "condition": "Equal to",
                                            "input_value": "connector",
                                            "and_or": "",
                                        },
                                    ],
                                },
                            )
                            if not element_connector_detail.empty:
                                connector_config = json.loads(
                                    element_connector_detail.tab_body_content.iloc[0]
                                )
                                if connector_config.get("computationInputConfig"):
                                    computation_data_pass_on["computationInputConfig"] = connector_config.get(
                                        "computationInputConfig"
                                    )
                                else:
                                    pass
                                next_element = connector_config["child"]
                                execute_auto_run_computation(
                                    next_element,
                                    subprocess_code,
                                    request,
                                    computation_data_pass_on=computation_data_pass_on,
                                )
                            else:
                                continue
                        else:
                            break
                    else:
                        break
        else:
            update_data_func(
                request,
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "Process_flow_model",
                        "Columns": [
                            {
                                "column_name": "current_status",
                                "input_value": "Fail",
                                "separator": ",",
                            },
                            {
                                "column_name": "modified_date",
                                "input_value": datetime.now(),
                                "separator": ",",
                            },
                            {
                                "column_name": "total_batch_data",
                                "input_value": str(total_data),
                                "separator": ",",
                            },
                            {
                                "column_name": "pass_batch_data",
                                "input_value": str(passed_data),
                                "separator": ",",
                            },
                            {
                                "column_name": "detailed_status",
                                "input_value": current_element_message,
                                "separator": ",",
                            },
                            {
                                "column_name": "modified_by",
                                "input_value": username,
                                "separator": "",
                            },
                            {
                                "column_name": "run_time",
                                "input_value": run_time,
                                "separator": "",
                            },
                        ],
                    },
                    "condition": [
                        {
                            "column_name": "element_id",
                            "condition": "Equal to",
                            "input_value": element_id,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "transaction_id",
                            "condition": "Equal to",
                            "input_value": transaction_id,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "app_code",
                            "condition": "Equal to",
                            "input_value": app_code,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "subprocess",
                            "condition": "Equal to",
                            "input_value": subprocess_code,
                            "and_or": "",
                        },
                    ],
                },
            )
    else:
        # New Transaction: create transaction details and record in Process flow model table
        flow_connector_details = (
            read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "TabScreens",
                        "Columns": ["tab_body_content"],
                    },
                    "condition": [
                        {
                            "column_name": "related_item_code",
                            "condition": "Equal to",
                            "input_value": subprocess_code,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "tab_type",
                            "condition": "Equal to",
                            "input_value": "connector",
                            "and_or": "",
                        },
                    ],
                },
            )
            .tab_body_content.apply(json.loads)
            .tolist()
        )
        if flow_connector_details:
            subprocess_flow_data = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "process_subprocess_flowchart",
                        "Columns": ["flowchart_elements"],
                    },
                    "condition": [
                        {
                            "column_name": "related_item_code",
                            "condition": "Equal to",
                            "input_value": subprocess_code,
                            "and_or": "",
                        }
                    ],
                },
            ).flowchart_elements.iloc[0]
            subprocess_flow_data = json.loads(subprocess_flow_data)
            subprocess_flow_data = {ele["shapeID"]: ele for ele in subprocess_flow_data}
            process_flow_path = [element_id]
            process_flow_status = {
                element_id: {
                    "status": current_element_status.title(),
                    "detailed_status": current_element_message,
                }
            }
            flow_ended = False
            current_element = element_id
            last_element_status = current_element_status
            while not flow_ended:
                for conn in flow_connector_details:
                    if conn["parent"] == current_element:
                        current_element_details = subprocess_flow_data[current_element]
                        if current_element_details["shape"] == "flowcontrol":
                            if type(data) != type(None):
                                next_elements = flow_controller_handler(current_element, request, data)
                                if len(next_elements) != 0:
                                    if last_element_status == "pass":
                                        process_flow_status[current_element] = {
                                            "status": "Pass",
                                            "detailed_status": "Success",
                                            "connector_config": conn,
                                        }
                                    else:
                                        last_element_status = "Not started"
                                        process_flow_status[current_element] = {
                                            "status": last_element_status,
                                            "detailed_status": last_element_status,
                                            "connector_config": conn,
                                        }
                                    if len(next_elements) == 1:
                                        current_element = next_elements[0]
                                    else:
                                        pass
                                else:
                                    last_element_status = "fail"
                                    if last_element_status == "pass":
                                        process_flow_status[current_element] = {
                                            "status": "Pass",
                                            "detailed_status": "Success",
                                            "connector_config": conn,
                                        }
                                    else:
                                        last_element_status = "Not started"
                                        process_flow_status[current_element] = {
                                            "status": last_element_status,
                                            "detailed_status": last_element_status,
                                            "connector_config": conn,
                                        }
                            else:
                                if last_element_status == "pass":
                                    last_element_status = "fail"
                                    process_flow_status[current_element] = {
                                        "status": "fail",
                                        "detailed_status": "None of the conditions satisfied by the data.",
                                        "connector_config": conn,
                                    }
                                else:
                                    last_element_status = "Not started"
                                    process_flow_status[current_element] = {
                                        "status": last_element_status,
                                        "detailed_status": last_element_status,
                                        "connector_config": conn,
                                    }
                                flow_ended = True
                                break
                        else:
                            if current_element != element_id:
                                if last_element_status == "pass" and (
                                    current_element_details["shape"] == "process"
                                    or current_element.startswith("ellipse")
                                ):
                                    process_flow_status[current_element] = {
                                        "status": "Pass",
                                        "detailed_status": "Success",
                                        "connector_config": conn,
                                    }
                                else:
                                    last_element_status = "Not started"
                                    process_flow_status[current_element] = {
                                        "status": last_element_status,
                                        "detailed_status": last_element_status,
                                        "connector_config": conn,
                                    }
                            else:
                                process_flow_status[current_element]["connector_config"] = conn
                            current_element = conn["child"]
                        process_flow_path.append(current_element)

                        if subprocess_flow_data[current_element]["child"] == "#":
                            if last_element_status == "pass" and (
                                subprocess_flow_data[current_element]["shape"] == "process"
                                or current_element.startswith("ellipse")
                            ):
                                process_flow_status[current_element] = {
                                    "status": "Pass",
                                    "detailed_status": "Success",
                                    "connector_config": {},
                                }
                            else:
                                last_element_status = "Not started"
                                process_flow_status[current_element] = {
                                    "status": last_element_status,
                                    "detailed_status": last_element_status,
                                    "connector_config": {},
                                }
                            flow_ended = True
                            break
                        else:
                            pass
                        break
                    else:
                        continue
            createTransactionRecords(
                subprocess_code, process_flow_status, app_code, transaction_id, request, run_time
            )
            for ele, ele_details in process_flow_status.items():
                if ele_details["status"] == "Pass" and ele_details.get("connector_config"):
                    if ele_details["connector_config"]["autoRun"]:
                        if ele_details["connector_config"].get("computationInputConfig"):
                            computation_data_pass_on["computationInputConfig"] = ele_details[
                                "connector_config"
                            ].get("computationInputConfig")
                        else:
                            pass
                        next_element = ele_details["connector_config"]["child"]
                        execute_auto_run_computation(
                            next_element,
                            subprocess_code,
                            request,
                            computation_data_pass_on=computation_data_pass_on,
                        )
                    else:
                        continue
                else:
                    continue
        else:
            pass
    return None


def flow_controller_handler(element_id, request, data):
    """
    Identifies the next element in the flow basis the scenarios configured in flow controller block

    Parameters:
        element_id (str): Element id of the subprocess tab/ block.
        request (AsgiRequest): Django request object.
        data (pandas DataFrame): Data pertaining to the parent element of the flow controller.
    """
    flow_controller_details = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "TabScreens",
                "Columns": ["tab_body_content"],
            },
            "condition": [
                {
                    "column_name": "element_id",
                    "condition": "Equal to",
                    "input_value": element_id,
                    "and_or": "",
                }
            ],
        },
    ).tab_body_content.iloc[0]
    flow_controller_details = json.loads(flow_controller_details)
    flow_controller_details = flow_controller_details["Category_sub_elements"][0][
        "Category_sub_element_attributes"
    ][1]["value"]
    next_element = []
    for key, value in flow_controller_details.items():
        if value != "augmentation" and key not in ["decision_name", "decision_purpose"]:
            condition_value = value["value"]
            if value["type"] == "FloatField":
                condition_value = float(condition_value)
            elif value["type"] == "IntegerField":
                condition_value = int(condition_value)
            elif value["type"] == "BigIntegerField":
                condition_value = int(condition_value)
            elif value["type"] in ["DateField", "DateTimeField"]:
                condition_value = pd.to_datetime(condition_value)
            else:
                pass

            if value["condition"] == "Starts with":
                if not data[data[value["column"]].astype("str").startswith(condition_value)].empty:
                    next_element.append(key)
                else:
                    continue
            elif value["condition"] == "Ends with":
                if not data[data[value["column"]].str.endswith(condition_value)].empty:
                    next_element.append(key)
                else:
                    continue
            elif value["condition"] == "Equal to":
                if not data[data[value["column"]] == condition_value].empty:
                    next_element.append(key)
                else:
                    continue
            elif value["condition"] == "Not Equal to":
                if not data[data[value["column"]] != condition_value].empty:
                    next_element.append(key)
                else:
                    continue
            elif value["condition"] == "Greater than":
                if not data[data[value["column"]] > condition_value].empty:
                    next_element.append(key)
                else:
                    continue
            elif value["condition"] == "Smaller than":
                if not data[data[value["column"]] < condition_value].empty:
                    next_element.append(key)
                else:
                    continue
            elif value["condition"] == "IN":
                if not data[data[value["column"]].isin(condition_value)].empty:
                    next_element.append(key)
                else:
                    continue
            elif value["condition"] == "NOT IN":
                if not data[~data[value["column"]].isin(condition_value)].empty:
                    next_element.append(key)
                else:
                    continue
            else:
                continue
        else:
            continue
    return next_element


def createTransactionRecords(subprocess_code, subprocess_flow, app_code, transaction_id, request, run_time):
    """
    Creates transaction detail records in process flow model table

    Parameters:
        subprocess_code (str): Id of the sub-process where this element is in.
        subprocess_flow (dict): Dictionary of flow elements with details.
        transaction_id (str): Id of the existing transaction.
        app_code (str): Id of the application where this sub-process is in.
        request (AsgiRequest): Django request object.
        run_time (str): run time of specific transaction is recorded
    """
    username = request.user.username
    run_left = "0"
    process_code = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "NavigationSideBar",
                "Columns": ["item_group_code"],
            },
            "condition": [
                {
                    "column_name": "item_code",
                    "condition": "Equal to",
                    "input_value": subprocess_code,
                    "and_or": "",
                }
            ],
        },
    ).item_group_code.iloc[0]
    element_details = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "TabScreens",
                "Columns": ["element_id", "tab_header_name", "tab_type"],
            },
            "condition": [
                {
                    "column_name": "element_id",
                    "condition": "IN",
                    "input_value": list(subprocess_flow.keys()),
                    "and_or": "",
                },
            ],
        },
    )
    flow_data = pd.DataFrame(
        columns=[
            "app_code",
            "process",
            "subprocess",
            "transaction_id",
            "flow",
            "flow_id",
            "current_status",
            "element_id",
            "created_by",
            "created_date",
            "modified_by",
            "modified_date",
            "element_name",
            "data_id",
            "tab_type",
            "detailed_status",
            "redirect_status",
            "run_left",
            "run_time",
        ]
    )
    for ele in subprocess_flow:
        connector_config = subprocess_flow[ele].get("connector_config")
        flow_id = "NULL"
        if connector_config:
            if connector_config.get("nextElement"):
                flow_id = json.dumps(connector_config.get("nextElement"))
            else:
                pass
        else:
            pass
        if subprocess_flow[ele]["status"] == "Pass":
            redirect_status = "Active"
        else:
            redirect_status = "Not active"
        transaction_element_detail = pd.DataFrame(
            [
                {
                    "app_code": app_code,
                    "process": process_code,
                    "subprocess": subprocess_code,
                    "transaction_id": transaction_id,
                    "flow": json.dumps(list(subprocess_flow.keys())),
                    "flow_id": flow_id,
                    "current_status": subprocess_flow[ele]["status"],
                    "element_id": ele,
                    "created_by": username,
                    "created_date": datetime.now(),
                    "modified_by": username,
                    "modified_date": datetime.now(),
                    "element_name": element_details.loc[
                        element_details.element_id == ele, "tab_header_name"
                    ].values[0],
                    "data_id": "",
                    "tab_type": element_details.loc[element_details.element_id == ele, "tab_type"].values[0],
                    "detailed_status": subprocess_flow[ele]["detailed_status"],
                    "redirect_status": redirect_status,
                    "run_left": run_left,
                    "run_time": run_time,
                }
            ]
        )
        flow_data = pd.concat([flow_data, transaction_element_detail], ignore_index=True)
    data_handling(request, flow_data, "Process_flow_model")
    return None
