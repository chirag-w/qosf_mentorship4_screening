import random
from qiskit import *
from qiskit.circuit import ParameterVector
from qiskit import quantum_info as qi
import matplotlib as mpl
import numpy as np 

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
    #Each qubit will randomly be in |0>,|1>,|+> or |-> after this loop
    for i in range(4):
        if(str[2*i]=='1'):
            qc.x(i)
        if(str[2*i+1]=='1'):
            qc.h(i)
    return qc

def get_initial_states():
    #Returns 4 random 4-qubit states
    states = []
    for i in range(4):
        states.append(generate_state())
    return states

def get_desired_output_states():
    #Returns the 4 desired output states
    states = []
    strings = ['0011','0101','1010','1100']
    for i in range(4):
        qc = QuantumCircuit(4)
        for j in range(4):
            if(strings[i][j]=='1'):
                qc.x(j)
        states.append(qc)
    return states

def get_parameterized_circuit(layers):
    qc = QuantumCircuit(4)
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
    return qc,theta

def get_output_states(states,var_circuit):
    output_states = []
    for i in range(len(states)):
        output_states.append(states[i] +var_circuit)
    return output_states

def statevector(circuits):
    backend = Aer.get_backend('statevector_simulator')
    statevectors = []
    for circuit in circuits:
        job = execute(circuit,backend)
        result = job.result()
        statevectors.append(result.get_statevector())
    return statevectors

def avg_fidelity(output_statevectors,desired_output_statevectors):
    n = len(output_states)
    fid = 0
    for i in range(n):
        fid+= qi.state_fidelity(output_statevectors[i],desired_output_statevectors[i])
    return fid/n



param_circuit, parameters = get_parameterized_circuit(3)
states = get_initial_states()
val_dict = {parameter: np.random.random() for parameter in parameters}

bound_circuit = param_circuit.bind_parameters(val_dict)

output_states = get_output_states(states,bound_circuit)
desired_output_states = get_desired_output_states()

output_statevectors = statevector(output_states)
desired_output_statevectors = statevector(desired_output_states)


overlap = avg_fidelity(output_statevectors,desired_output_statevectors)
print(overlap)