import re

from currency_symbols import CurrencySymbols
from pybaht import bahttext


class TextFunctions:
    def bahttextfunc(self, dataframe, new_col_name, colname):
        dataframe[new_col_name] = dataframe[colname].map(lambda x: bahttext(x), na_action="ignore")
        return dataframe

    def lowerfunc(self, dataframe, colname):
        if dataframe[colname].dtype == "object":
            dataframe[colname] = dataframe[colname].map(lambda x: x.lower(), na_action="ignore")
        return dataframe

    def properfunc(self, dataframe, colname):
        if dataframe[colname].dtype == "object":
            dataframe[colname] = dataframe[colname].map(lambda x: x.capitalize(), na_action="ignore")
        return dataframe

    def upperfunc(self, dataframe, colname):
        if dataframe[colname].dtype == "object":
            dataframe[colname] = dataframe[colname].map(lambda x: x.upper(), na_action="ignore")
        return dataframe

    def lenfunc(self, dataframe, new_col_name, colname):
        dataframe[new_col_name] = dataframe[colname].map(lambda x: len(str(x)), na_action="ignore")
        return dataframe

    def charfunc(self, dataframe, new_col_name, colname):
        if dataframe[colname].dtype in ["float64", "float32", "float", "int", "int32", "int64"]:
            dataframe[new_col_name] = dataframe[colname].map(
                lambda x: chr(int(x)) if (0 < x < 256) else None, na_action="ignore"
            )
        return dataframe

    def unicodefunc(self, dataframe, new_col_name, colname):
        y = dataframe[colname].astype(str)
        dataframe[new_col_name] = y.map(lambda x: ord(x[0]), na_action="ignore")
        return dataframe

    def leftfunc(self, dataframe, number, new_col_name, colname):
        dataframe[new_col_name] = dataframe[colname].map(lambda x: (str(x)[0:number]), na_action="ignore")
        return dataframe

    def rightfunc(self, dataframe, number, new_col_name, colname):
        dataframe[new_col_name] = dataframe[colname].map(
            lambda x: (str(x)[len(str(x)) - number : len(str(x))]), na_action="ignore"
        )
        return dataframe

    def midfunc(self, dataframe, start, number, new_col_name, colname):
        dataframe[new_col_name] = dataframe[colname].map(
            lambda x: (str(x)[start - 1 : number + start - 1]), na_action="ignore"
        )
        return dataframe

    def exactfunc(self, dataframe, new_col_name, colname1, colname2):
        dataframe[new_col_name] = dataframe[colname1].eq(dataframe[colname2])
        return dataframe

    def unicharfunc(self, dataframe, new_col_name, colname):
        if dataframe[colname].dtype in ["float64", "float32", "float", "int", "int32", "int64"]:
            dataframe[new_col_name] = dataframe[colname].map(lambda x: chr(int(x)), na_action="ignore")
        return dataframe

    def reptfunc(self, dataframe, number, new_col_name, colname):
        dataframe[new_col_name] = dataframe[colname].map(lambda x: str(x) * number, na_action="ignore")
        return dataframe

    def findfunc(self, dataframe, substr, new_col_name, colname):
        dataframe[new_col_name] = dataframe[colname].map(
            lambda x: (str(x).find(substr) + 1), na_action="ignore"
        )
        return dataframe

    def searchfunc(self, dataframe, substr, new_col_name, colname):
        y = dataframe[colname].astype(str)
        dataframe[new_col_name] = y.map(lambda x: ((x.upper()).find(substr.upper()) + 1), na_action="ignore")
        return dataframe

    def replacefunc(self, dataframe, substr, index, no_chars, colname):
        dataframe[colname] = dataframe[colname].map(
            lambda x: str(x).replace(str(x)[index - 1 : index - 1 + no_chars], substr), na_action="ignore"
        )
        return dataframe

    def trimfunc(self, dataframe, colname):
        if dataframe[colname].dtype == "object":
            dataframe[colname] = dataframe[colname].map(lambda x: x.strip(), na_action="ignore")
        return dataframe

    def codefunc(self, dataframe, new_col_name, colname):
        y = dataframe[colname].astype(str)
        dataframe[new_col_name] = y.map(lambda x: ord(x[0]) if (x[0].isascii()) else None, na_action="ignore")
        return dataframe

    def cleanfunc(self, dataframe, colname):
        if dataframe[colname].dtype == "object":
            dataframe[colname] = dataframe[colname].map(
                lambda x: x.encode("ascii", "ignore").decode("ascii"), na_action="ignore"
            )
        return dataframe

    def valuetotextfunc(self, dataframe, format_num, colname):
        if dataframe[colname].dtype == "object":
            dataframe[colname] = dataframe[colname].astype(str)
            if format_num == 0:
                pass
            elif format_num == 1:
                dataframe[colname] = dataframe[colname].map(lambda x: f'"{x}"', na_action="ignore")
        else:
            dataframe[colname] = dataframe[colname].astype(str)
        return dataframe

    def substitutefunc(self, dataframe, substr, replacement, instance, colname):
        dataframe[colname] = dataframe[colname].astype(str)
        for i in range(len(dataframe)):
            x = [
                s
                for s in range(len(dataframe.loc[i, colname]))
                if dataframe.loc[i, colname].startswith(substr, s)
            ]
            if instance == None:
                dataframe.loc[i, colname] = dataframe.loc[i, colname].replace(substr, replacement)
            elif instance <= 0:
                dataframe.loc[i, colname] = ""
            elif instance > len(x):
                dataframe.loc[i, colname] = dataframe.loc[i, colname]
            else:
                position = x[instance - 1]
                dataframe.loc[i, colname] = (
                    dataframe.loc[i, colname][:position]
                    + replacement
                    + dataframe.loc[i, colname][position + 1 :]
                )
        dataframe[colname] = dataframe[colname].str.replace("nan", "-")
        return dataframe

    def tfunc(self, dataframe, colname):
        if dataframe[colname].dtype == "object":
            dataframe[colname] = dataframe[colname].map(lambda x: x, na_action="ignore")
        else:
            dataframe[colname] = dataframe[colname].map(lambda x: "", na_action="ignore")
        return dataframe

    def numbervaluefunc(self, dataframe, dec_sep, grp_sep, colname):
        def nv(x, dec_sep, grp_sep):
            find = re.findall(r"[^0-9]", x)
            list1 = []
            for val in x:
                if val == dec_sep or val == grp_sep:
                    list1.append(val)
            if len(list1) == len(find):
                x = x.replace(dec_sep, ".")
                x = x.replace(grp_sep, "")
            else:
                x = 0
            x = float(x)
            x = round(x, 1)
            return x

        if dataframe[colname].dtype == "object":
            dataframe[colname] = dataframe[colname].map(lambda x: nv(x, dec_sep, grp_sep), na_action="ignore")
        return dataframe

    def valuefunc(self, dataframe, colname):
        def v(x):
            find = re.search("[^0-9,.]", x)
            if find == None:
                x = re.sub(",", "", x)
            else:
                x = 0
            x = float(x)
            return x

        if dataframe[colname].dtype == "object":
            dataframe[colname] = dataframe[colname].map(lambda x: v(x), na_action="ignore")
        return dataframe

    def textjoinfunc(self, dataframe, delimiter, new_col_name, colname1, colname2, colname3=None):
        if colname3 == None:
            x1 = dataframe[colname1].astype(str)
            x2 = dataframe[colname2].astype(str)
            dataframe[new_col_name] = x1 + delimiter + x2
        else:
            x1 = dataframe[colname1].astype(str)
            x2 = dataframe[colname2].astype(str)
            x3 = dataframe[colname3].astype(str)
            dataframe[new_col_name] = x1 + delimiter + x2 + delimiter + x3
        return dataframe

    def textafterfunc(self, dataframe, substr, match_mode, instance, new_col_name, colname):
        def ta(x, substr, match_mode, instance):
            x = str(x)
            sub = []
            for val in substr:
                y = re.escape(val)
                sub.append(y)
                substr = "|".join(sub)
            if substr == "":
                x = x
            else:
                x = x.lower()
                if match_mode == 1:
                    match_list = re.findall(substr, x, re.IGNORECASE)
                    a = [m.lower() for m in match_list]
                    l1 = list(set(a))
                    if len(l1) == 0:
                        x = ""
                    else:
                        l = len(l1)
                        s = l1[l - 1]
                        k = len(s)
                        w = [p for p in range(len(x)) if x.startswith(s, p)]
                        if instance < 0:
                            instance *= -1
                            if instance > len(w):
                                x = ""
                            else:
                                w[0] += k - 1
                                position = w[instance - 1]
                                x = x[position + 1 :]
                        elif instance == 0:
                            x = ""
                        else:
                            if instance > len(w):
                                x = ""
                            else:
                                w[0] += k - 1
                                position = w[instance - 1]
                                x = x[position + 1 :]
                elif match_mode == 0:
                    match_list = re.findall(substr, x, re.IGNORECASE)
                    l1 = list(set(match_list))
                    if len(l1) == 0:
                        x = ""
                    else:
                        l = len(l1)
                        s = l1[l - 1]
                        k = len(s)
                        w = [p for p in range(len(x)) if x.startswith(s, p)]
                        if instance < 0:
                            instance *= -1
                            if instance > len(w):
                                x = ""
                            else:
                                w[0] += k - 1
                                position = w[instance - 1]
                                x = x[position + 1 :]
                        elif instance == 0:
                            x = ""
                        else:
                            if instance > len(w):
                                x = ""
                            else:
                                w[0] += k - 1
                                position = w[instance - 1]
                                x = x[position + 1 :]
                else:
                    x = ""
            return x

        dataframe[new_col_name] = dataframe[colname].map(
            lambda x: ta(x, substr, match_mode, instance), na_action="ignore"
        )
        return dataframe

    def textbeforefunc(self, dataframe, substr, match_mode, instance, new_col_name, colname):
        def tb(x, substr, match_mode, instance):
            x = str(x)
            sub = []
            for val in substr:
                y = re.escape(val)
                sub.append(y)
            substr = "|".join(sub)
            if substr == "":
                x = x
            else:
                x = x.lower()
                if match_mode == 1:
                    match_list = re.findall(substr, x, re.IGNORECASE)
                    a = [m.lower() for m in match_list]
                    l1 = list(set(a))
                    if len(l1) != 0:
                        s = l1[0]
                        w = [p for p in range(len(x)) if x.startswith(s, p)]
                        if instance < 0:
                            if instance > len(w):
                                x = ""
                            else:
                                position = w[instance + len(w)]
                                x = x[:position]
                        elif instance == 0:
                            x = ""
                        else:
                            if instance > len(w):
                                x = ""
                            else:
                                position = w[instance - 1]
                                x = x[:position]
                    else:
                        x = ""
                elif match_mode == 0:
                    match_list = re.findall(substr, x)
                    l1 = list(set(match_list))
                    if len(l1) != 0:
                        s = l1[0]
                        w = [p for p in range(len(x)) if x.startswith(s, p)]
                        if instance < 0:
                            if instance > len(w):
                                x = ""
                            else:
                                position = w[instance + len(w)]
                                x = x[:position]
                        elif instance == 0:
                            x = ""
                        else:
                            if instance > len(w):
                                x = ""
                            else:
                                position = w[instance - 1]
                                x = x[:position]
                    else:
                        x = ""
                else:
                    x = ""
            return x

        dataframe[new_col_name] = dataframe[colname].map(
            lambda x: tb(x, substr, match_mode, instance), na_action="ignore"
        )
        return dataframe

    def fixedfunc(self, dataframe, decimal, no_commas, colname):
        def ff(x, decimal, no_commas):
            if no_commas == True and decimal == None:
                x = round(x, 2)
                x = re.sub(r"(\d{3})(?=\d)", r"\1,", str(x)[::-1])[::-1]
                x = x.lstrip()
            elif no_commas == True:
                x = round(x, decimal)
                x = re.sub(r"(\d{3})(?=\d)", r"\1,", str(x)[::-1])[::-1]
                x = x.lstrip()
            else:
                x = round(x, decimal)
                x = str(x)
                x = x.lstrip()
            return x

        if dataframe[colname].dtype in ["float64", "float32", "float", "int64", "int32", "int"]:
            dataframe[colname] = dataframe[colname].map(
                lambda x: ff(x, decimal, no_commas), na_action="ignore"
            )
        return dataframe

    def dollarfunc(self, dataframe, decimal, currency, colname):
        def df(x, decimal, currency):
            dollarSymbol = CurrencySymbols.get_symbol(currency)
            x = round(x, decimal)
            x = re.sub(r"(\d{3})(?=\d)", r"\1,", str(x)[::-1])[::-1]
            x = x.lstrip()
            x = dollarSymbol + x
            return x

        if dataframe[colname].dtype in ["float64", "float32", "float", "int64", "int32", "int"]:
            dataframe[colname] = dataframe[colname].map(
                lambda x: df(x, decimal, currency), na_action="ignore"
            )
        return dataframe

    def arraytotextfunc(self, dataframe, form, new_col_name, colname):
        if form == 0:
            dataframe["New"] = dataframe[colname].astype(str)
            dataframe["New"] = dataframe[colname].fillna("")
            list1 = dataframe["New"].tolist()
            string = ",".join(list1)
            dataframe.loc[0, new_col_name] = string
        elif form == 1:
            dataframe["New"] = dataframe[colname].astype(str)
            dataframe["New"] = dataframe["New"].fillna("")
            list1 = dataframe["New"].tolist()
            string = ";".join(list1)
            dataframe.loc[0, new_col_name] = f"[{string}]"
        else:
            pass
        dataframe = dataframe.drop("New", axis=1)
        return dataframe

    def textfunc(self, dataframe, formattext, colname):
        def text(x, formattext):
            x = str(x)
            list1 = []
            list2 = []
            list3 = []
            string1 = ""
            string2 = ""
            for val in formattext:
                if val == "#":
                    string1 += "{}"
                    list1.append("{}")
                    list2.append("{}")
                    list3.append("{}")
                    string2 += "{}"
                else:
                    string1 += val
                    string2 += val
                    list2.append(val)
            if len(list1) == len(x):
                x = string1.format(*x)
            elif len(list1) > len(x):
                b = len(list3) - len(x)
                n = 0
                for y in list2:
                    if y == "{}":
                        while n < b:
                            list2.remove(y)
                            n += 1
                final_string = "".join(list2)
                x = final_string.format(*x)
            else:
                p = [s for s in x]
                n = 0
                b = len(x) - len(list3)
                for val in p:
                    while n < b:
                        p[0] = p[0] + p[1]
                        p.pop(1)
                        n += 1
                x = string2.format(*p)
            return x

        dataframe[colname] = dataframe[colname].map(lambda x: text(x, formattext), na_action="ignore")
        return dataframe

    def textsplitfunc(self, dataframe, col_delimiter, row_delimiter, match_mode, new_col_name, colname):
        col = []
        row = []
        for val in col_delimiter:
            y = re.escape(val)
            col.append(y)
        col_delimiter = "|".join(col)
        for val in row_delimiter:
            y = re.escape(val)
            row.append(y)
        row_delimiter = "|".join(row)
        new_col_name.insert(0, colname)
        dataframe[colname] = dataframe[colname].astype(str)

        def col_split(dataframe, new_col_name, colname):
            if match_mode == 1:
                for val in col_delimiter:
                    val = val.lower()
                dataframe[colname] = dataframe[colname].str.lower()
                dataframe[new_col_name] = dataframe[colname].str.split(col_delimiter, expand=True)
            elif match_mode == 0:
                dataframe[new_col_name] = dataframe[colname].str.split(col_delimiter, expand=True)
            else:
                pass
            return dataframe

        def row_split(dataframe, colname):
            list2 = []
            if match_mode == 1:
                dataframe[colname] = dataframe[colname].str.lower()
                for val in row_delimiter:
                    val = val.lower()
                for i in range(len(dataframe)):
                    x = re.split(row_delimiter, dataframe.loc[i, colname])
                    list2.append(x)
                dataframe[colname] = list2
                dataframe = dataframe.explode(colname)
            elif match_mode == 0:
                for i in range(len(dataframe)):
                    x = re.split(row_delimiter, dataframe.loc[i, colname])
                    list2.append(x)
                dataframe[colname] = list2
                dataframe = dataframe.explode(colname)
            else:
                pass
            return dataframe

        if col_delimiter == "" and row_delimiter == "":
            pass
        elif col_delimiter != "" and row_delimiter == "":
            dataframe = col_split(dataframe, new_col_name, colname)
        elif col_delimiter == "" and row_delimiter != "":
            dataframe = row_split(dataframe, colname)
        else:
            if col_delimiter == row_delimiter:
                dataframe = col_split(dataframe, new_col_name, colname)
            else:
                dataframe = row_split(dataframe, colname)
                dataframe = col_split(dataframe, new_col_name, colname)
        return dataframe


