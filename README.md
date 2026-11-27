# CPU Scheduling Simulator (PT 101 • Topic 1)

## Group Members

- Sanchez, Althea (Project Manager)
- Evangelista, Haira Joice (Backend Developer)
- Ilagan, Jaybee Jr. (Backend Developer)
- Cepillo, Steven Nicholas (Backend Developer)
- Mendoza, Mark Airon (Backend Developer)

## Project Description

The **CPU Scheduling Simulator** is an interactive desktop application built with Python and Tkinter that visually demonstrates how different CPU scheduling algorithms manage, preempt, and execute processes. It features a retro OS-window interface (teal, sky-blue, and cream theme with chunky 3D buttons) and animates real-time CPU execution, tracks the ready queue, draws a Gantt chart with hover details, calculates scheduling metrics, and ranks all algorithms side by side on a leaderboard.

## Objectives

- Understand how non-preemptive and preemptive CPU scheduling algorithms operate.
- Visualize process execution, CPU idle time, and ready queue changes in real time.
- Generate an interactive Gantt chart with hoverable segment details.
- Calculate Completion Time (CT), Turnaround Time (TAT), Waiting Time (WT), and Response Time (RT).
- Compare average performance metrics across all supported algorithms.

## Scheduling Algorithms

| # | Algorithm | Type | How it picks the next process |
|---|---|---|---|
| 1 | **First-Come, First-Served (FCFS)** | Non-preemptive | Runs processes strictly in order of arrival, each to completion. |
| 2 | **Shortest Job First (SJF)** | Non-preemptive | When the CPU is free, picks the arrived process with the smallest burst time and runs it to completion. |
| 3 | **Shortest Remaining Time First (SRTF)** | Preemptive | Re-evaluated every time unit; the process with the least remaining time gets the CPU, so shorter newcomers can interrupt. |
| 4 | **Priority Scheduling** | Non-preemptive | When the CPU is free, picks the ready process with the highest priority (**lower number = higher priority**) and runs it to completion. |
| 5 | **Priority Scheduling** | Preemptive | Re-evaluated every time unit; a newly arrived higher-priority process immediately takes the CPU. |

> **Tie-Breaking Rule:** When two or more processes have identical scheduling criteria (burst time, remaining time, or priority), ties are broken by **Arrival Time (AT)** first, followed by **input order**.

## Key Features

- **Add Process panel:** Add custom processes with input validation, delete selected rows, clear the list, load the built-in **★ SAMPLE** dataset (includes an idle CPU gap), or generate a **🎲 RANDOM** workload. Each process gets its own color across the whole interface.
- **CPU Core monitor:** A CPU chip graphic shows the running process (or `IDLE`, `STANDBY`, `DONE`), along with the process count, selected algorithm, status (`Ready`, `Running`, `Paused`, `Complete`), the simulation clock (`t`), and a CPU load bar.
- **Algorithm tabs:** Five color-coded tabs (`FCFS`, `SJF`, `SRTF`, `PRIORITY (NP)`, `PRIORITY (P)`). Clicking a tab switches algorithm and starts the simulation immediately. An info card explains the selected algorithm and shows a `PREEMPTIVE` / `NON-PREEMPTIVE` badge.
- **Playback controls:** `▶ RUN`, `⏸ PAUSE` / `▶ RESUME` / `↻ REPLAY`, `⏭ STEP` (advance one time unit), `⏩ SKIP` (jump to the finished result), and a speed slider from `1 u/s` to `12 u/s`.
- **Interactive Gantt chart and Ready Queue:** Process blocks and `IDLE` periods are drawn as time advances, with a moving time marker. Hover over a block to see its process, time range, length, `AT`, `BT`, and priority. The ready queue shows the waiting processes live.
- **Process Metrics table:** `CT`, `TAT`, `WT`, and `RT` appear as each process completes, followed by the overall averages.
- **Algorithm Leaderboard (`⚡ COMPARE ALL`):** Runs all five algorithms on the current process list and shows bar charts of Average TAT, WT, and RT, highlighting the best value in each column with `★`. Double-click any row to simulate that algorithm.
- **Resizable, scrollable layout:** If the window is smaller than the comfortable layout size, the page scrolls (mouse wheel, or `Shift` + wheel for horizontal scrolling).

## User Input

Processes are entered through the **Add Process** form in the GUI (press `Enter` in any field to add):

| Input | Description | Validation Rule |
|---|---|---|
| **Process ID (PID)** | Unique identifier for each process (auto-suggests `P1`, `P2`, ...) | Non-empty, unique (case-insensitive), cannot be `IDLE` |
| **Arrival Time (AT)** | Time unit when the process enters the ready queue | Integer `>= 0` |
| **Burst Time (BT)** | Total CPU time required by the process | Integer `> 0` |
| **Priority** | Priority rank assigned to the process (lower = higher priority) | Integer (defaults to `0` if left blank) |

## Scheduling Formulas

| Metric | Formula |
|---|---|
| **Completion Time (CT)** | Time unit when the process finishes execution |
| **Turnaround Time (TAT)** | `CT - AT` |
| **Waiting Time (WT)** | `TAT - BT` |
| **Response Time (RT)** | `First Start Time - AT` |
| **CPU Load** | `(Busy Time so far / Current Time) * 100%` |

### Average Calculations

```text
Average TAT = Sum of all TAT / Number of Processes
Average WT  = Sum of all WT  / Number of Processes
Average RT  = Sum of all RT  / Number of Processes
```

## Built-in Sample Dataset (★ SAMPLE)

Clicking **SAMPLE** loads five processes designed to showcase scheduling behavior and CPU idle time (`t = 17` to `t = 25`):

| PID | Arrival Time (AT) | Burst Time (BT) | Priority |
|---|---|---|---|
| P1 | 0 | 6 | 3 |
| P2 | 2 | 4 | 1 |
| P3 | 4 | 2 | 4 |
| P4 | 6 | 5 | 2 |
| P5 | 25 | 3 | 1 |

### Example Result (FCFS on the sample dataset)

```text
Gantt Chart:
| P1 | P2 | P3 | P4 | IDLE | P5 |
0    6    10   12   17     25   28

PID   AT   BT   Priority   CT   TAT   WT   RT
P1    0    6      3         6    6     0    0
P2    2    4      1        10    8     4    4
P3    4    2      4        12    8     6    6
P4    6    5      2        17   11     6    6
P5    25   3      1        28    3     0    0

Average TAT: 7.20
Average WT:  3.20
Average RT:  3.20
```

## Requirements

- Python 3.x
- Tkinter (included with standard Python installations on Windows and macOS; on Linux, install it with `sudo apt install python3-tk` if needed)
- No external third-party packages required (uses only the standard library: `math`, `random`, `tkinter`)

## How to Run

1. Clone or open the project folder in your terminal or IDE.
2. Run the application:

   ```bash
   python gui_cpu_scheduler.py
   ```

   (use whichever file name you keep in your repository, for example `main.py`)

3. Add processes manually, or click **★ SAMPLE** / **🎲 RANDOM**.
4. Click an algorithm tab (`FCFS`, `SJF`, `SRTF`, `PRIORITY (NP)`, or `PRIORITY (P)`) to run it, or use **▶ RUN**. Use **⏩ SKIP** for instant results.
5. Click **⚡ COMPARE ALL** to benchmark all five algorithms on the leaderboard.

## Conclusion

The CPU Scheduling Simulator bridges operating system theory and visual intuition. By pairing accurate scheduling calculations with step-by-step Gantt chart animation and multi-algorithm benchmarking, it clearly demonstrates how preemption, burst length, and priority assignment affect turnaround, waiting, and response times.
