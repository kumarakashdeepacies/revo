## Code for saving the flowchart structure for computation manager
from kore_investment.users.computations.db_centralised_function import read_data_func


def save_flowchart_config(xml):

    ##Inititalisation of variables

    elementList = []
    connectors = []
    connected_nodes = []
    finalElements = []

    ## Processing the flowchart xml dictionary
    for i in xml["mxGraphModel"]["root"]["mxCell"]:
        elementDict = {}
        elementDict = {"id": i["@id"]}
        if "@value" in i.keys():
            if i["@value"].find("&nbsp;&nbsp;") >= 0:
                elementDict["text"] = i["@value"][
                    i["@value"].find("&nbsp;&nbsp;") + 12 : i["@value"].find("</h5>")
                ]
            elif i["@value"] == "Port":
                elementDict["text"] = "Port"
                elementDict["parent"] = i["@parent"]
            else:
                if "@source" in i.keys() and "@target" in i.keys():
                    elementDict["text"] = "Connector"
                    elementDict["source_port"] = i["@source"]
                    elementDict["target_port"] = i["@target"]
                    connectDict = {"source": i["@source"], "target": i["@target"]}
                    connectors.append(connectDict)
            if i["@value"].find("span") >= 0:
                elementDict["element_id"] = i["@value"][
                    i["@value"].find("span") + 12 : i["@value"].find('"></span')
                ]
            else:
                elementDict["element_id"] = "#"
        elementList.append(elementDict)

    for j in connectors:
        connections = {}
        for k in elementList:
            if "text" in k.keys():
                if k["text"] == "Port":
                    if k["id"] == j["source"]:
                        connections["source"] = k["parent"]
                    if k["id"] == j["target"]:
                        connections["target"] = k["parent"]
        connected_nodes.append(connections)

    ## Creating the final json that will be used in rendering
    temp_element_list = []
    g_var_element_list = []
    export_element_list = []
    for i in elementList:
        finalDict = {}
        parent = []
        child = []
        finalDict["element_id"] = "#"
        if "element_id" in i.keys():
            finalDict["element_id"] = i["element_id"]
        if "text" in i.keys():
            finalDict["text"] = i["text"]
        for j in connected_nodes:
            if j["target"] == i["id"]:
                parent.append(j["source"])
            if j["source"] == i["id"]:
                child.append(j["target"])
        if len(parent) > 0:
            finalparentIDS = [k["element_id"] for k in elementList if k["id"] in parent]
            finalDict["parent"] = finalparentIDS
        else:
            finalDict["parent"] = "#"
        if len(child) > 0:
            finalchildIDS = [k["element_id"] for k in elementList if k["id"] in child]
            finalDict["child"] = finalchildIDS
        else:
            finalDict["child"] = "#"
        if finalDict["element_id"] != "#":
            parent_exists = True
            if finalDict["text"] not in ["Global Variable", "Export Data"]:
                if finalDict["parent"] != "#":
                    eixtsing_ele = [ele["element_id"] for ele in finalElements]
                    for p in finalDict["parent"]:
                        if p not in eixtsing_ele:
                            parent_exists = False
                            break
                if parent_exists:
                    finalElements.append(finalDict)
                else:
                    temp_element_list.append(finalDict)
            elif finalDict["text"] == "Export Data":
                export_element_list.append(finalDict)
            else:
                g_var_element_list.append(finalDict)

    if len(temp_element_list):
        while len(temp_element_list) > 0:
            for idx, temp in enumerate(temp_element_list):
                parent_exists = True
                if temp["parent"] != "#":
                    eixtsing_ele = [ele["element_id"] for ele in finalElements]
                    for p in temp["parent"]:
                        if p not in eixtsing_ele:
                            parent_exists = False
                if parent_exists:
                    finalElements.append(temp)
                    del temp_element_list[idx]
    finalElements = g_var_element_list + finalElements + export_element_list
    return finalElements


