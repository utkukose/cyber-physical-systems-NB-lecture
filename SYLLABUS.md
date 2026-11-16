# Syllabus: Cyber-Physical Systems

**BIL-435 Siber Fiziksel Sistemler. Undergraduate elective course, Department of Computer Engineering, Süleyman Demirel University, Isparta, Türkiye**

Instructor: Prof. Dr. Utku Kose, Department of Computer Engineering, Süleyman Demirel University. Contact: utkukose@sdu.edu.tr, utkukose@gmail.com. This course is updated in line with current developments in the field. First version: November 2026.

## Course information

Course code: BIL-435. Type: Undergraduate elective course of the Department of Computer Engineering, Süleyman Demirel University. Language: English. Format: Fourteen weeks, one session of about three hours per week, usable in synchronous and asynchronous study.

## Course description

Cyber-physical systems (CPS) integrate computation, networking and physical processes: Embedded computers and networks monitor and control the physical processes, usually with feedback loops in which the physical processes affect the computations and the computations affect the physical processes [1, 2]. They run power grids, factories, buildings, vehicles and medical devices, and their design joins computer engineering with control and physics [3, 4]. Over fourteen weeks, the course leads from the feedback loop and the models of continuous, discrete and hybrid dynamics to sensors, actuators, feedback control and estimation. It continues with embedded computing, real-time scheduling and the networks that connect the devices, and then with optimisation, learning from data and the security of CPS. Two weeks build a digital twin of the running project, and the last week turns to dependability, safety and verification.

## Prerequisites

Basic programming in any language and first-year mathematics, in particular functions, derivatives, elementary differential equations, matrices and elementary probability. Python is taught from the first step; the optional warm-up in `start-here/` introduces Colab and the first Python steps.

## Learning outcomes

1. Explain what makes a system cyber-physical, describe its feedback loops and model the power balance of a microgrid.
2. Model continuous, discrete and hybrid dynamics with differential equations and state machines, and simulate them.
3. Describe sensors and actuators with sampling, quantisation and noise, and design feedback controllers of the P, PI and PID type for stability and performance.
4. Estimate the state of a physical process from noisy measurements with filters such as the Kalman filter, and detect bad data.
5. Analyse the timing of embedded and networked systems, including real-time schedules, fieldbuses, publish-subscribe messaging and the effect of network delay on control loops.
6. Optimise the operation of an energy system, forecast its loads and generation, and detect anomalies and attacks.
7. Build, synchronise and calibrate a digital twin of a cyber-physical system and use it for what-if analysis and predictive maintenance, with attention to dependability and safety.
8. Write and run Python programs in Google Colab that simulate, control and analyse cyber-physical systems.

## Weekly plan

| Week | Topic | Python step |
|---|---|---|
| 1 | Foundations: Cyber-Physical Systems, Feedback Loops and the Power Balance | Step 1: Values, variables, lists and decisions |
| 2 | Continuous Dynamics: Batteries, Buildings and Grid Frequency | Step 2: Simulation loops with NumPy |
| 3 | Discrete and Hybrid Dynamics: State Machines, Thermostats and Protection Relays | Step 3: States and transitions |
| 4 | Sensors and Actuators: Sampling, Quantisation, Noise and Smart Meters | Step 4: Signals as arrays |
| 5 | Feedback Control: P, PI and PID, Stability and Frequency Control | Step 5: Functions for controllers |
| 6 | Estimation and Filtering: The Kalman Filter, State Estimation and Bad Data | Step 6: Matrices and the Kalman filter |
| 7 | Embedded Computing and Real-Time Scheduling: RM, EDF and the PLC Scan Cycle | Step 7: Tasks and time |
| 8 | Networks and Communication: Modbus, MQTT, IEC 61850 and Control over Networks | Step 8: Bytes, bits and binary messages |
| 9 | Energy Optimisation: Economic Dispatch, Battery Scheduling and Demand Response | Step 9: Optimisation with SciPy |
| 10 | Learning from Data: Load and Generation Forecasting, Anomaly Detection | Step 10: Fitting and forecasting |
| 11 | Security of Cyber-Physical Systems: False Data Injection and Defences | Step 11: Hashes and keys |
| 12 | Digital Twins I: Synchronisation and Calibration | Step 12: A twin as a class |
| 13 | Digital Twins II: What-If Analysis and Predictive Maintenance | Step 13: Scenarios and Monte Carlo |
| 14 | Dependability, Safety and Verification | Step 14: Organised and tested code |

The midterm project is released in Week 6 and due at the end of Week 7. The final project is released in Week 12 and due at the end of Week 14. Exact dates are announced by the instructor during active semesters.

## Learning activities and workload

Each week combines a lecture page with formulas, worked examples, knowledge checks, an interactive scene, animations and review cards, also available as printable lecture notes. An interactive lab adds a 3D virtual laboratory with the hardware of the week, step-by-step calculators, a self-assessment and reflection prompts. A Colab notebook opens with the Python step of the week and continues with hands-on exercises on the campus microgrid. A development template, application challenges, a weekly task and an optional research assignment complete the week. The overview page of each week lists them together with the study path. The expected workload is seven to ten hours per week, including the class session when the course is taught in person.

