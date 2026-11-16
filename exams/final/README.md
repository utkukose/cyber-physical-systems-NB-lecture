<div align="center">

# Final project: A networked cyber-physical system with its digital twin

**Cyber-Physical Systems (BIL-435 Siber Fiziksel Sistemler)**  
Prof. Dr. Utku Kose, Süleyman Demirel University

</div>

## Overview

The final project takes a cyber-physical system of the student's choice along the later stages of the campus microgrid [1, 2]. These are its communication, its operation with an optimisation or a forecast, its digital twin and its safety argument. It combines the methods of the whole course, with the weight on Weeks 8 to 14. Choose one of the three options below, and extend its starter Colab notebook with the data of your own system. Timing: Released in Week 12, due at the end of Week 14. The final project counts 60 percent of the course grade.

## Learning outcomes assessed

Course learning outcomes 5, 6, 7 and 8 (see the [course README](../../README.md)).

## Options

### Final option 1: A heated building with its digital twin

Choose a building with a heating or cooling system and sensors, such as a sports hall, a library or a greenhouse. Design the publishers of its Message Queuing Telemetry Transport (MQTT) network, and check the load of the broker and the lost readings (Week 8) [3, 4]. Calibrate the twin of the building from a log, and keep it in step with the readings (Week 12) [5, 6]. Detect a change of the building with the cumulative sum (CUSUM) of the innovations, and recalibrate the twin (Weeks 10 and 12) [7]. Ask the twin a what-if question under uncertainty with the Monte Carlo method (Week 13) [8]. Close with a safety argument: A fault tree of a hazard and a runtime monitor that compares the sensors with the twin (Week 14) [9, 10].

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/utkukose/cyber-physical-systems-NB-lecture/blob/main/exams/final/FIN1_heated_hall_twin.ipynb) Starter Colab notebook: [`FIN1_heated_hall_twin.ipynb`](FIN1_heated_hall_twin.ipynb). Its example case: A sports hall with a heat pump of 60 kW and wireless sensors.

### Final option 2: A battery with forecast-based dispatch

Choose a building with solar panels and a battery, such as a supermarket, a school or a workshop. Forecast its load with a regression and its solar power from the cloud cover (Week 10) [11, 12]. Compare both forecasts with a naive baseline [13]. Plan the battery for each day with a linear program, and evaluate the plans with the actual values (Week 9) [14, 15]. Check the cycle time of the Modbus field bus that reads the devices (Week 8) [16]. Estimate the remaining useful life of the battery from its capacity tests, with its uncertainty (Week 13) [17]. Close with a safety argument: A runtime monitor that keeps the reserve, with its tests (Week 14) [10].

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/utkukose/cyber-physical-systems-NB-lecture/blob/main/exams/final/FIN2_battery_dispatch.ipynb) Starter Colab notebook: [`FIN2_battery_dispatch.ipynb`](FIN2_battery_dispatch.ipynb). Its example case: A supermarket with 120 kWp of solar panels and a battery of 200 kWh.

### Final option 3: A pumping station with a safety case

Choose a system with a hazard and a remote link, such as a pumping station, a cold store or a charging station. Decide after how many lost readings the pump stops, from the false stops and the delay (Week 8) [18]. Calibrate a twin of the reservoir with linear least squares, and validate its predictions (Week 12) [6]. Plan the pumping with a linear program on the demand that the twin forecasts (Weeks 9 and 10) [14]. Check every reachable state of the controller with a model checker, and find the counterexamples of the weaker designs (Week 14) [19, 20]. Close with the reliability of the protections and the fault tree of an overflow (Week 14) [21, 9].

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/utkukose/cyber-physical-systems-NB-lecture/blob/main/exams/final/FIN3_pumping_station.ipynb) Starter Colab notebook: [`FIN3_pumping_station.ipynb`](FIN3_pumping_station.ipynb). Its example case: A pumping station that fills a hillside reservoir over a radio link.

## Proposal

The final project starts with a proposal of about 500 words, written in Week 12. It names the system with its physical process, its sensors, actuators and network, and the hazard that matters most. It names the option with its methods and the data: A log of the real system, measurements of the student or a simulation with stated assumptions. It plans the evaluation with its scenarios and measures. During active semesters, the proposal can be sent to utkukose@sdu.edu.tr or utkukose@gmail.com for early feedback.

## Example proposals

