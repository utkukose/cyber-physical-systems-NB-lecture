<div align="center">

# Midterm project: A model and a controller for a cyber-physical system

**Cyber-Physical Systems (BIL-435 Siber Fiziksel Sistemler)**  
Prof. Dr. Utku Kose, Süleyman Demirel University

</div>

## Overview

The midterm project applies the methods of Weeks 1 to 7 to a small cyber-physical system of the student's choice [1]. Examples are a heated room, a battery with a solar panel and a water tank with a pump. The system is modelled, its modes and sensors are described, and a controller is designed and tested in simulation. Finally, the timing of the computer that runs the controller is checked. Choose one of the three options below, and extend its starter Colab notebook with the data of your own system. Timing: Released in Week 6, due at the end of Week 7. The midterm project counts 40 percent of the course grade. The optional weekly tasks and research assignments carry no separate weight. They are combined with the midterm component, and the instructor may take them into account as a discretionary adjustment.

## Learning outcomes assessed

Course learning outcomes 1, 2, 3, 4, 5 and 8 (see the [course README](../../README.md)).

## Options

### Midterm option 1: A heated room

Choose a room that you can observe, such as a seminar room, a laboratory or a room at home. Identify its thermal resistance and capacitance from a step test, and model a day of its use (Week 2) [2]. Describe its thermostat as a hybrid automaton (Week 3) [3]. For a noisy sensor, find the hysteresis band that balances comfort against the switchings of the heater (Week 4) [4]. Design a proportional-integral (PI) controller by placing the poles of the loop, and compare it with the thermostat, with and without anti-windup (Week 5) [5]. Filter the readings with a Kalman filter (Week 6) [6]. Close with the response times of the tasks of the controller under rate-monotonic scheduling (Week 7) [7, 8].

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/utkukose/cyber-physical-systems-NB-lecture/blob/main/exams/midterm/MID1_heated_room.ipynb) Starter Colab notebook: [`MID1_heated_room.ipynb`](MID1_heated_room.ipynb). Its example case: A seminar room with an electric heater of 8 kW on a winter day.

### Midterm option 2: A solar street light

Choose a small system with a solar panel and a battery, such as a street light, a parking meter or a weather station. Model its energy balance and the state of charge (SoC) of the battery over several days of changing weather (Weeks 1 and 2). Describe the controller as a hybrid automaton with a low-voltage disconnect (Week 3) [3]. Measure the state of charge with a biased current sensor and a noisy voltage (Week 4). A Kalman filter that also learns the offset of the sensor combines the two (Week 6) [9]. Design a proportional controller that dims the lamp as the battery empties (Week 5) [5]. Close with the schedulability of the tasks under rate-monotonic and earliest-deadline-first scheduling (Week 7) [7, 10].

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/utkukose/cyber-physical-systems-NB-lecture/blob/main/exams/midterm/MID2_solar_street_light.ipynb) Starter Colab notebook: [`MID2_solar_street_light.ipynb`](MID2_solar_street_light.ipynb). Its example case: A solar street light with a battery of 1.2 kWh over ten winter days.

### Midterm option 3: A water tank with a pump

Choose a tank that a pump fills, such as the roof tank of a building, a rainwater tank or the tank of a greenhouse. Model the level as an integrator of the inflow and the demand (Week 2). Describe the float switches as a hybrid automaton, and choose their band from the number of starts that the motor allows (Week 3). Choose the sampling and the averaging of an ultrasonic level sensor, so that surface waves neither alias nor reach the pump (Week 4) [11]. Design a proportional-integral (PI) controller for a variable-speed pump with anti-windup (Week 5) [5]. Close with the reaction time of the programmable logic controller (PLC) and the time from an alarm to an overflow (Week 7) [12].

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/utkukose/cyber-physical-systems-NB-lecture/blob/main/exams/midterm/MID3_water_tank.ipynb) Starter Colab notebook: [`MID3_water_tank.ipynb`](MID3_water_tank.ipynb). Its example case: The roof tank of a student dormitory, filled by a pump of 3 m³/h.

## Deliverables

