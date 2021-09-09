import random
from qiskit import *
from qiskit.circuit import ParameterVector
from qiskit import quantum_info as qi
import matplotlib as mpl
import numpy as np 
from scipy.optimize import minimize

def generate_bitstring(n):
    #Write a random n-bit binary string to a file
    s = ""
    for i in range(n):
        s+= str(random.randint(0,1)) #Append a random bit to the string
    return s

def construct_state(str):
    qc = QuantumCircuit(4,4)
    #Apply gates to the qubits according to the random bitstring
    #Each qubit will randomly be in |0>,|1>,|+> or |-> after this loop
    for i in range(4):
        if(str[i]=='1'):
            qc.x(i)
    return qc

def get_initial_states():
    #Returns 4 random 4-qubit states
    strings = []
    for i in range(4):
        strings.append(generate_bitstring(4))
        check = False
        while(check == False):
            check = True
            for j in range(i):
                if(strings[i] == strings[j]):
                    check = False
            if(check == False):
                strings[i] = generate_bitstring(4)
    print("Starting states:",strings)
    states = [construct_state(strings[i]) for i in range(4)]

    return states

def get_desired_output_states():
    #Returns the 4 desired output states as bitstrings
    strings = ['1100','1010','0101','0011'] #Output strings are stored backwards as they are reversed in qiskit
    return strings

def get_parameterized_circuit(layers):
    qc = QuantumCircuit(4,4)
    theta = ParameterVector(name = 'θ', length = 8*layers)
    for i in range(layers):
        for j in range(4):
            qc.rx(theta[8*i+j],j)
        for j in range(4):
            qc.ry(theta[8*i+4+j],j)
        qc.barrier()
        for j in range(4):
            for k in range(j):
                qc.cx(k,j)
        qc.barrier()
    for i in range(4):
        qc.measure(i,i)
    return qc,theta

def get_output_states(states,var_circuit):
    output_states = []
    for i in range(len(states)):
        output_states.append(states[i] +var_circuit)
    return output_states


def objective_function(theta_vals):
    val_dict = dict(zip(parameters,theta_vals))
    bound_circuit = param_circuit.bind_parameters(val_dict)
    output_states = get_output_states(states,bound_circuit)
    n = len(output_states)
    res = 0
    for i in range(n):
        counts = execute(output_states,backend,shots = 1024).result().get_counts()
        try:
            val = counts[0][desired_output_states[i]]
            res+= val
        except KeyError:
            pass
    return -res

states = get_initial_states()
desired_output_states = get_desired_output_states()
backend = Aer.get_backend('qasm_simulator')

for l in range(1,3):
    param_circuit, parameters = get_parameterized_circuit(l)
    for j in range(5):
        theta_vals = 2*np.pi*np.random.random(8*l)
        bounds = [(0,2*np.pi) for theta in theta_vals]
        res = minimize(objective_function,theta_vals,bounds = bounds)
        print('Layers =',l)
        print('Starting values =',theta_vals)
        print(res)
