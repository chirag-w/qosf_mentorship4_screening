import random
from qiskit import *
from qiskit.circuit import ParameterVector
from qiskit import quantum_info as qi
import matplotlib as mpl
import numpy as np 
from scipy.optimize import minimize

def generate_bitstring(n):
    #Return a random n-bit binary string
    s = ""
    for i in range(n):
        s+= str(random.randint(0,1)) #Append a random bit to the string
    return s

def construct_state(str):
    qc = QuantumCircuit(4,4)
    #Apply gates to the qubits according to the bitstring str
    #Each qubit will be in |+> or |-> after this loop
    for i in range(4):
        if(str[i]=='1'):
            qc.x(i)
        qc.h(i)
    return qc

def xor(str1,str2):
    #Return the bitwise xor of two binary strings of equal length
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
    seed = generate_bitstring(4) #Generate a random seed
    while(seed == "0000" or seed == "1111"):
        seed = generate_bitstring(4) #Ensure seed is not '0000' or '1111'
    for i in range(4):
        strings[i] = xor(strings[i],seed) #Generate 4 starting strings using seed
    states = [construct_state(strings[i]) for i in range(4)] #Construct the initial states

    return states

def get_desired_output_states():
    #Returns the 4 desired output states as bitstrings
    strings = ['0011','0101','1010','1100']
    return strings

def get_parameterized_circuit(layers):
    #Returns the appropriate parameterized circuit
    qc = QuantumCircuit(4,4)
    theta = ParameterVector(name = 'θ', length = 4*layers)
    for i in range(layers):
        for j in range(4):
            qc.ry(theta[4*i+j],j) #Apply an Ry gate to each qubit
        qc.barrier()
        for j in range(4):
            for k in range(j):
                qc.cz(k,j) #Apply a CZ gate between each pair of qubits
        qc.barrier()
    for i in range(4):
        qc.measure(i,i)
    return qc,theta

def get_output_states(states,var_circuit):
    #Append the parameterized circuit to the initial circuits and return
    output_states = []
    for i in range(len(states)):
        output_states.append(states[i] +var_circuit)
    return output_states

def objective_function(theta_vals):
    #Return the ratio of successful outputs
    val_dict = dict(zip(parameters,theta_vals))
    bound_circuit = param_circuit.bind_parameters(val_dict)
    output_states = get_output_states(states,bound_circuit)
    n = len(output_states)
    res = 0
    for i in range(n):
        counts = execute(output_states,backend,shots = 1024).result().get_counts()
        try:
            val = counts[i][desired_output_states[i]]
            res+= val/1024
        except KeyError:
            pass
    return -res/n #Return negative value as SciPy can only minimize

def display_output(in_circuits,out_circuit):
    state_backend = Aer.get_backend('statevector_simulator')
    count_backend = Aer.get_backend('qasm_simulator')
    in_states = []
    out_states = []
    i = 0
    for in_circuit in in_circuits:
        i+=1
        job = execute(in_circuit,state_backend)
        result = job.result()
        in_state = result.get_statevector()
        ###
        job = execute(in_circuit+out_circuit,count_backend)
        result = job.result()
        out_counts = result.get_counts()
        print("Input state",i,":",in_state) #Display the initial statevector
        print()
        print("Output counts for input state",i,":",out_counts) #Display the counts of the output state
        print('---------------------------')


states = get_initial_states()

desired_output_states = get_desired_output_states()
backend = Aer.get_backend('qasm_simulator')

l = 2
param_circuit, parameters = get_parameterized_circuit(l)
max_acc = 0
theta_opt = []
while(max_acc < 0.99): #Optimization continues until a high empirical probability to get the desired states is observed 
    theta_vals = 2*np.pi*np.random.random(4*l)
    res = minimize(objective_function,theta_vals, method = "COBYLA")
    fidelity = -res.fun
    if(fidelity > max_acc): #If this result is the best one so far
        max_acc = fidelity  #Update the accuracy
        theta_opt = res.x   #Update the optimal parameters
    
final_dict = dict(zip(parameters,theta_opt))
final_circuit = param_circuit.bind_parameters(final_dict) #Trained circuit

display_output(states,final_circuit)

print("Trained circuit:")
print(final_circuit)
print("Achieved fidelity between ideal circuit and trained circuit:",max_acc)
print('---------------------------')