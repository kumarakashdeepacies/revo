import json
import logging
import multiprocessing as mp
import os
import pickle
from numpy import dtypes

import dask.dataframe as dd
import pandas as pd
import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.flight
import pyarrow.parquet as pq

from config import settings

client = pa.flight.connect("grpc://arrowflight:8815")


def to_diskstorage(
    storage_dataframe,
    storage_file_name,
    writer=None,
    schema=None,
    location="",
    metadata={},
    store_on_flight=True,
):

    # We want to use Parquet format in order to read and write. Apache Arrow has a layer that allows us to perform that activity. The storage_file_name variable should atleast be a summation of file_name+entity+model_name+date. We can discuss if we want the files to be overwritten with each run
    try:
        storage_dataframe = pa.Table.from_pandas(
            storage_dataframe, nthreads=mp.cpu_count() - 1, preserve_index=False
        )
    except Exception as e:
        logging.warning(f"Following exception ocurred - {e}")
        storage_dataframe = output_data_formatter(storage_dataframe)
        storage_dataframe = pa.Table.from_pandas(
            storage_dataframe, nthreads=mp.cpu_count() - 1, preserve_index=False
        )
    if metadata:
        data_schema = pa.schema(storage_dataframe.schema, metadata=metadata)
    else:
        data_schema = storage_dataframe.schema
    if writer is None:
        if store_on_flight:
            # Storing data in flight server
            command = {"path": f"{storage_file_name}.feather", "file_type": "feather"}
            upload_descriptor = pa.flight.FlightDescriptor.for_command(json.dumps(command))
            writer, _ = client.do_put(upload_descriptor, storage_dataframe.schema)
            for batch in storage_dataframe.to_batches(max_chunksize=20000):
                writer.write_batch(batch)
            writer.close()
        else:
            writer = pq.ParquetWriter(settings.base.DISKSTORE_PATH + storage_file_name, data_schema)
            writer.write_table(table=storage_dataframe)
            writer.close()
    return None


def filemanager_diskstorage(storage_location=None):
    # Ability to get the name of files stored in a particular location as a list
    if storage_location is None:
        storage_filenames = next(os.walk(settings.base.DISKSTORE_PATH))[2]
    else:
        storage_filenames = next(os.walk(storage_location))[2]

    return storage_filenames, storage_location


def read_diskstorage(storage_file_name, columns=None, filters=None, num_rows=None, store_on_flight=True):

    # Ability to get the name of files stored in a particular location as a list
    if store_on_flight is not True:
        storage_filenames, storage_location = filemanager_diskstorage(storage_location=None)
        if storage_file_name in storage_filenames:
            try:
                if not num_rows:
                    storage_dataframe = pq.read_table(
                        source=settings.base.DISKSTORE_PATH + storage_file_name,
                        columns=columns,
                        filters=filters,
                    ).to_pandas(use_threads=True)
                else:
                    parquet_file = pq.ParquetFile(settings.base.DISKSTORE_PATH + storage_file_name)
                    first_n_rows = next(parquet_file.iter_batches(batch_size=num_rows))
                    storage_dataframe = pa.Table.from_batches([first_n_rows]).to_pandas(use_threads=True)
            except Exception as e:
                logging.warning(f"Following exception occurred while reading data from parquet storage - {e}")
                if not num_rows:
                    storage_dataframe = pq.read_table(
                        source=storage_file_name, columns=columns, filters=filters
                    ).to_pandas(use_threads=True)
                else:
                    parquet_file = pq.ParquetFile(storage_file_name)
                    first_n_rows = next(parquet_file.iter_batches(batch_size=num_rows))
                    storage_dataframe = pa.Table.from_batches([first_n_rows]).to_pandas(use_threads=True)
        else:
            return None
        return storage_dataframe
    else:
        if not storage_file_name.endswith(".feather"):
            storage_file_name += ".feather"
        else:
            pass
        storage_dataframe = get_data_from_flight(storage_file_name, columns=columns, num_rows=num_rows)
    return storage_dataframe


def flush_diskstorage(storage_file_name):
    if check_if_file_in_flight(f"{storage_file_name}.feather"):
        pass
    elif storage_file_name + ".pickle" in filemanager_diskstorage(storage_location=None)[0]:
        os.remove(settings.base.DISKSTORE_PATH + storage_file_name + ".pickle")
    return True


