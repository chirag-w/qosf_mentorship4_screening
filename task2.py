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
    #Each qubit will randomly be in |+> or |-> after this loop
    for i in range(4):
        if(str[i]=='1'):
            qc.x(i)
        qc.h(i)
    return qc

def xor(str1,str2):
    str = ""
    n = len(str1)
    for i in range(n):
        if(str1[i]==str2[i]):
            str+='0'
        else:
            str+='1'
    return str

def get_initial_states():
    #Returns 4 random 4-qubit states
    strings = get_desired_output_states()
    seed = generate_bitstring(4)
    for i in range(4):
        strings[i] = xor(strings[i],seed)
    print("Starting states:",strings)
    states = [construct_state(strings[i]) for i in range(4)]

    return states

def get_desired_output_states():
    #Returns the 4 desired output states as bitstrings
    strings = ['0011','0101','1010','1100'] #Output strings are stored backwards as they are reversed in qiskit
    return strings

def get_parameterized_circuit(layers):
    qc = QuantumCircuit(4,4)
    theta = ParameterVector(name = 'θ', length = 4*layers)
    for i in range(layers):
        for j in range(4):
            qc.ry(theta[4*i+j],j)
        qc.barrier()
        for j in range(4):
            for k in range(j):
                qc.cz(k,j)
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
            val = counts[i][desired_output_states[i]]
            res+= val
        except KeyError:
            pass
    return -res

states = get_initial_states()
desired_output_states = get_desired_output_states()
backend = Aer.get_backend('qasm_simulator')

l = 2
param_circuit, parameters = get_parameterized_circuit(l)
for j in range(5):
    theta_vals = 2*np.pi*np.random.random(4*l)
    res = minimize(objective_function,theta_vals, method = "COBYLA")
    print('Layers =',l)
    print('Starting values =',theta_vals)
    print(res)