## Assessment

Assessment rests on two projects, each a coding application with a short technical report. The midterm project at the end of Week 7 models a small cyber-physical system of the student's choice with the methods of Weeks 1 to 7, designs a controller for it and checks its timing. The final project at the end of Week 14 adds a communication design, an optimisation or a forecast, a digital twin and a safety argument. The midterm component counts 40 percent of the course grade and the final project 60 percent. Each week also offers an optional task, an optional research and report assignment and a self-assessment in the interactive lab. The optional work carries no separate weight. It is combined with the midterm component, and the instructor may take it into account as a discretionary adjustment. During an active semester, the deadlines are announced by the instructor, and the optional work can be sent to utkukose@sdu.edu.tr or utkukose@gmail.com.

| Component | Weight |
|---|---|
| Midterm project, end of Week 7, with the optional weekly tasks and research assignments as a discretionary adjustment | 40 % |
| Final project, end of Week 14 | 60 % |

Reports use the Word template `exams/REPORT_TEMPLATE.docx`, cite their sources in square brackets and include the Colab notebooks that produced their results. Unless an assignment states otherwise, a research report has 1500 to 2500 words, follows the structure of an academic paper and cites at least six scholarly or official sources.

## Policy on generative AI tools

Generative AI tools may be used as assistants for explanation, debugging and drafting, under four conditions. Students state in every submission which tools were used and for what. Students verify every factual, numerical and code claim themselves and remain fully responsible for its correctness. Students cite the primary sources that support their work, not the tool. Finally, students do not enter confidential, personal or unpublished data into external services, which includes data of real buildings, devices and their users. Submissions that present unverified generated content as the student's own analysis are treated as academic misconduct [5, 6].

## Academic integrity

Collaboration in discussing ideas is encouraged. Code, reports and reflections are individual unless a task states otherwise. Code taken from other sources, including the reference solutions of the Colab notebooks and the development templates, must be acknowledged. Experiments on real equipment follow the safety rules of the laboratory, and data collected from buildings or devices stay anonymous.

## Accessibility

The lecture pages and interactive labs are designed for keyboard use, legible fonts, sufficient contrast and reduced motion when the operating system requests it. The 3D parts can be operated with the buttons below each view. Students who need other adjustments can contact the instructor.

## Main textbooks and open resources

Lee and Seshia for the models and the embedded side of cyber-physical systems [2], and Alur for their principles and verification [4]. Kundur for the dynamics of power systems [7], Åström and Wittenmark for computer-controlled systems [8], and Kurose and Ross for computer networks [9]. The review of Olivares and colleagues frames the control of microgrids [10].

## References

[1] Lee, E. A. (2008). Cyber physical systems: Design challenges. In *2008 11th IEEE International Symposium on Object and Component-Oriented Real-Time Distributed Computing (ISORC)* (pp. 363-369). IEEE. <https://doi.org/10.1109/ISORC.2008.25>

[2] Lee, E. A., & Seshia, S. A. (2017). *Introduction to Embedded Systems: A Cyber-Physical Systems Approach* (2nd ed.). MIT Press. <https://ptolemy.berkeley.edu/books/leeseshia/>

[3] Rajkumar, R., Lee, I., Sha, L., & Stankovic, J. (2010). Cyber-physical systems: The next computing revolution. In *Proceedings of the 47th Design Automation Conference* (pp. 731-736). ACM. <https://doi.org/10.1145/1837274.1837461>

[4] Alur, R. (2015). *Principles of Cyber-Physical Systems*. MIT Press. <https://cis.upenn.edu/~alur/pcps.html>

[5] Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., Ishii, E., Bang, Y. J., Madotto, A., & Fung, P. (2023). Survey of hallucination in natural language generation. *ACM Computing Surveys*, *55*(12), 1-38. <https://doi.org/10.1145/3571730>

[6] Kose, U. (2018). Are we safe enough in the future of artificial intelligence? A discussion on machine ethics and artificial intelligence safety. *BRAIN. Broad Research in Artificial Intelligence and Neuroscience*, *9*(2), 184-197. <https://doi.org/10.5281/zenodo.1245926>

[7] Kundur, P. (1994). *Power System Stability and Control*. McGraw-Hill.

[8] Åström, K. J., & Wittenmark, B. (1997). *Computer-Controlled Systems: Theory and Design* (3rd ed.). Prentice Hall.

[9] Kurose, J. F., & Ross, K. W. (2021). *Computer Networking: A Top-Down Approach* (8th ed.). Pearson. <https://www.pearson.com/store/p/computer-networking/P100002980218/9780136681557>

[10] Olivares, D. E., Mehrizi-Sani, A., Etemadi, A. H., Cañizares, C. A., Iravani, R., Kazerani, M., Hajimiragha, A. H., Gomis-Bellmunt, O., Saeedifard, M., Palma-Behnke, R., Jiménez-Estévez, G. A., & Hatziargyriou, N. D. (2014). Trends in microgrid control. *IEEE Transactions on Smart Grid*, *5*(4), 1905-1919. <https://doi.org/10.1109/TSG.2013.2295514>
