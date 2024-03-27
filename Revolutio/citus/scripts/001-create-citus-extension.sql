-- wrap in transaction to ensure Docker flag always visible
BEGIN;
CREATE EXTENSION citus;
