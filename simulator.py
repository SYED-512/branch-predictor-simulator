# simulator.py

MISPREDICTION_PENALTY = 3  # cycles lost per misprediction (typical 5-stage pipeline)

class PipelineSimulator:
    def __init__(self, predictor):
        self.predictor = predictor
        self.cycle = 0
        self.instructions = 0
        self.penalty_cycles = 0
        self.history = []  # list of (address, predicted, actual, correct)

    def run_trace(self, trace):
        """
        trace: list of (address:int, taken:bool)
        """
        for address, actual_taken in trace:
            predicted = self.predictor.predict(address)
            correct = (predicted == actual_taken)

            self.predictor.update(address, actual_taken)
            self.instructions += 1
            self.cycle += 1  # 1 cycle per instruction (ideal)

            if not correct:
                self.cycle += MISPREDICTION_PENALTY
                self.penalty_cycles += MISPREDICTION_PENALTY

            self.history.append({
                'address': address,
                'predicted': predicted,
                'actual': actual_taken,
                'correct': correct,
                'cycle': self.cycle
            })

    def ipc(self):
        """Instructions Per Cycle estimate"""
        return (self.instructions / self.cycle) if self.cycle > 0 else 0

    def report(self):
        return {
            'predictor': self.predictor.name,
            'accuracy': self.predictor.accuracy(),
            'total_branches': self.predictor.total,
            'mispredictions': self.predictor.total - self.predictor.correct,
            'penalty_cycles': self.penalty_cycles,
            'total_cycles': self.cycle,
            'ipc': self.ipc()
        }