An executed Colab notebook with all outputs and the report as a PDF. The report has 1500 to 2500 words and follows the sections of the Word template [REPORT_TEMPLATE.docx](../REPORT_TEMPLATE.docx). File names start with the student number. Measurements on real equipment, such as the step test of a room, are welcome. The report then describes the set-up and the safety measures.

## Evaluation

| Criterion | Weight |
|---|---|
| The system, its requirements and its model | 15 % |
| Correctness of the models, the measures and the code | 25 % |
| Modes, sensors and estimation | 15 % |
| The controller and its tuning | 20 % |
| Timing of the computing platform | 10 % |
| Report quality, figures and references | 10 % |
| Statement on tools and responsible use | 5 % |

## Experiments and data

Measurements on real systems make a project stronger, for example the step test of a room or the log of a building. Equipment is switched, opened or changed only with the permission and under the supervision of the person responsible for it. Work on mains voltage, pressurised water or rotating machines is left to qualified staff. Logs of organisations are used only with their permission and without personal data. Simulated data are acceptable where real data cannot be collected, if the report says so clearly and explains how they were simulated.

## Submission

During active semesters, the deadline and the submission channel are announced by the instructor. Reports and Colab notebooks can be sent to utkukose@sdu.edu.tr or utkukose@gmail.com. Self-learners are welcome to complete the projects for their own portfolios. The policy on generative artificial intelligence tools in the [syllabus](../../SYLLABUS.md) applies.

## References

[1] Lee, E. A., & Seshia, S. A. (2017). *Introduction to Embedded Systems: A Cyber-Physical Systems Approach* (2nd ed.). MIT Press. <https://ptolemy.berkeley.edu/books/leeseshia/>

[2] Bacher, P., & Madsen, H. (2011). Identifying suitable models for the heat dynamics of buildings. *Energy and Buildings*, *43*(7), 1511-1522. <https://doi.org/10.1016/j.enbuild.2011.02.005>

[3] Henzinger, T. A. (1996). The theory of hybrid automata. In *Proceedings of the 11th Annual IEEE Symposium on Logic in Computer Science* (pp. 278-292). IEEE. <https://doi.org/10.1109/LICS.1996.561342>

[4] Bennett, W. R. (1948). Spectra of quantized signals. *Bell System Technical Journal*, *27*(3), 446-472. <https://doi.org/10.1002/j.1538-7305.1948.tb01340.x>

[5] Åström, K. J., & Murray, R. M. (2021). *Feedback Systems: An Introduction for Scientists and Engineers* (2nd ed.). Princeton University Press.

[6] Kalman, R. E. (1960). A new approach to linear filtering and prediction problems. *Journal of Basic Engineering*, *82*(1), 35-45. <https://doi.org/10.1115/1.3662552>

[7] Liu, C. L., & Layland, J. W. (1973). Scheduling algorithms for multiprogramming in a hard-real-time environment. *Journal of the ACM*, *20*(1), 46-61. <https://doi.org/10.1145/321738.321743>

[8] Joseph, M., & Pandya, P. (1986). Finding response times in a real-time system. *The Computer Journal*, *29*(5), 390-395. <https://doi.org/10.1093/comjnl/29.5.390>

[9] Plett, G. L. (2004). Extended Kalman filtering for battery management systems of LiPB-based HEV battery packs. *Journal of Power Sources*, *134*(2), 252-261. <https://doi.org/10.1016/j.jpowsour.2004.02.031>

[10] Buttazzo, G. C. (2011). *Hard Real-Time Computing Systems: Predictable Scheduling Algorithms and Applications* (3rd ed.). Springer. <https://doi.org/10.1007/978-1-4614-0676-1>

[11] Shannon, C. E. (1949). Communication in the presence of noise. *Proceedings of the IRE*, *37*(1), 10-21. <https://doi.org/10.1109/JRPROC.1949.232969>

[12] John, K.-H., & Tiegelkamp, M. (2010). *IEC 61131-3: Programming Industrial Automation Systems: Concepts and Programming Languages, Requirements for Programming Systems, Decision-Making Aids* (2nd ed.). Springer. <https://doi.org/10.1007/978-3-642-12015-2>
