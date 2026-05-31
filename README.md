@"
# Branch Predictor Simulator

A Python-based interactive simulator for 4 CPU branch prediction algorithms, built as a Computer Architecture Lab project.

## Algorithms Implemented
- Static Predictor
- 1-Bit Predictor
- 2-Bit Saturating Counter
- Tournament Predictor (Local + Global History)

## Features
- Interactive GUI with real-time charts
- Pipeline animation showing misprediction flushes
- Comparison of accuracy, penalty cycles, and IPC
- 3 built-in branch trace types + load your own

## How to Run
pip install matplotlib numpy
python trace_generator.py
python main.py

## Built With
Python | Tkinter | Matplotlib
"@ | Out-File -Encoding utf8 README.md