def output_data_formatter(data):
    field_type = data.dtypes.apply(lambda x: x.name).to_dict()
    for col in data.columns.tolist():
        if field_type[col] == "datetime64[ns]":
            data[col] = pd.to_datetime(data[col])
        elif field_type[col] == "Object":
            data[col] = data[col].astype("object")
        elif field_type[col] in ["int64", "float64", "int32", "float32", "int", "float"]:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    return data


# Function to write data to pickle files
def to_pickle_datastorage(data, file_name, location=None):
    """
    Write data provided in a pickle file to the location
    data: Data to be stored
    file_name: Name of the pickle file
    location: storage location (optional)
    """
    if not location:
        location = settings.base.DISKSTORE_PATH
    with open(f"{location}{file_name}.pickle", "wb") as pickle_file:
        pickle.dump(data, pickle_file)
        pickle_file.close()
    return None


# Function to read data from pickle files
def read_pickle_diskstorage(file_name, location=None):
    output_data = None
    if not location:
        location = settings.base.DISKSTORE_PATH
    with open(f"{location}{file_name}.pickle", "rb") as pickle_file:
        output_data = pickle.load(pickle_file)
        pickle_file.close()
    return output_data


def computation_storage(data, data_type, file_name, location=None, metadata={}):
    if data_type == "dataframe":
        # Store in parquet file
        to_diskstorage(data, file_name, metadata=metadata)
    else:
        # Store data in pickle file as it cant be converted to parquet
        to_pickle_datastorage(data, file_name, location=location)
    return None


def file_storage_checker(file_name):
    if check_if_file_in_flight(f"{file_name}.feather"):
        return "dataframe"
    elif file_name + ".pickle" in filemanager_diskstorage(storage_location=None)[0]:
        return "exception"
    else:
        return False


def read_computation_from_storage(file_name, columns=None, filters=None, num_rows=None):
    if check_if_file_in_flight(f"{file_name}.feather"):
        file_name += ".feather"
        output_data = get_data_from_flight(file_name=file_name, num_rows=num_rows)
    elif file_name + ".pickle" in filemanager_diskstorage(storage_location=None)[0]:
        output_data = read_pickle_diskstorage(file_name)
    else:
        output_data = None
    return output_data


class parquetSchemaReader:

    def __init__(self, file_name):
        self.file_name = f"{file_name}.feather"
        self.pyarrow_file = get_file_info_from_flight(f"{file_name}.feather")

    def get_num_rows(self):
        return self.pyarrow_file.total_records

    def get_num_columns(self):
        return len(self.pyarrow_file.schema.names)

    def get_columns_list(self):
        return self.pyarrow_file.schema.names

    def get_metadata(self):
        return self.pyarrow_file.metadata

    def get_data_type_dict(self):
        arrow_schema_list = self.pyarrow_file.schema
        data_type_dict = {
            field.name: (
                field.type.to_pandas_dtype().__name__
                if field.type.to_pandas_dtype() != "datetime64[ns]" and not isinstance(field.type.to_pandas_dtype(), dtypes.DateTime64DType)
                else "datetime64[ns]"
            )
            for field in arrow_schema_list
        }
        data_type_dict = {
            key: (value.rstrip("_") if value.endswith("_") else value)
            for key, value in data_type_dict.items()
        }
        return data_type_dict


def read_data_schema_from_storage(file_name, columns=True, data_types=False):
    """
    Returns the list of columns and data types in a parquet file
    file_name: Name of the file/ element to read from
    columns (bool): To return the list of columns in the parquet file
    data_types (bool): To return the data type mapping of columns in the parquet file
    """
    list_of_columns = []
    data_type_dict = {}
    if check_computation_file_exists(file_name):
        parquet_object = parquetSchemaReader(file_name)
        if columns:
            list_of_columns = parquet_object.get_columns_list()
        else:
            pass
        if data_types:
            data_type_dict = parquet_object.get_data_type_dict()
        else:
            pass
    else:
        pass
    return list_of_columns, data_type_dict


