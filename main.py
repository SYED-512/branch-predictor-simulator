import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

from predictors import StaticPredictor, OneBitPredictor, TwoBitPredictor, TournamentPredictor
from simulator import PipelineSimulator
from trace_generator import generate_loop_trace, generate_random_trace, generate_nested_if_trace, load_trace

class BranchSimApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Branch Predictor Simulator')
        self.root.geometry('1100x750')
        self.root.configure(bg='#1A1A2E')
        self.trace = []
        self.results = []
        self._build_ui()

    def _build_ui(self):
        title = tk.Label(self.root, text='Branch Predictor Simulator',
                         font=('Arial', 20, 'bold'), bg='#1A1A2E', fg='#4FC3F7')
        title.pack(pady=10)

        ctrl = tk.Frame(self.root, bg='#16213E', padx=10, pady=10)
        ctrl.pack(fill=tk.X, padx=20)

        tk.Label(ctrl, text='Trace:', bg='#16213E', fg='white', font=('Arial', 11)).grid(row=0, column=0, padx=5)

        self.trace_var = tk.StringVar(value='Loop Heavy')
        trace_opts = ttk.Combobox(ctrl, textvariable=self.trace_var, width=18,
                                  values=['Loop Heavy', 'Random', 'Nested IF', 'Load from file'])
        trace_opts.grid(row=0, column=1, padx=5)

        run_btn = tk.Button(ctrl, text='Run Simulation', command=self.run_simulation,
                            bg='#2E75B6', fg='white', font=('Arial', 11, 'bold'),
                            relief=tk.FLAT, padx=15, pady=5)
        run_btn.grid(row=0, column=2, padx=15)

        clear_btn = tk.Button(ctrl, text='Clear', command=self.clear,
                              bg='#555', fg='white', font=('Arial', 10),
                              relief=tk.FLAT, padx=10, pady=5)
        clear_btn.grid(row=0, column=3, padx=5)

        self.status = tk.Label(ctrl, text='Ready. Select a trace and click Run.',
                               bg='#16213E', fg='#90CAF9', font=('Arial', 10))
        self.status.grid(row=0, column=4, padx=20)

        tframe = tk.Frame(self.root, bg='#1A1A2E')
        tframe.pack(fill=tk.X, padx=20, pady=10)

        cols = ('Predictor', 'Accuracy %', 'Mispredictions', 'Penalty Cycles', 'Total Cycles', 'IPC')
        self.tree = ttk.Treeview(tframe, columns=cols, show='headings', height=5)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background='#0F3460', foreground='white',
                        rowheight=28, fieldbackground='#0F3460', font=('Arial', 10))
        style.configure('Treeview.Heading', background='#2E75B6', foreground='white',
                        font=('Arial', 10, 'bold'))
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150, anchor='center')
        self.tree.pack(fill=tk.X)

        self.fig, self.axes = plt.subplots(1, 3, figsize=(11, 3.5))
        self.fig.patch.set_facecolor('#1A1A2E')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, padx=20, pady=5)

        anim_frame = tk.Frame(self.root, bg='#16213E', pady=8)
        anim_frame.pack(fill=tk.X, padx=20)
        tk.Label(anim_frame, text='Pipeline Trace (last 20 branches):',
                 bg='#16213E', fg='#90CAF9', font=('Arial', 10, 'bold')).pack(anchor='w')
        self.pipeline_canvas = tk.Canvas(anim_frame, height=60, bg='#0D0D0D')
        self.pipeline_canvas.pack(fill=tk.X)

    def _get_trace(self):
        choice = self.trace_var.get()
        if choice == 'Loop Heavy':
            return generate_loop_trace()
        elif choice == 'Random':
            return generate_random_trace()
        elif choice == 'Nested IF':
            return generate_nested_if_trace()
        elif choice == 'Load from file':
            path = filedialog.askopenfilename(filetypes=[('Text files', '*.txt')])
            if path:
                return load_trace(path)
        return []

    def run_simulation(self):
        self.trace = self._get_trace()
        if not self.trace:
            messagebox.showwarning('No Trace', 'No trace loaded.')
            return
        predictors = [StaticPredictor(always_taken=True), OneBitPredictor(),
                      TwoBitPredictor(), TournamentPredictor()]
        self.results = []
        for pred in predictors:
            sim = PipelineSimulator(pred)
            sim.run_trace(self.trace)
            r = sim.report()
            r['history'] = sim.history
            self.results.append(r)
        self._update_table()
        self._update_charts()
        self._update_pipeline_anim(self.results[-1]['history'])
        self.status.config(text=f'Done! Ran {len(self.trace)} branches on all 4 predictors.')

    def _update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in self.results:
            self.tree.insert('', 'end', values=(
                r['predictor'], f"{r['accuracy']:.1f}%", r['mispredictions'],
                r['penalty_cycles'], r['total_cycles'], f"{r['ipc']:.3f}"))

    def _update_charts(self):
        names = ['Static', '1-Bit', '2-Bit', 'Tournament']
        colors = ['#EF5350', '#FFA726', '#42A5F5', '#66BB6A']
        fg = 'white'
        for ax in self.axes:
            ax.clear()
            ax.set_facecolor('#0F3460')
            ax.tick_params(colors=fg)
            for spine in ax.spines.values():
                spine.set_edgecolor('#333')
        acc = [r['accuracy'] for r in self.results]
        self.axes[0].bar(names, acc, color=colors)
        self.axes[0].set_title('Prediction Accuracy (%)', color=fg, fontsize=10)
        self.axes[0].set_ylim(0, 105)
        self.axes[0].set_ylabel('%', color=fg)
        for i, v in enumerate(acc):
            self.axes[0].text(i, v + 1, f'{v:.1f}%', ha='center', color=fg, fontsize=8)
        pen = [r['penalty_cycles'] for r in self.results]
        self.axes[1].bar(names, pen, color=colors)
        self.axes[1].set_title('Total Penalty Cycles', color=fg, fontsize=10)
        self.axes[1].set_ylabel('Cycles', color=fg)
        ipc = [r['ipc'] for r in self.results]
        self.axes[2].bar(names, ipc, color=colors)
        self.axes[2].set_title('IPC (Instructions Per Cycle)', color=fg, fontsize=10)
        self.axes[2].set_ylabel('IPC', color=fg)
        self.axes[2].axhline(1.0, color='yellow', linestyle='--', linewidth=1)
        self.fig.tight_layout()
        self.canvas.draw()

    def _update_pipeline_anim(self, history):
        self.pipeline_canvas.delete('all')
        last20 = history[-20:]
        w = self.pipeline_canvas.winfo_width() or 900
        box_w = w / max(len(last20), 1)
        for i, h in enumerate(last20):
            color = '#4CAF50' if h['correct'] else '#F44336'
            x0 = i * box_w + 2
            x1 = (i + 1) * box_w - 2
            self.pipeline_canvas.create_rectangle(x0, 5, x1, 50, fill=color, outline='#222')
            label = 'T' if h['actual'] else 'N'
            self.pipeline_canvas.create_text((x0+x1)/2, 27, text=label,
                                              fill='white', font=('Arial', 9, 'bold'))
        self.pipeline_canvas.create_text(10, 57, anchor='w',
            text='Green=Correct   Red=Misprediction   T=Taken  N=Not-Taken',
            fill='#90CAF9', font=('Arial', 8))

    def clear(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for ax in self.axes:
            ax.clear()
            ax.set_facecolor('#0F3460')
        self.canvas.draw()
        self.pipeline_canvas.delete('all')
        self.status.config(text='Cleared.')

if __name__ == '__main__':
    root = tk.Tk()
    app = BranchSimApp(root)
    root.mainloop()
