# Development templates

Each week adds a development template: A small, working Python program that carries out one method of the week and can be reused in projects. The templates run with the Python standard library and NumPy unless their header states otherwise, and each starts with a description, its inputs and outputs, and an example run.

| Week | Template | What it does |
|---|---|---|
| [Week 1](../weeks/week-01/README.md) | [`power_balance_day.py`](power_balance_day.py) | Computes the hourly balance of a site from its demand, solar and wind models and a battery rule, with the energies, the peak import and the self-sufficiency. |
| [Week 1](../weeks/week-01/README.md) | [`sense_compute_actuate.py`](sense_compute_actuate.py) | A skeleton of a periodic control loop with a sensor, a controller and an actuator as small classes, run against a simulated plant. |
| [Week 2](../weeks/week-02/README.md) | [`building_preheat.py`](building_preheat.py) | Simulates a building with its RC model and a heating schedule, and finds the latest start of the heater for a target temperature by bisection. |
| [Week 2](../weeks/week-02/README.md) | [`first_order_simulation.py`](first_order_simulation.py) | Simulates any model dx/dt = f(t, x, u) with the methods of Euler, Heun and Runge-Kutta, and compares them with an exact solution. |
| [Week 8](../weeks/week-08/README.md) | [`modbus_rtu_frames.py`](modbus_rtu_frames.py) | Builds and parses Modbus RTU frames with their CRC, decodes registers into integers and floats and computes the poll cycle of a bus. |
| [Week 8](../weeks/week-08/README.md) | [`mqtt_topics_and_bridge.py`](mqtt_topics_and_bridge.py) | Matches MQTT topic filters, publishes on change with a deadband and a heartbeat, and bridges Modbus values to MQTT when the client library paho-mqtt is installed. |
| [Week 8](../weeks/week-08/README.md) | [`networked_loop_sim.py`](networked_loop_sim.py) | Simulates a first-order control loop with network delay, sampling and packet loss, and computes its delay margin. |

Run a template with `python <file>` in a terminal or paste it into a Colab cell. The templates are licensed under the MIT License of the repository.