Two example proposals show the expected scope and level of detail. Each follows the parts of the proposal above. Students write their own proposals in the same way for the system of their choice.

### A greenhouse heated by a biomass boiler (Option 1)

**The system and its hazard.** The greenhouse of a horticulture school grows seedlings in winter. A biomass boiler heats it through pipes under the benches, and eight wireless sensors measure the air and the soil. Below 5 °C the seedlings die within a night, so the hazard is a cold night with a failed boiler or a wrong sensor.

**The data.** The school logs the temperatures, the power of the boiler and a weather station every 15 minutes. Three weeks of January give the log for the calibration and the validation. The solar gains are large, so the twin keeps the term of the irradiance.

**The methods.** The sensors publish over MQTT to a broker on a small computer in the greenhouse. The twin of Week 12 is fitted to two weeks and validated on the third. The CUSUM of the innovations watches for an open vent. The twin answers when the boiler must start before a frosty morning, with the forecast error of the weather service.

**The evaluation plan.** The broker is checked for its load with 12 sensors at one reading per minute. The twin is judged by its root mean square error one day ahead. The safety argument rests on a fault tree of the frost hazard and on a monitor that compares each sensor with the twin.

**Safety and data.** The student never switches the boiler. All experiments run on the log and on the twin, and the log holds no personal data.

### The battery of a bus depot (Option 2)

**The system and its hazard.** A bus depot charges six electric buses at night. It has 300 kWp of solar panels and a battery of 500 kWh, and its grid connection allows 400 kW. A higher peak trips the main breaker, and the hazard is a depot that cannot charge its buses for the morning service.

**The data.** The operator provides one year of hourly loads of the chargers and of the workshop, and the power of the solar panels. The weather service provides the temperatures and the cloud cover with their forecasts.

**The methods.** A regression forecasts the load of the workshop, and the timetable gives the charging of the buses. A linear program plans the battery and the chargers each evening, with the limit of the connection as a constraint. The Modbus cycle of the chargers, the meter and the battery is checked against a control period of 1 s. The capacity tests of the battery give its remaining useful life.

**The evaluation plan.** The plans are evaluated on 30 days that the regression did not use, against charging without a plan. The monitor that keeps the buses chargeable is tested with unit tests and with forecast errors of 20 percent.

**Safety and data.** All experiments run on the logs and in simulation. The logs hold no data about the drivers.

## Deliverables

An executed Colab notebook with all outputs, the report as a PDF and the data that the Colab notebook uses, or the code that simulates them. The report has 1500 to 2500 words and follows the sections of the Word template [REPORT_TEMPLATE.docx](../REPORT_TEMPLATE.docx). Its safety argument states the claim, the evidence and the assumptions. File names start with the student number.

## Evaluation

| Criterion | Weight |
|---|---|
| The system, its hazard and its requirements | 10 % |
| The communication and its timing | 15 % |
| The optimisation or the forecast, with its evaluation | 15 % |
| The digital twin: Calibration, validation and use | 20 % |
| The safety argument: Verification, fault tree or monitor | 20 % |
| Report quality, figures and references | 15 % |
| Statement on tools and responsible use | 5 % |

## Experiments and data

Measurements on real systems make a project stronger, for example the step test of a room or the log of a building. Equipment is switched, opened or changed only with the permission and under the supervision of the person responsible for it. Work on mains voltage, pressurised water or rotating machines is left to qualified staff. Logs of organisations are used only with their permission and without personal data. Simulated data are acceptable where real data cannot be collected, if the report says so clearly and explains how they were simulated.

## Submission

During active semesters, the deadline and the submission channel are announced by the instructor. Reports and Colab notebooks can be sent to utkukose@sdu.edu.tr or utkukose@gmail.com. Self-learners are welcome to complete the projects for their own portfolios. The policy on generative artificial intelligence tools in the [syllabus](../../SYLLABUS.md) applies.

## References

[1] Rajkumar, R., Lee, I., Sha, L., & Stankovic, J. (2010). Cyber-physical systems: The next computing revolution. In *Proceedings of the 47th Design Automation Conference* (pp. 731-736). ACM. <https://doi.org/10.1145/1837274.1837461>