def save_flowchart_config_connect(xml, request):

    ##Inititalisation of variables
    elementList = []
    connectors = []
    finalElements = []
    ## Processing the flowchart xml dictionary
    for i in xml["mxGraphModel"]["root"]["mxCell"]:
        elementDict = {}
        elementDict = {"id": i["@id"]}
        if "@value" not in i.keys():
            if "@source" in i.keys() and "@target" in i.keys():
                elementDict["text"] = "Connector"
                elementDict["source_port"] = i["@source"]
                elementDict["target_port"] = i["@target"]
                connectDict = {"source": i["@source"], "target": i["@target"], "style": i["@style"]}
                connectors.append(connectDict)
        if i["@id"].__contains__("flow"):
            if "@source" in i.keys() and "@target" in i.keys():
                elementDict["text"] = "Connector"
                elementDict["source_port"] = i["@source"]
                elementDict["target_port"] = i["@target"]
                connectDict = {"source": i["@source"], "target": i["@target"], "style": i["@style"]}
                connectors.append(connectDict)
        elif i.get("@style"):
            if i["@style"].__contains__("flow"):
                if "@source" in i.keys() and "@target" in i.keys():
                    elementDict["text"] = "Connector"
                    elementDict["source_port"] = i["@source"]
                    elementDict["target_port"] = i["@target"]
                    connectDict = {"source": i["@source"], "target": i["@target"], "style": i["@style"]}
                    connectors.append(connectDict)
        elementList.append(elementDict)

    # ## Creating the final json that will be used in rendering
    finalElements = []
    for i in xml["mxGraphModel"]["root"]["mxCell"]:
        childElements = []
        element_id = []
        tab_header = []
        if len(connectors) > 0:
            finalDict = {}
            for k in connectors:
                if k["source"] == i["@id"] and i["@value"] == "Create View":
                    finalDict["parent"] = i["@id"]
                    for j in xml["mxGraphModel"]["root"]["mxCell"]:
                        if j["@id"] == k["target"] and j["@value"] == "List View":
                            childElements.append(j["@id"])
                            element_id.append(
                                i["@style"].split("shapeUniqueID")[1].replace("=", "").replace(";", "")
                            )
                    finalDict["child"] = childElements
                    for e in element_id:
                        th = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "TabScreens",
                                    "Columns": ["tab_header_name"],
                                },
                                "condition": [
                                    {
                                        "column_name": "element_id",
                                        "condition": "Equal to",
                                        "input_value": e,
                                        "and_or": "",
                                    }
                                ],
                            },
                        )["tab_header_name"].tolist()
                        tab_header.append(th)
                    finalDict["element_id"] = element_id
                    finalDict["tab_header"] = tab_header
                    finalElements.append(finalDict)

    return finalElements


def get_parent_child(xml, request):
    elementList = []
    connectors = []
    finalElements = []
    table_dic = {}
    ## Processing the flowchart xml dictionary
    for i in xml["mxGraphModel"]["root"]["mxCell"]:
        elementDict = {}
        elementDict = {"id": i["@id"]}
        if "@value" not in i.keys():
            if "@source" in i.keys() and "@target" in i.keys():
                elementDict["text"] = "Connector"
                elementDict["source_port"] = i["@source"]
                elementDict["target_port"] = i["@target"]
                connectDict = {"source": i["@source"], "target": i["@target"], "style": i["@style"]}
                connectors.append(connectDict)
        if i["@id"].__contains__("flow"):
            if "@source" in i.keys() and "@target" in i.keys():
                elementDict["text"] = "Connector"
                elementDict["source_port"] = i["@source"]
                elementDict["target_port"] = i["@target"]
                connectDict = {"source": i["@source"], "target": i["@target"], "style": i["@style"]}
                connectors.append(connectDict)
        elif i.get("@style"):
            if i["@style"].__contains__("flow"):
                if "@source" in i.keys() and "@target" in i.keys():
                    elementDict["text"] = "Connector"
                    elementDict["source_port"] = i["@source"]
                    elementDict["target_port"] = i["@target"]
                    connectDict = {"source": i["@source"], "target": i["@target"], "style": i["@style"]}
                    connectors.append(connectDict)
        elementList.append(elementDict)

    # ## Creating the final json that will be used in rendering
    finalElements = []
    for i in xml["mxGraphModel"]["root"]["mxCell"]:
        childElements = []
        element_id = []
        if len(connectors) > 0:
            finalDict = {}
            for k in connectors:
                if k["source"] == i["@id"]:
                    finalDict["parent"] = i["@id"]
                    for j in xml["mxGraphModel"]["root"]["mxCell"]:
                        if j["@id"] == k["target"]:
                            childElements.append(j["@id"])
                            if len(i["@style"].split("shapeUniqueID")) > 1:
                                single_element_id = (
                                    i["@style"].split("shapeUniqueID")[1].replace("=", "").replace(";", "")
                                )
                            else:
                                single_element_id = ""
                            element_id.append(single_element_id)
                            data = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "TabScreens",
                                        "Columns": ["table_name"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "element_id",
                                            "condition": "Equal to",
                                            "input_value": single_element_id,
                                            "and_or": "",
                                        },
                                    ],
                                },
                            )
                            if not data.empty:
                                table_dic[single_element_id] = data.iloc[0]["table_name"]
                    finalDict["child"] = childElements
                    finalDict["element_id"] = element_id
                    finalDict["table"] = table_dic
                    finalElements.append(finalDict)
    return finalElements


