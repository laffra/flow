# Flow

Python data flows.


# Using MicroPython for fast startup

The UI of Flow is written in Python, using PyScript/LTK. 
See [main.py](main.py) for the logic. LTK is desiged in such a way
that it uses minimal Python APIs, so it can easily run in MicroPython.

MicroPython is a version of Python that runs in constrained environments,
such as microcontrollers. But, it is also bundled by PyScript, so it
can be used to run small Python apps in the browser. The total footprint
of MicroPython is around 240K bytes. It downloads fast, and loads fast.

Once the UI is created, a worker is created, and the worker is used
to run the flow. The main thread on MicroPython talks with the worker
using publish/subscribe message, very similar to Kafka.

# Using PyOdide in a worker 

The main thread creates the PyOdide worker. 
When a flow is executed in the worker, the result is sent
back to the main thread using the publish/subscribe mechanism.

# Rendering the result

The main thread receives the visualization and updates the flow UI.

# Summary

This small application performs a careful
dance between three VMs: The JavaScript VM, the MicroPython VM, and the
PyOdide worker VM. Information between the worker and main thread is 
done by PyScript using a publish/subscribe mechanism. The main thread
and JavaScript VM communicate using the Foreign Function Interface (FFI).

When the main thread creates the UI, it leverages PyScript LTK. This is
a UI toolkit written in Python, where widgets are a thin layer around
jQuery elements to create layouts, set CSS styling, and handle events.
The state of Flow is kept in one single model, and where appropriate,
the UI is using the Reactive capabilities of LTK, to avoid having
to use event handlers.