def Apply_Text_Functions(dataframe, config_dict):
    Ops_TextFunc = TextFunctions()
    if config_dict["function"] == "bahttextfunc":
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.bahttextfunc(dataframe, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "lowerfunc":
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.lowerfunc(dataframe, colname)
        return output_data
    elif config_dict["function"] == "properfunc":
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.properfunc(dataframe, colname)
        return output_data
    elif config_dict["function"] == "upperfunc":
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.upperfunc(dataframe, colname)
        return output_data
    elif config_dict["function"] == "lenfunc":
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.lenfunc(dataframe, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "charfunc":
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.charfunc(dataframe, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "unicodefunc":
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.unicodefunc(dataframe, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "leftfunc":
        number = config_dict["inputs"]["number"]
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.leftfunc(dataframe, number, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "rightfunc":
        number = config_dict["inputs"]["number"]
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.rightfunc(dataframe, number, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "midfunc":
        start = config_dict["inputs"]["start"]
        number = config_dict["inputs"]["number"]
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.midfunc(dataframe, start, number, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "exactfunc":
        colname1 = config_dict["inputs"]["colname1"]
        colname2 = config_dict["inputs"]["colname2"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.exactfunc(dataframe, new_col_name, colname1, colname2)
        return output_data
    elif config_dict["function"] == "unicharfunc":
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.unicharfunc(dataframe, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "reptfunc":
        number = config_dict["inputs"]["number"]
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.reptfunc(dataframe, number, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "findfunc":
        substr = config_dict["inputs"]["substr"]
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.findfunc(dataframe, substr, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "searchfunc":
        substr = config_dict["inputs"]["substr"]
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.searchfunc(dataframe, substr, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "replacefunc":
        substr = config_dict["inputs"]["substr"]
        index = config_dict["inputs"]["index"]
        no_chars = config_dict["inputs"]["no_chars"]
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.replacefunc(dataframe, substr, index, no_chars, colname)
        return output_data
    elif config_dict["function"] == "trimfunc":
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.trimfunc(dataframe, colname)
        return output_data
    elif config_dict["function"] == "codefunc":
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.codefunc(dataframe, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "cleanfunc":
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.cleanfunc(dataframe, colname)
        return output_data
    elif config_dict["function"] == "valuetotextfunc":
        format_num = config_dict["inputs"]["format_num"]
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.valuetotextfunc(dataframe, format_num, colname)
        return output_data
    elif config_dict["function"] == "substitutefunc":
        substr = config_dict["inputs"]["substr"]
        replacement = config_dict["inputs"]["replacement"]
        instance = config_dict["inputs"]["instance"]
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.substitutefunc(dataframe, substr, replacement, instance, colname)
        return output_data
    elif config_dict["function"] == "tfunc":
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.tfunc(dataframe, colname)
        return output_data
    elif config_dict["function"] == "numbervaluefunc":
        dec_sep = config_dict["inputs"]["dec_sep"]
        grp_sep = config_dict["inputs"]["grp_sep"]
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.numbervaluefunc(dataframe, dec_sep, grp_sep, colname)
        return output_data
    elif config_dict["function"] == "valuefunc":
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.valuefunc(dataframe, colname)
        return output_data
    elif config_dict["function"] == "textjoinfunc":
        delimiter = config_dict["inputs"]["delimiter"]
        colname1 = config_dict["inputs"]["colname1"]
        colname2 = config_dict["inputs"]["colname2"]
        colname3 = config_dict["inputs"]["colname3"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.textjoinfunc(
            dataframe, delimiter, new_col_name, colname1, colname2, colname3
        )
        return output_data
    elif config_dict["function"] == "textafterfunc":
        substr = config_dict["inputs"]["substr"]
        match_mode = config_dict["inputs"]["match_mode"]
        instance = config_dict["inputs"]["instance"]
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.textafterfunc(
            dataframe, substr, match_mode, instance, new_col_name, colname
        )
        return output_data
    elif config_dict["function"] == "textbeforefunc":
        substr = config_dict["inputs"]["substr"]
        match_mode = config_dict["inputs"]["match_mode"]
        instance = config_dict["inputs"]["instance"]
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.textbeforefunc(
            dataframe, substr, match_mode, instance, new_col_name, colname
        )
        return output_data
    elif config_dict["function"] == "fixedfunc":
        decimal = config_dict["inputs"]["decimal"]
        no_commas = config_dict["inputs"]["no_commas"]
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.fixedfunc(dataframe, decimal, no_commas, colname)
        return output_data
    elif config_dict["function"] == "dollarfunc":
        decimal = config_dict["inputs"]["decimal"]
        currency = config_dict["inputs"]["currency"]
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.dollarfunc(dataframe, decimal, currency, colname)
        return output_data
    elif config_dict["function"] == "arraytotextfunc":
        form = config_dict["inputs"]["form"]
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.arraytotextfunc(dataframe, form, new_col_name, colname)
        return output_data
    elif config_dict["function"] == "textfunc":
        formattext = config_dict["inputs"]["formattext"]
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_TextFunc.textfunc(dataframe, formattext, colname)
        return output_data
    elif config_dict["function"] == "textsplitfunc":
        col_delimiter = config_dict["inputs"]["col_delimiter"]
        row_delimiter = config_dict["inputs"]["row_delimiter"]
        match_mode = config_dict["inputs"]["match_mode"]
        colname = config_dict["inputs"]["colname"]
        new_col_name = config_dict["inputs"]["new_col_name"]
        output_data = Ops_TextFunc.textsplitfunc(
            dataframe, col_delimiter, row_delimiter, match_mode, new_col_name, colname
        )
        return output_data
    else:
        pass
