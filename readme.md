## Setup
-  Install dependencies:
``python manege.py -r requirements.txt``

## Input Format


To run the scripts, we will need three files as input:

### 1.  circuit_file

This file contains the circuit to be computed. In addition, it also contains which inputs are assigned to alice and bob

**Format**:
- The file starts with a description of the circuit
    - Each line contains a gate or a terminal (A terminal simoly means a input)
    - terminals are represented as `term <name>`.
    - gates are represented as 
       - binary gates: `<gate_type> <input1> <input2> <identifier>` 
       - unary gates: `<gate_type> <input> <identifier>`
       - `identifier` is an identifier for the gate used for later inputs
       - each input should be a previusly defined terminal or gate 
- The gate description ends with a line describing the output in the format `output <identifier>`
   - `identifier` is the identifier of the gate that produces the output and must be a previously defined gate
- Finally, the file ends with two lines:
   - `a1 a2 ... an` where `a0`, `a1`, `a2` are the identifiers of the inputs assigned to alice
   - `b1 b2 ... bm` where `b0`, `b1`, `b2` are the identifiers of the inputs assigned to bob
- Empty lines and lines starting with `#` are ignored. So, we can add comments to the file using `#`
- Allowed gates are and, or, not.

**Example**:
  ```
  # This is a comment
  term a0
  term a1
  term b0
  term b1
    
  not a0 na0
  and na0 a1 x
  and b0 b1 b
  or x b out
    
  output out
    
  a0 a1
  b0 b1
  ```

### 2. alice_assignment_file

This file contains the values assigned to alice's inputs

**Format**: Each line contains `input_name value`. Empty lines and lines starting with `#` are ignored.

**Example**:
    ```
    a0 1
    a1 0
    ```
  
### 3. bob_assignment_file
Similar to `alice_assignment_file`, but for bob's inputs. Every input must be in one of the two files. 


## Scripts
There are two scripts to run:
### 1. **bob.py**
This script acts as bob and uses `circuit_file` and `bob_assignment_file`. In addition, it also acts as the server for communication with alice

**Usage**: `python bob.py <port> <circuit_file> <bob_assignment_file> [--verbose]`

**Example**: `python bob.py 12345 circuit.txt bob.txt --verbose`

### 2. **alice.py**
This script acts as alice and uses `circuit_file` and `alice_assignment_file`. It acts as the client for communication with bob

**Usage:** `python alice.py <ip> <port> <circuit_file> <alice_assignment_file> [--verbose]`

Here ip and port are the ip and port of bob.py.

**Example**: `python alice.py localhost 12345 circuit.txt alice.txt --verbose`



### **run.sh**
If we are running both scripts on the same machine, we can use the script `run.sh` to run both scripts in parallel.

First we put the three files in the same directoory and name them as `circuit.txt`, `bob.txt` and `alice.txt`. 
Then we run the script as follows:
```./run.sh <port> <directory>```
```