def get_child(xml, request):
    elementList = []
    connectors = []
    finalElements = []
    table_dic = {}
    ## Processing the flowchart xml dictionary
    for i in xml["mxGraphModel"]["root"]["mxCell"]:
        elementDict = {}
        elementDict = {"id": i["@id"]}
        if "@value" not in i.keys():
            if "@source" in i.keys() and "@target" in i.keys():
                elementDict["text"] = "Connector"
                elementDict["source_port"] = i["@source"]
                elementDict["target_port"] = i["@target"]
                connectDict = {"source": i["@source"], "target": i["@target"], "style": i["@style"]}
                connectors.append(connectDict)
        if i["@id"].__contains__("flow"):
            if "@source" in i.keys() and "@target" in i.keys():
                elementDict["text"] = "Connector"
                elementDict["source_port"] = i["@source"]
                elementDict["target_port"] = i["@target"]
                connectDict = {"source": i["@source"], "target": i["@target"], "style": i["@style"]}
                connectors.append(connectDict)
        elif i.get("@style"):
            if i["@style"].__contains__("flow"):
                if "@source" in i.keys() and "@target" in i.keys():
                    elementDict["text"] = "Connector"
                    elementDict["source_port"] = i["@source"]
                    elementDict["target_port"] = i["@target"]
                    connectDict = {"source": i["@source"], "target": i["@target"], "style": i["@style"]}
                    connectors.append(connectDict)
        elementList.append(elementDict)

    # ## Creating the final json that will be used in rendering
    finalElements = []
    for i in xml["mxGraphModel"]["root"]["mxCell"]:
        childElements = []
        element_id = []
        childElementsName = []
        if len(connectors) > 0:
            finalDict = {}
            for k in connectors:
                if k["target"] == i["@id"]:
                    finalDict["parent"] = i["@id"]
                    for j in xml["mxGraphModel"]["root"]["mxCell"]:
                        if j["@id"] == k["source"]:
                            childElements.append(j["@id"])
                            if len(i["@style"].split("shapeUniqueID")) > 1:
                                single_element_id = (
                                    i["@style"].split("shapeUniqueID")[1].replace("=", "").replace(";", "")
                                )
                            else:
                                single_element_id = ""
                            element_id.append(single_element_id)
                            data = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "TabScreens",
                                        "Columns": ["table_name", "tab_header_name", "computation_name"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "element_id",
                                            "condition": "Equal to",
                                            "input_value": single_element_id,
                                            "and_or": "",
                                        },
                                    ],
                                },
                            )
                            if data.empty:
                                childElementsName.append("")
                                table_dic[single_element_id] = ""
                            else:
                                if single_element_id.__contains__("paralle"):
                                    childElementsName.append(data.iloc[0]["computation_name"])
                                else:
                                    childElementsName.append(data.iloc[0]["tab_header_name"])
                                table_dic[single_element_id] = data.iloc[0]["table_name"]
                    finalDict["child"] = childElements
                    finalDict["element_id"] = element_id
                    finalDict["table"] = table_dic
                    finalDict["childName"] = childElementsName
                    finalElements.append(finalDict)
    return finalElements
