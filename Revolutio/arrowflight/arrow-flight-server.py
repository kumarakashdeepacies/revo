import json
import pathlib

import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.flight
from pyarrow.lib import Codec, Table, concat_tables, schema  # noqa
import pyarrow.parquet


class FlightServer(pa.flight.FlightServerBase):

    def __init__(self, location="grpc://0.0.0.0:8815", repo=pathlib.Path("/opt/data_store"), **kwargs):
        super().__init__(location, **kwargs)
        self._location = location
        self._repo = repo

    def _make_flight_info(self, descriptor):
        asset_info = json.loads(descriptor.command)
        dataset = asset_info["path"]
        file_type = asset_info["file_type"]
        dataset_path = self._repo / dataset
        if file_type == "parquet":
            schema = pa.parquet.read_schema(dataset_path)
            metadata = pa.parquet.read_metadata(dataset_path)
            descriptor = pa.flight.FlightDescriptor.for_path(dataset.encode("utf-8"))
            endpoints = [pa.flight.FlightEndpoint(dataset, [self._location])]
            return pyarrow.flight.FlightInfo(
                schema, descriptor, endpoints, metadata.num_rows, metadata.serialized_size
            )
        elif file_type == "feather":
            schema = feather.read_table(dataset_path).schema
            metadata = schema.metadata
            descriptor = pa.flight.FlightDescriptor.for_path(dataset.encode("utf-8"))
            endpoints = [pa.flight.FlightEndpoint(dataset, [self._location])]
            return pyarrow.flight.FlightInfo(schema, descriptor, endpoints, 0, 0)
        else:
            raise ValueError(f"Mismatch in file type: {file_type}")

    def list_flights(self, context, criteria):
        for dataset in self._repo.iterdir():
            Command = {
                "path": f'{str(dataset).split("/")[-1]}',
                "file_type": f'{str(dataset).split(".")[-1]}',
            }
            descriptor = pa.flight.FlightDescriptor.for_command(json.dumps(Command))
            yield self._make_flight_info(descriptor)

    def get_flight_info(self, context, descriptor):
        return self._make_flight_info(descriptor)

    def do_put(self, context, descriptor, reader, writer):
        asset_info = json.loads(descriptor.command)
        dataset = asset_info["path"]
        dataset_path = self._repo / dataset
        data_table = reader.read_all()
        file_type = asset_info["file_type"]
        if file_type == "parquet":
            pa.parquet.write_table(data_table, dataset_path)
        elif file_type == "feather":
            feather.write_feather(data_table, dataset_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def do_get(self, context, ticket):
        dataset = ticket.ticket.decode("utf-8")
        dataset_path = self._repo / dataset
        file_type = dataset.split(".")[-1]
        if file_type == "parquet":
            return pa.flight.RecordBatchStream(pa.parquet.read_table(dataset_path))
        elif file_type == "feather":
            return pa.flight.RecordBatchStream(feather.read_table(dataset_path))
        else:
            raise ValueError(f"Mismatch in file type: {file_type}")

    def list_actions(self, context):
        return [
            ("drop_dataset", "Delete a dataset."),
        ]

    def do_action(self, context, action):
        if action.type == "drop_dataset":
            self.do_drop_dataset(action.body.to_pybytes().decode("utf-8"))
        else:
            raise NotImplementedError

    def do_drop_dataset(self, dataset):
        dataset_path = self._repo / dataset
        dataset_path.unlink()


if __name__ == "__main__":
    server = FlightServer()
    server._repo.mkdir(exist_ok=True)
    server.serve()
