import json
from typing import List
from pydantic import BaseModel, ValidationError


class RPCMethod(BaseModel):
    name: str
    argument_types: List[str]
    return_types: List[str]


class RPCDefinition(BaseModel):
    symbol_path: str
    methods: List[RPCMethod]


def validate_rpc_definitions(payload, silent=False):
    try:
        return [RPCDefinition(**rpc_definition) for rpc_definition in payload]
    except ValidationError as e:
        if not silent:
            print(e)
            schema_file_name = "rpc_definitions_schema.json"
            with open(schema_file_name, 'w') as file:
                json.dump(RPCDefinition.model_json_schema(), file, indent=4)
            print(f"Schema file {schema_file_name} created to help in the creation of the rpc definition file.")
