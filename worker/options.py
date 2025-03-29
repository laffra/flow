"""
CopyRight (c) 2024 - Chris Laffra - All Rights Reserved.

This module provides a worker for a PyScript-based application to run Python
code, find dependencies, and perform code completion.
"""

import collections
import inspect
import sys

class Module():
    """ Placeholder for a module. """
    def __init__(self, name):
        self.__name__ = name

    def __getattr__(self, name):
        return Module(f"{object.__getattribute__(self, "__name__")}.{name}")

    def __str__(self):
        return self.__name__


sys.modules["pandas"] = Module("pandas")
sys.modules["duckdb"] = Module("duckdb")
sys.modules["matplotlib"] = Module("matplotlib")
sys.modules["matplotlib.pyplot"] = Module("matplotlib.pyplot")

import polyscript # pylint: disable=import-error disable=wrong-import-position
import flows # pylint: disable=wrong-import-position



def get_type_name(annotation):
    """
    Get the name of the type of a node.
    """
    if callable(annotation):
        return annotation.__name__
    return str(annotation)

def load_imports(file_path):
    """
    Load the imports from a file.
    """
    with open(file_path, encoding="utf-8") as file:
        lines = file.readlines()
        imports = []
        for line in lines:
            if line.startswith("import"):
                imports.append(line.split("import ")[1].split(" ")[0])
            elif line.startswith("from"):
                imports.append(line.split("from ")[1].split(" ")[0])
        return imports

def setup():
    """ Load the node options """
    options = collections.defaultdict(list)
    category = None
    for name, module in flows.__dict__.items():
        if hasattr(module, "__file__"):
            if module.__file__:
                packages = []
                imports = load_imports(module.__file__)
                secrets = []
                category = module.__name__.split(".")[-2]
                for function_name, function in module.__dict__.items():
                    if function_name == "packages":
                        packages = function
                    elif function_name == "secrets":
                        secrets = function
                    elif callable(function):
                        script = inspect.getsource(function)
                        signature = inspect.signature(function)
                        parameters = signature.parameters
                        inputs = [
                            ( name, get_type_name(param.annotation))
                            for name, param in parameters.items()
                        ]
                        output_type = get_type_name(signature.return_annotation)
                        options[category].append({
                            "category": category, 
                            "name": function_name,
                            "packages": packages, 
                            "secrets": secrets, 
                            "imports": imports,
                            "inputs": inputs, 
                            "output_type": get_type_name(output_type), 
                            "script": script
                        })

    polyscript.xworker.sync.publish("Worker", "Main", "options", options)

setup()
