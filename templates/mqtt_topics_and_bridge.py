"""Matches MQTT topic filters, publishes on change with a deadband and a heartbeat, and bridges Modbus values to MQTT
when the client library paho-mqtt is installed.

Week: 8
Inputs: topic filters and topics, a series of measured values, the deadband and the heartbeat, the address of a broker.
Outputs: the topics that a filter receives, the samples that are published, and MQTT messages on a broker.
Example: python mqtt_topics_and_bridge.py           (offline demonstration)
         python mqtt_topics_and_bridge.py --broker test.mosquitto.org   (publishes to a public test broker)
The matching rules and the levels of quality of service follow the OASIS standard MQTT Version 5.0. The bridge uses
paho-mqtt (pip install paho-mqtt) and publishes simulated values; replace read_value() with a Modbus read.
"""
import json
import math
import random
import sys
import time


def matches(filt: str, topic: str) -> bool:
    """'+' matches exactly one level, '#' all remaining levels (only as the last level)."""
    f, t = filt.split("/"), topic.split("/")
    for i, part in enumerate(f):
        if part == "#":
            return i == len(f) - 1
        if i >= len(t) or (part != "+" and part != t[i]):
            return False
    return len(f) == len(t)


def broker_packets(n_msgs: int, subscribers: int, qos: int) -> int:
    """Packets that pass the broker: QoS 0, 1, 2 exchange 1, 2, 4 packets on each hop."""
    k = {0: 1, 1: 2, 2: 4}[qos]
    return n_msgs * (k + subscribers * k)


class OnChange:
    """Decides whether a new sample is published: a change beyond the deadband or a heartbeat."""

    def __init__(self, deadband: float, heartbeat_s: float):
        self.deadband, self.heartbeat_s = deadband, heartbeat_s
        self.last_value, self.last_time = None, -math.inf

    def should_publish(self, value: float, now_s: float) -> bool:
        if (self.last_value is None or abs(value - self.last_value) > self.deadband
                or now_s - self.last_time >= self.heartbeat_s):
            self.last_value, self.last_time = value, now_s
            return True
        return False


def read_value(t_s: float) -> float:
    """A simulated meter in kW; replace it with a Modbus read of the real device."""
    return 150 + 20 * math.sin(t_s / 600) + random.gauss(0, 1.0)


def bridge(host: str, topic: str = "campus/demo/meter/power", seconds: int = 60):
    import paho.mqtt.client as mqtt                       # pip install paho-mqtt
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2) if hasattr(mqtt, "CallbackAPIVersion") else mqtt.Client()
    client.will_set(topic + "/status", "offline", qos=1, retain=True)
    client.connect(host, 1883, keepalive=30)
    client.loop_start()
    client.publish(topic + "/status", "online", qos=1, retain=True)
    gate = OnChange(deadband=2.0, heartbeat_s=30)
    t0 = time.time()
    while time.time() - t0 < seconds:
        now = time.time() - t0
        v = read_value(now)
        if gate.should_publish(v, now):
            client.publish(topic, json.dumps({"t": round(now, 1), "kw": round(v, 2)}), qos=1)
            print("published", round(v, 2))
        time.sleep(1)
    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    topics = ["campus/b1/meter/power", "campus/b2/meter/energy", "campus/pv/inverter/power", "campus/bat/bms/soc"]
    for f in ["campus/#", "campus/+/meter/+", "campus/bat/#", "campus/+/+/power"]:
        print(f"{f:<20} -> {[t for t in topics if matches(f, t)]}")
    print("packets at QoS 1, 1728 messages, 3 subscribers:", broker_packets(1728, 3, 1))
    random.seed(1)
    gate = OnChange(deadband=5.0, heartbeat_s=300)
    sent = sum(gate.should_publish(read_value(t), t) for t in range(0, 3600, 25))
    print("published on change in one hour:", sent, "of", 3600 // 25)
    if "--broker" in sys.argv:
        bridge(sys.argv[sys.argv.index("--broker") + 1])
