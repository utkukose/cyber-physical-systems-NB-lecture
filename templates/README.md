# Development templates

Each week adds a development template: A small, working Python program that carries out one method of the week and can be reused in projects. The templates run with the Python standard library and NumPy unless their header states otherwise, and each starts with a description, its inputs and outputs, and an example run.

| Week | Template | What it does |
|---|---|---|
| [Week 8](../weeks/week-08/README.md) | [`modbus_rtu_frames.py`](modbus_rtu_frames.py) | Builds and parses Modbus RTU frames with their CRC, decodes registers into integers and floats and computes the poll cycle of a bus. |
| [Week 8](../weeks/week-08/README.md) | [`mqtt_topics_and_bridge.py`](mqtt_topics_and_bridge.py) | Matches MQTT topic filters, publishes on change with a deadband and a heartbeat, and bridges Modbus values to MQTT when the client library paho-mqtt is installed. |
| [Week 8](../weeks/week-08/README.md) | [`networked_loop_sim.py`](networked_loop_sim.py) | Simulates a first-order control loop with network delay, sampling and packet loss, and computes its delay margin. |

Run a template with `python <file>` in a terminal or paste it into a Colab cell. The templates are licensed under the MIT License of the repository.