def check_computation_file_exists(file_name):
    storage_filenames, __ = filemanager_diskstorage(storage_location=None)
    if check_if_file_in_flight(f"{file_name}.feather"):
        return True
    elif file_name + ".pickle" in storage_filenames:
        return True
    else:
        return False


def read_data_from_csv(
    file_buffer,
    output_filename,
    engine="parquet",
    engine_config={},
    chunksize=4096,
    destination="flight_server",
):
    writer = None
    Command = {"path": f"{output_filename}.feather", "file_type": "feather"}
    upload_descriptor = pa.flight.FlightDescriptor.for_command(json.dumps(Command))
    if engine_config:
        field_type = engine_config["field_type"]
        parameter_config = engine_config["parameter_config"]
    else:
        field_type = {}
        parameter_config = {}
    if engine == "pandas":
        if parameter_config.get("engine") != "pyarrow":
            if parameter_config.get("blocksize"):
                parameter_config["chunksize"] = int(parameter_config["blocksize"])
                del parameter_config["blocksize"]
            else:
                parameter_config["chunksize"] = 50000
        else:
            not_supported = ["infer_datetime_format", "blocksize", "thousands", "nrows", "dayfirst"]
            for i in not_supported:
                if parameter_config.get(i):
                    del parameter_config[i]
                else:
                    pass
        if parameter_config.get("skiprows"):
            parameter_config["skiprows"] = [int(i) for i in parameter_config["skiprows"]]
        else:
            pass
        if parameter_config.get("nrows"):
            parameter_config["nrows"] = int(parameter_config["nrows"])
        else:
            pass
        final_field_type = {}
        for field, ftype in field_type.items():
            if ftype not in ["date", "time"]:
                if ftype == "int64":
                    final_field_type[field] = "float64"
                else:
                    final_field_type[field] = ftype
            else:
                if parameter_config.get("parse_dates"):
                    if field not in parameter_config["parse_dates"]:
                        parameter_config["parse_dates"].append(field)
                    else:
                        continue
                else:
                    parameter_config["parse_dates"] = [field]
        if parameter_config.get("index_col") == False:
            parameter_config["index_col"] = None
        else:
            pass
        if parameter_config.get("chunksize"):
            data = pd.read_csv(file_buffer, dtype=final_field_type, **parameter_config)
            table_schema = None
            for chunk in data:
                next_table = pa.Table.from_pandas(chunk, schema=table_schema)
                if table_schema is None:
                    table_schema = next_table.schema
                if writer is None:
                    writer, _ = client.do_put(upload_descriptor, next_table.schema)
                writer.write_table(next_table)
            if writer is not None:
                writer.close()
            else:
                pass
        else:
            data = pd.read_csv(file_buffer, dtype=final_field_type, **parameter_config)
            next_table = pa.Table.from_pandas(data)
            if writer is None:
                writer, _ = client.do_put(upload_descriptor, next_table.schema)
            writer.write_table(next_table)
            writer.close()
    elif engine == "dask":
        writer = None
        del parameter_config["index_col"]
        if parameter_config.get("skiprows"):
            parameter_config["skiprows"] = [int(i) for i in parameter_config["skiprows"]]
        else:
            pass
        if not parameter_config.get("blocksize"):
            parameter_config["blocksize"] = 50000
        else:
            parameter_config["blocksize"] = int(parameter_config["blocksize"])

        if parameter_config.get("nrows") and parameter_config["engine"] == "pyarrow":
            del parameter_config["nrows"]
        elif parameter_config.get("nrows"):
            parameter_config["nrows"] = int(parameter_config["nrows"])
        else:
            pass
        if parameter_config.get("index_col") is False:
            parameter_config["index_col"] = None
        final_field_type = {}
        for field, ftype in field_type.items():
            if ftype not in ["date", "time"]:
                if ftype == "int64":
                    final_field_type[field] = "float64"
                else:
                    final_field_type[field] = ftype
            else:
                if parameter_config.get("parse_dates"):
                    if field not in parameter_config["parse_dates"]:
                        parameter_config["parse_dates"].append(field)
                    else:
                        continue
                else:
                    parameter_config["parse_dates"] = [field]
        parameter_config["engine"] = "python"

        data = dd.read_csv(file_buffer.temporary_file_path(), dtype=final_field_type, **parameter_config)
        table_schema = None
        for part in range(data.npartitions):
            next_chunk = data.get_partition(part)
            next_table = pa.Table.from_pandas(next_chunk.compute(), schema=table_schema)
            if table_schema is None:
                table_schema = next_table.schema
            if writer is None:
                writer, _ = client.do_put(upload_descriptor, table_schema)
            writer.write_table(next_table)
        if writer is not None:
            writer.close()
        else:
            pass
    else:
        parse_option_config = {
            k: v
            for k, v in parameter_config.items()
            if k
            in [
                "delimiter",
                "quote_char",
                "double_quote",
                "escaape_char",
                "newlines_in_values",
                "ignore_empty_lines",
                "invalid_row_hanlder",
            ]
        }
        convert_option_config = {
            k: v
            for k, v in parameter_config.items()
            if k
            in [
                "check_utf8",
                "null_values",
                "true_value",
                "false_value",
                "decimal_point",
                "strings_can_be_null",
                "quoted_strings_can_be_null",
                "timestamp_parser",
            ]
        }
        read_option_config = {
            k: v
            for k, v in parameter_config.items()
            if k
            in [
                "autogenerate_column_names",
                "block_size",
                "column_names",
                "encoding",
                "skip_rows",
                "skip_rows_after_names",
            ]
        }
        parse_options = csv.ParseOptions(**parse_option_config)

        if not read_option_config.get("block_size"):
            read_option_config["block_size"] = 30000
        else:
            read_option_config["block_size"] = int(read_option_config["block_size"])
        read_options = csv.ReadOptions(use_threads=True, **read_option_config)

        arrow_field_type = {}
        for field, ftype in field_type.items():
            if ftype == "object":
                arrow_field_type[field] = pa.string()
            elif ftype == "float64":
                arrow_field_type[field] = pa.float64()
            elif ftype == "int64":
                arrow_field_type[field] = pa.int64()
            elif ftype == "date":
                pass
            elif ftype == "time":
                pass
            elif ftype == "bool":
                arrow_field_type[field] = pa.bool_()
            else:
                arrow_field_type[field] = pa.string()
        convert_options = csv.ConvertOptions(column_types=arrow_field_type, **convert_option_config)

        with csv.open_csv(
            file_buffer,
            parse_options=parse_options,
            read_options=read_options,
            convert_options=convert_options,
        ) as reader:
            for next_chunk in reader:
                if next_chunk is None:
                    break
                if writer is None:
                    writer, _ = client.do_put(upload_descriptor, next_chunk.schema)
                next_table = pa.Table.from_batches([next_chunk])
                writer.write_table(next_table)
        if writer is not None:
            writer.close()
        else:
            pass
    return f"{output_filename}.feather"


