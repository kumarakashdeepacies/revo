# Write parquet
import json

import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.flight

client = pa.flight.connect("grpc://arrowflight:8815")

# Write file depending on format given

# Create descriptor with file type
data_table = pa.table([["ABCD", "KJKJL", "Peach"]], names=["Character"])
Command = {"path": "uploaded.feather", "file_type": "feather"}
upload_descriptor = pa.flight.FlightDescriptor.for_command(json.dumps(Command))
writer, _ = client.do_put(upload_descriptor, data_table.schema)
writer.write_table(data_table)
writer.close()

# Retrieve metadata of newly uploaded dataset
flight = client.get_flight_info(upload_descriptor)
descriptor = flight.descriptor

# Read content of the dataset
reader = client.do_get(ticket=flight.endpoints[0].ticket)
read_table = reader.read_all()
print(read_table.to_pandas().head())

# Check list of flight datasets
for flight in client.list_flights():
    descriptor = flight.descriptor
    print(descriptor.path[0].decode("utf-8"))

# Check if a particular file is a flight

Command = {"path": "uploaded.feather", "file_type": "feather"}
upload_descriptor = pa.flight.FlightDescriptor.for_command(json.dumps(Command))
flight = client.get_flight_info(upload_descriptor)
print(flight.descriptor.path[0].decode("utf-8"))
