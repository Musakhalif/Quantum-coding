import tkinter as tk
from tkinter import messagebox
import threading
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
simulator = AerSimulator()
WINS = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
def measure_qubit(gate):
    qc = QuantumCircuit(1,1)
    if gate == 'x': qc.x(0)
    elif gate == 'h': qc.h(0)
    qc.measure(0,0)
    job = simulator.run(qc, shots=1, memory=True)
    return int(job.result().get_memory()[0])
class Game:
    def __init__(self, root):
        self.root = root
        self.root.title('Quantum Tic-Tac-Toe')
        self.root.configure(bg='#1a1a2e')
        self.board = [' '] * 9
        self.turn = 0
        self.busy = False
        self.buttons = []
        tk.Label(root, text='Quantum Tic-Tac-Toe', font=('Helvetica',22,'bold'), bg='#1a1a2e', fg='#e0e0ff', pady=14).grid(row=0, column=0, columnspan=3)
        self.status = tk.Label(root, text='X turn - classical', font=('Helvetica',13), bg='#1a1a2e', fg='#aaaaff', pady=4)
        self.status.grid(row=1, column=0, columnspan=3)
        for i in range(9):
            btn = tk.Button(root, text=' ', font=('Helvetica',36,'bold'), width=3, height=1, bg='#16213e', fg='#e0e0ff', activebackground='#0f3460', relief='flat', command=lambda idx=i: self.click(idx))
            btn.grid(row=(i//3)+2, column=i%3, padx=8, pady=8)
            self.buttons.append(btn)
        self.log = tk.Text(root, height=7, width=42, font=('Courier',11), state='disabled', bg='#0d0d1a', fg='#00ffaa', relief='flat')
        self.log.grid(row=5, column=0, columnspan=3, padx=12, pady=6)
        tk.Button(root, text='Restart', font=('Helvetica',12,'bold'), bg='#0f3460', fg='white', relief='flat', padx=14, pady=6, command=self.restart).grid(row=6, column=0, columnspan=3, pady=10)
        self.msg('Game started! X goes first.')
        self.msg('X = classical  |  O = quantum 50/50')
    def msg(self, m):
        self.log.config(state='normal')
        self.log.insert('end', '  ' + m + chr(10))
        self.log.see('end')
        self.log.config(state='disabled')
    def click(self, idx):
        if self.board[idx] != ' ' or self.busy: return
        self.busy = True
        for b in self.buttons: b.config(state='disabled')
        p = 'X' if self.turn == 0 else 'O'
        threading.Thread(target=self.run_move, args=(idx,p), daemon=True).start()
    def run_move(self, idx, p):
        if p == 'X': result = measure_qubit('x')
        else:
            self.root.after(0, self.msg, 'O plays cell ' + str(idx+1) + ' - superposition...')
            result = measure_qubit('h')
        self.root.after(0, self.finish_move, idx, p, result)
    def finish_move(self, idx, p, result):
        if p == 'X':
            self.board[idx] = 'X'
            self.buttons[idx].config(text='X', fg='#ff6b6b', bg='#2d1b1b')
            self.msg('X claims cell ' + str(idx+1) + '!')
        else:
            if result == 1:
                self.board[idx] = 'O'
                self.buttons[idx].config(text='O', fg='#74b9ff', bg='#1b2d3d')
                self.msg('O claims cell ' + str(idx+1) + '!')
            else:
                self.msg('Quantum void! O loses this turn.')
        w = self.winner()
        if w:
            self.msg(w + ' wins!')
            self.status.config(text=w + ' wins!', fg='#00ff99')
            messagebox.showinfo('Game Over', w + ' wins!')
            self.busy = False
            return
        if all(c != ' ' for c in self.board):
            self.msg('Draw!')
            self.status.config(text='Draw!', fg='#bf7fff')
            self.busy = False
            return
        self.turn = 1 - self.turn
        self.busy = False
        for i,b in enumerate(self.buttons):
            if self.board[i] == ' ': b.config(state='normal')
        if self.turn == 0: self.status.config(text='X turn - classical', fg='#ff9999')
        else: self.status.config(text='O turn - quantum 50/50!', fg='#74b9ff')
    def winner(self):
        for a,b,c in WINS:
            if self.board[a]==self.board[b]==self.board[c] and self.board[a]!=' ':
                for i in (a,b,c): self.buttons[i].config(bg='#1a4731')
                for b in self.buttons: b.config(state='disabled')
                return self.board[a]
        return None
    def restart(self):
        self.board = [' '] * 9
        self.turn = 0
        self.busy = False
        for b in self.buttons: b.config(text=' ', state='normal', bg='#16213e', fg='#e0e0ff')
        self.status.config(text='X turn - classical', fg='#aaaaff')
        self.log.config(state='normal')
        self.log.delete('1.0', 'end')
        self.log.config(state='disabled')
        self.msg('Game restarted!')
root = tk.Tk()
root.tk.call('tk', 'scaling', 2.0)
Game(root)
root.mainloop()
