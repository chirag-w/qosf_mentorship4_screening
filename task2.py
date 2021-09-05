import random
from qiskit import QuantumCircuit
import matplotlib as mpl

def generate_bitstring(n):
    #Return a random n-bit binary string
    s = ""
    for i in range(n):
        s+= str(random.randint(0,1)) #Append a random bit to the string
    return s

def generate_state():
    qc = QuantumCircuit(4)
    str = generate_bitstring(8)
    #Apply gates to the qubits according to the random bitstring
    #Each qubit will be in |0>,|1>,|+> or |-> after this loop
    for i in range(4):
        if(str[2*i]=='1'):
            qc.x(i)
        if(str[2*i+1]=='1'):
            qc.h(i)
    return qc

def get_initial_states():
    states = []
    for i in range(4):
        states.append(generate_state())
    return states

def get_desired_output_states():
    states = []
    strings = ['0011','0101','1010','1100']
    for i in range(4):
        qc = QuantumCircuit(4)
        for j in range(4):
            if(strings[i][j]=='1'):
                qc.x(j)
        states.append(qc)
    return states