[2] Grieves, M., & Vickers, J. (2017). Digital twin: Mitigating unpredictable, undesirable emergent behavior in complex systems. In F.-J. Kahlen, S. Flumerfelt, & A. Alves (Eds.), *Transdisciplinary Perspectives on Complex Systems: New Findings and Approaches* (pp. 85-113). Springer. <https://doi.org/10.1007/978-3-319-38756-7_4>

[3] Banks, A., Briggs, E., Borgendale, K., & Gupta, R. (Eds.). (2019). *MQTT Version 5.0* (OASIS Standard, 7 March 2019). OASIS. <https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html>

[4] Little, J. D. C. (1961). A proof for the queuing formula: L = λW. *Operations Research*, *9*(3), 383-387. <https://doi.org/10.1287/opre.9.3.383>

[5] Kritzinger, W., Karner, M., Traar, G., Henjes, J., & Sihn, W. (2018). Digital Twin in manufacturing: A categorical literature review and classification. *IFAC-PapersOnLine*, *51*(11), 1016-1022. <https://doi.org/10.1016/j.ifacol.2018.08.474>

[6] Ljung, L. (1999). *System Identification: Theory for the User* (2nd ed.). Prentice Hall.

[7] Page, E. S. (1954). Continuous inspection schemes. *Biometrika*, *41*(1-2), 100-115. <https://doi.org/10.1093/biomet/41.1-2.100>

[8] Metropolis, N., & Ulam, S. (1949). The Monte Carlo method. *Journal of the American Statistical Association*, *44*(247), 335-341. <http://links.jstor.org/sici?sici=0162-1459%28194909%2944%3A247%3C335%3ATMCM%3E2.0.CO%3B2-3>

[9] Ruijters, E., & Stoelinga, M. (2015). Fault tree analysis: A survey of the state-of-the-art in modeling, analysis and tools. *Computer Science Review*, *15-16*, 29-62. <https://doi.org/10.1016/j.cosrev.2015.03.001>

[10] Sha, L. (2001). Using simplicity to control complexity. *IEEE Software*, *18*(4), 20-28. <https://doi.org/10.1109/MS.2001.936213>

[11] Hong, T., Gui, M., Baran, M. E., & Willis, H. L. (2010). Modeling and forecasting hourly electric load by multiple linear regression with interactions. In *IEEE PES General Meeting*. IEEE. <https://doi.org/10.1109/PES.2010.5589959>

[12] Kasten, F., & Czeplak, G. (1980). Solar and terrestrial radiation dependent on the amount and type of cloud. *Solar Energy*, *24*(2), 177-189. <https://doi.org/10.1016/0038-092X(80)90391-6>

[13] Hyndman, R. J., & Koehler, A. B. (2006). Another look at measures of forecast accuracy. *International Journal of Forecasting*, *22*(4), 679-688. <https://doi.org/10.1016/j.ijforecast.2006.03.001>

[14] Boyd, S., & Vandenberghe, L. (2004). *Convex Optimization*. Cambridge University Press. <https://doi.org/10.1017/CBO9780511804441>

[15] Huangfu, Q., & Hall, J. A. J. (2018). Parallelizing the dual revised simplex method. *Mathematical Programming Computation*, *10*(1), 119-142. <https://doi.org/10.1007/s12532-017-0130-5>

[16] Modbus-IDA. (2006). *MODBUS over Serial Line Specification and Implementation Guide V1.02*. Modbus Organization.

[17] Si, X.-S., Wang, W., Hu, C.-H., & Zhou, D.-H. (2011). Remaining useful life estimation – A review on the statistical data driven approaches. *European Journal of Operational Research*, *213*(1), 1-14. <https://doi.org/10.1016/j.ejor.2010.11.018>

[18] Hespanha, J. P., Naghshtabrizi, P., & Xu, Y. (2007). A survey of recent results in networked control systems. *Proceedings of the IEEE*, *95*(1), 138-162. <https://doi.org/10.1109/JPROC.2006.887288>

[19] Clarke, E. M., Emerson, E. A., & Sistla, A. P. (1986). Automatic verification of finite-state concurrent systems using temporal logic specifications. *ACM Transactions on Programming Languages and Systems*, *8*(2), 244-263. <https://doi.org/10.1145/5397.5399>

[20] Baier, C., & Katoen, J.-P. (2008). *Principles of Model Checking*. MIT Press.

[21] Rausand, M., & Høyland, A. (2004). *System Reliability Theory: Models, Statistical Methods, and Applications* (2nd ed.). Wiley.
