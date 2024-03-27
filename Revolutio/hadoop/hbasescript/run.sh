#!/bin/bash

mkdir -p /opt/hbase-$HBASE_VERSION/data/logs
/opt/hbase-$HBASE_VERSION/bin/hbase thrift start > /opt/hbase-$HBASE_VERSION/data/logs/hbase-thrift.log 2>&1 &
/opt/hbase-$HBASE_VERSION/bin/hbase master start