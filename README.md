# pregnancytest
# CPU Scheduling Simulator

## Group Members
- Sanchez, Althea
- Evangelista, Haira Joice
- Ilagan, Jaybee Jr.
- Cepillo, Steven Nicholas
- Mendoza, Mark Airon

## Project Description
The CPU Scheduling Simulator is a program that demonstrates how different CPU scheduling algorithms manage and execute processes. It simulates process execution, generates Gantt charts, calculates scheduling metrics, and compares the performance of each algorithm.

## Objectives
- Understand how different CPU scheduling algorithms work.
- Simulate process execution based on scheduling rules.
- Generate a Gantt chart or timeline.
- Calculate completion time, turnaround time, waiting time, and response time.
- Compare the performance of different scheduling algorithms.

## Scheduling Algorithms

### 1. First Come, First Served (FCFS)
FCFS executes processes in the order they arrive in the ready queue. It is a non-preemptive algorithm.

### 2. Shortest Job First (SJF)
SJF selects the available process with the shortest burst time. It is a non-preemptive algorithm.

### 3. Shortest Remaining Time First (SRTF)
SRTF selects the available process with the shortest remaining burst time. It is a preemptive algorithm.

### 4. Priority Scheduling
Priority Scheduling selects processes based on their assigned priority values. It can be preemptive or non-preemptive, depending on the instructor's requirements.

## User Input
The program asks the user to enter the following information:

| Input | Description |
|---|---|
| Number of Processes | Total number of processes |
| Process ID | Unique identifier for each process |
| Arrival Time (AT) | Time when a process enters the ready queue |
| Burst Time (BT) | Total CPU time required by a process |
| Priority | Priority value assigned to each process |
| Tie-Breaking Rule | Rule used when processes have equal scheduling values |

## Actual Processing
1. Validate the user's input.
2. Store the process information.
3. Simulate each scheduling algorithm.
4. Determine the execution order of processes.
5. Generate a Gantt chart or timeline.
6. Calculate the scheduling metrics.
7. Compute the average turnaround time, waiting time, and response time.
8. Display a comparison of the scheduling algorithms.

## Scheduling Formulas

| Metric | Formula |
|---|---|
| Completion Time (CT) | Time when the process finishes |
| Turnaround Time (TAT) | CT - AT |
| Waiting Time (WT) | TAT - BT |
| Response Time (RT) | First Start Time - AT |

### Average Calculations

```text
Average TAT = Sum of all TAT / Number of Processes
Average WT = Sum of all WT / Number of Processes
Average RT = Sum of all RT / Number of Processes
```

## Expected Output
The program displays the following information for each scheduling algorithm:

- Algorithm name
- Gantt chart or execution timeline
- Process scheduling table
- Completion time (CT)
- Turnaround time (TAT)
- Waiting time (WT)
- Response time (RT)
- Average turnaround time
- Average waiting time
- Average response time
- Short comparison of the algorithms

## Sample Input

```text
Enter number of processes: 4

Process ID: P1
Arrival Time: 0
Burst Time: 5
Priority: 2

Process ID: P2
Arrival Time: 1
Burst Time: 3
Priority: 1

Process ID: P3
Arrival Time: 2
Burst Time: 8
Priority: 3

Process ID: P4
Arrival Time: 3
Burst Time: 2
Priority: 2
```

## Sample Output

```text
========================================
        CPU SCHEDULING SIMULATOR
========================================

Algorithm: FCFS

Gantt Chart:
| P1 | P2 | P3 | P4 |
0    5    8    16   18

Process Scheduling Table:

PID   AT   BT   Priority   CT   TAT   WT   RT
P1    0    5      2        5    5     0    0
P2    1    3      1        8    7     4    4
P3    2    8      3        16   14    6    6
P4    3    2      2        18   15    13   13

Average Turnaround Time: 10.25
Average Waiting Time: 5.75
Average Response Time: 5.75
```

## Short Comparison
- FCFS executes processes in arrival order.
- SJF selects the process with the shortest burst time.
- SRTF selects the process with the shortest remaining burst time and allows preemption.
- Priority Scheduling executes processes according to their assigned priority values.

The program compares the average turnaround time, waiting time, and response time to determine the performance of each algorithm.

## Requirements
- Python 3.x
- Python IDE or terminal

## How to Run
1. Open the project folder.
2. Run the Python program using a terminal or Python IDE.

```bash
python main.py
```

3. Enter the required process information.
4. Select the scheduling algorithm.
5. View the Gantt chart, scheduling table, average calculations, and comparison.

## Conclusion
The CPU Scheduling Simulator provides a practical way to understand how different CPU scheduling algorithms work. It demonstrates how each algorithm affects process execution and system performance through scheduling simulations and calculations.