def get_data_from_flight(file_name, columns=[], num_rows=None):
    command = {
        "path": file_name,
        "file_type": "feather",
        "batch_size": num_rows,
        "interaction_properties": {"row_limit": num_rows},
    }
    upload_descriptor = pa.flight.FlightDescriptor.for_command(json.dumps(command))
    flight = client.get_flight_info(upload_descriptor)
    reader = client.do_get(ticket=flight.endpoints[0].ticket)
    read_table = reader.read_all()
    if num_rows:
        return read_table.to_pandas().head(num_rows)
    else:
        return read_table.to_pandas()


def csv_file_field_info(file_buffer, engine_parameters=None):
    data = dd.read_csv(file_buffer.temporary_file_path(), **engine_parameters)
    field_info = data.dtypes.apply(lambda x: x.name).to_dict()
    return field_info


def check_if_file_in_flight(file_name):
    command = {"path": file_name, "file_type": "feather"}
    upload_descriptor = pa.flight.FlightDescriptor.for_command(json.dumps(command))
    try:
        client.get_flight_info(upload_descriptor)
    except Exception as e:
        logging.warning(f"Error while reading data from flight - {e}")
        return False
    else:
        return True


def get_file_info_from_flight(file_name):
    command = {"path": file_name, "file_type": "feather"}
    upload_descriptor = pa.flight.FlightDescriptor.for_command(json.dumps(command))
    flight = client.get_flight_info(upload_descriptor)
    return flight
