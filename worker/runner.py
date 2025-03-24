"""
CopyRight (c) 2024 - Chris Laffra - All Rights Reserved.

This module provides a worker for a PyScript-based application to run Python
code, find dependencies, and perform code completion.
"""

import ast
import json
import time

import polyscript # pylint: disable=import-error

state = {}
state.update(globals())
state.update({
    "print": lambda *args: publish("print", " ".join(map(str, args)))
})

class Runner():
    """ Runner class for running Python code. """

    def __init__(self, key, script, inputs):
        """ Runs the script. """
        self.start = time.time()
        self.key = key
        print("="*30)
        print(script)
        print("="*30)
        self.script = self.intercept_last_expression(key, script)
        self.inputs = inputs

    def run(self):
        """ Runs the script. """
        try:
            exec(self.script, state, state) # pylint: disable=exec-used
            publish("result", [self.key, str(state[self.key])])
        except Exception as e: # pylint: disable=broad-exception-caught
            lineno = e.__traceback__.tb_lineno
            publish("error", [self.key, f"Line {lineno}, {type(e).__name__}: {e}"])
            print(e)

    def intercept_last_expression(self, key, script):
        """ Assigns the last expression in the given Python script to `_`. """
        if not script:
            return ""
        tree = ast.parse(script)
        last = tree.body[-1]
        lines = script.split("\n")
        if isinstance(last, (ast.Expr, ast.Assign)):
            lines[last.lineno - 1] = f"{key} = {lines[last.lineno - 1]}"
        else:
            lines.append(f"{key} = None")
        return "\n".join(lines)

def publish(topic, data):
    """ Publishes data to the main process. """
    polyscript.xworker.sync.publish("Worker", "Main", topic, data)


def handle_request(_sender, _topic, request):
    """
    Handles requests received by the worker process.
    """
    Runner(*json.loads(request)).run()


polyscript.xworker.sync.handler = handle_request
polyscript.xworker.sync.subscribe("Worker", "run", "pyodide-runner")

publish("ready", "")
