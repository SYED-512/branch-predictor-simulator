# trace_generator.py
import random

def generate_loop_trace(iterations=200, loop_len=10):
    """Simulates a loop: branch taken most of the time, not-taken at loop exit."""
    trace = []
    addr = 0x1000
    for _ in range(iterations):
        for i in range(loop_len):
            taken = (i < loop_len - 1)  # taken every iteration except last
            trace.append((addr, taken))
    return trace

def generate_random_trace(n=500, taken_prob=0.6):
    """Truly random branch outcomes."""
    trace = []
    for i in range(n):
        addr = random.choice([0x1000, 0x1010, 0x1020, 0x1030])
        trace.append((addr, random.random() < taken_prob))
    return trace

def generate_nested_if_trace(n=300):
    """Alternating taken/not-taken — worst case for 1-bit predictor."""
    trace = []
    for i in range(n):
        addr = 0x2000 + (i % 4) * 0x10
        trace.append((addr, i % 2 == 0))
    return trace

def save_trace(trace, filename):
    with open(filename, 'w') as f:
        for addr, taken in trace:
            f.write(f"{addr} {'T' if taken else 'N'}\n")

def load_trace(filename):
    trace = []
    with open(filename) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                addr = int(parts[0], 16) if parts[0].startswith('0x') else int(parts[0])
                taken = parts[1].upper() == 'T'
                trace.append((addr, taken))
    return trace

if __name__ == "__main__":
    import os
    os.makedirs("traces", exist_ok=True)
    save_trace(generate_loop_trace(), "traces/loop_heavy.txt")
    save_trace(generate_random_trace(), "traces/random.txt")
    save_trace(generate_nested_if_trace(), "traces/nested_if.txt")
    print("Traces generated in traces/ folder.")