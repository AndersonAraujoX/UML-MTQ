# Quantum Thermal Machine Framework

A Python framework for simulating and optimizing **quantum thermal machines** using hybrid quantum-classical variational algorithms. This repository constitutes the original software implementation that served as the practical foundation for the academic paper:

> *"Applying UML for Modeling a Quantum Thermal Machine Framework"*

The paper was derived from this implementation — not the other way around. The codebase was subsequently refactored and modeled using UML to extract its architecture for formal analysis.

---

## Overview

This framework provides a modular, object-oriented platform for:

- Simulating multi-qubit quantum thermal machines composed of hot/cold baths and internal working subsystems.
- Generating quantum correlations between subsystems via parametric quantum circuits.
- Optimizing work extraction (ergotropy) using a custom hybrid Adam optimizer over variational quantum circuits.
- Evaluating thermodynamic quantities such as average work, heat, and ergotropy from quantum states.

The repository serves dual roles:

1. **Software Framework** — An extensible, executable codebase for quantum thermodynamics simulation.
2. **Research Artifact** — The concrete implementation from which the architecture was extracted and modeled using UML Profiles and diagram methodologies for academic publication.

---

## Motivation

### Why Modeling Quantum Systems Is Hard

Quantum software systems operate at the intersection of two fundamentally different computational paradigms: classical control logic (optimization loops, data management, parameter updates) and quantum circuit execution (state preparation, unitary evolution, measurement). This hybrid nature introduces architectural complexity that is not adequately captured by conventional software engineering tools.

Key difficulties include:

- **State representation**: Quantum states live in exponentially large Hilbert spaces, encoded as density matrices or state vectors, incompatible with conventional data modeling.
- **Non-determinism**: Quantum measurements are probabilistic; reproducing results requires careful seeding and averaging strategies.
- **Circuit-classical coupling**: Variational algorithms tightly couple parametric quantum gates to classical gradient estimators, creating bidirectional data dependencies.
- **Abstraction gaps**: Standard programming abstractions (classes, interfaces, methods) do not naturally express quantum gate sequences, entanglement topologies, or Trotterized Hamiltonians.

### Why UML Is Relevant

UML (Unified Modeling Language) provides a standardized graphical notation capable of expressing software architecture at multiple levels of abstraction. For hybrid quantum-classical systems, UML becomes relevant because:

- Class diagrams can formalize the separation between classical, quantum, and hybrid components.
- Activity diagrams capture the sequential stages of a quantum thermodynamic cycle.
- Sequence diagrams illustrate the runtime interaction between classical optimizers and quantum circuit executors.
- UML Profiles (extensions of the standard) allow domain-specific stereotypes to be defined, enabling precise annotation of quantum constructs (qubits, quantum gates, Hamiltonians) within standard UML tooling.

This repository enabled the exploration of how such models can be systematically derived from a working implementation.

---

## Architecture Overview

The framework models a quantum thermal machine as a three-stage process:

### Stage 1 — Thermalization

The quantum system is initialized by coupling boundary qubits (indices `0` and `N-1`) to simulated thermal baths at inverse temperatures `β_A` (hot) and `β_B` (cold). This is implemented via `ThermalizationOperation`, which applies parametric `RX` rotations on the boundary qubits and propagates the thermal influence inward through a symmetric chain of `CNOT` gates.

The angles `θ_A` and `θ_B` encode the Boltzmann populations of each bath:

```
θ = 2 · arctan(exp(ε · β / 2))
```

### Stage 2 — Correlation Generation

After thermalization, quantum correlations (entanglement) are generated between pairs of internal qubits according to a chosen **topology**. Correlation operations are parametric circuits that apply entangling gate sequences (`RY`, `CNOT`, optionally `RZ` for imaginary-phase correlations).

Available correlation strategies include:
- `ParametricCorrelation` — real-valued two-parameter correlations.
- `ImaginaryParametricCorrelation` — extends above with an `RZ(π/2)` phase gate.
- `IsotropicCorrelation` — fixed unitary-based entanglement.

The choice of which qubit pairs to entangle is governed by an interchangeable **Topology** strategy class.

### Stage 3 — Work Extraction (VQA Loop)

Work is extracted by evolving the correlated quantum state under a parametric Hamiltonian (e.g., Heisenberg-XX, -XY, or -XYZ interaction). The work operation is implemented as a Trotterized time evolution (`qml.ApproxTimeEvolution`).

A classical **Adam optimizer** iterates over the coupling constants of this Hamiltonian, computing gradients via **central finite differences** over the quantum circuit outputs, and updates parameters to maximize the extracted average work (ergotropy):

```
W = Tr[H · ρ₀] - Tr[H · U(θ)ρ₀U†(θ)]
```

This constitutes the variational quantum algorithm (VQA) loop at the core of the framework.

---

## Core Components

### `QuantumThermalMachine` (`framework/classical_quantum/quantum_thermal_machine.py`)

The central quantum circuit controller. Manages the PennyLane device and compiles three internal QNodes:

| QNode | Purpose |
|---|---|
| `_initial_state_node` | Prepares the correlated initial state ρ₀ |
| `_final_state_node` | Runs the full three-stage circuit |
| `_swap_node` | Applies the work operation to an arbitrary QuTiP state |

Also provides utilities for circuit visualization (`draw`) and IBM Quantum hardware compilation (`compiled_ibm`).

### `ErgotropyOptimizer` (`framework/classical_quantum/ergotropy_optimizer.py`)

The hybrid classical-quantum controller responsible for maximizing ergotropy. Implements:

- **Adam optimizer** with configurable `learning_rate`, `beta1`, `beta2`, `num_epochs`, and `tol`.
- **Central finite difference** gradient estimation over quantum circuit parameters.
- **Early stopping** based on loss convergence tolerance.
- A static `optimize()` factory method that orchestrates the full initialization-and-optimization pipeline from raw parameters.

### `ThermodynamicsCalculator` (`framework/classical_quantum/thermodynamics_calculator.py`)

A stateless utility class exposing `compute_average_work(ρ_i, ρ_f, H_i, H_f)`. Computes the thermodynamic work difference between the initial and final quantum states using the QuTiP expectation value formalism.

### Operation Classes (`framework/quantum/operations.py`)

All quantum gate sequences are encapsulated as concrete subclasses of `QuantumOperation`, enforcing a uniform `.apply(num_qubits)` interface:

| Class | Stage | Description |
|---|---|---|
| `ThermalizationOperation` | 1 | Boundary `RX` + CNOT chain |
| `IsotropicCorrelation` | 2 | Fixed unitary entanglement |
| `ParametricCorrelation` | 2 | Parametric `RY`/`CNOT` entanglement |
| `ImaginaryParametricCorrelation` | 2 | Above + `RZ(π/2)` phase |
| `TrotterizedHeisenbergXX` | 3 | Heisenberg-XX time evolution |
| `TrotterizedHeisenbergXY` | 3 | Heisenberg-XY time evolution |
| `TrotterizedHeisenbergXYZ` | 3 | Full Heisenberg-XYZ time evolution |

### Topology Classes (`framework/classical/topologies.py`)

Topology strategies implement the abstract `Topology` interface with a single method `get_pairs(num_qubits) -> list`. They determine which qubit pairs interact in correlation and work extraction stages:

| Class | Pattern |
|---|---|
| `LinearTopology` | Chain: `[i, i+1]` |
| `RingTopology` | Closed ring |
| `StarTopology` | Hub-and-spoke from qubit 0 |
| `CompleteTopology` | All-to-all |
| `RainbowTopology` | Symmetric edge-to-center |
| `CompleteInternalTopology` | All-to-all excluding bath qubits |
| `LinearInternalTopology` | Chain excluding bath qubits |
| `PairInternalRainbowTopology` | Rainbow excluding bath qubits |

---

## Hybrid Execution Model

The framework implements a hybrid quantum-classical feedback loop. The execution flow is:

```
Classical (Python)          Quantum (PennyLane / lightning.qubit)
─────────────────           ─────────────────────────────────────
Set β_A, β_B, ε            
Compute θ_A, θ_B ──────►   ThermalizationOperation.apply()
                            CorrelationOperation.apply()
                  ◄──────   Return ρ₀ (state vector)

Initialize params           
For each epoch:
  For each param j:
    params[j] += ε  ──────► WorkOperation.apply() → ρ₊
    params[j] -= ε  ──────► WorkOperation.apply() → ρ₋
  Compute ∂W/∂θⱼ ◄──────   ThermodynamicsCalculator
  Adam update
  
Return optimal params, W
```

Classical Python manages all optimization state (parameters, moments, epoch counters). The quantum device executes only when a state vector evaluation is required. This separation is enforced structurally through the three-layer module organization (`classical/`, `quantum/`, `classical_quantum/`).

---

## UML Modeling

### Repository as a Modeling Basis

This implementation was used as the primary artifact from which a formal UML model of a quantum thermal machine framework was derived. The refactoring of the codebase was intentionally designed to maximize architectural clarity, with explicit separation of classical, quantum, and hybrid components — precisely to facilitate subsequent UML extraction.

### Refactoring for Modelability

The original procedural implementation was restructured to expose:
- Clear class hierarchies with abstract interfaces (`Topology`, `QuantumOperation`, `WorkOperation`).
- Explicit dependency injection via operation class parameters.
- Stateless utility classes (`ThermodynamicsCalculator`).
- A central orchestrator (`QuantumThermalMachine`) with a well-defined public API.

This structure maps directly to UML class diagrams with generalization, realization, and dependency relationships.

### UML Profiles Applied

The architecture was modeled using standard UML extended with domain-specific profiles:

- **Standard UML** — Class, activity, and sequence diagrams representing software structure and behavior.
- **Pérez-Castillo UML Profile** — A quantum computing UML extension providing stereotypes for qubits, quantum gates, and measurement.
- **QuanUML** — An alternative quantum software UML profile explored as a comparative modeling approach.

### Diagram Types

| Diagram Type | Content |
|---|---|
| Class Diagram | Full component hierarchy, dependencies, and interfaces |
| Activity Diagram | Quantum circuit stage abstraction (thermalization → correlation → work) |
| Sequence Diagram | Runtime interaction between `ErgotropyOptimizer` and `QuantumThermalMachine` |

---

## Project Structure

```
.
├── main.py                          # Simulation entry point
├── requirements.txt                 # Python dependencies
├── framework/
│   ├── classical/
│   │   └── topologies.py            # Qubit connectivity topology strategies
│   ├── quantum/
│   │   ├── operations.py            # Thermalization, correlation, work gate classes
│   │   ├── hamiltonians.py          # Observable builders (PennyLane)
│   │   ├── single_qubit_operators.py
│   │   └── many_qubit_operators.py
│   └── classical_quantum/
│       ├── quantum_thermal_machine.py   # QNode compiler and circuit executor
│       ├── ergotropy_optimizer.py       # Hybrid Adam optimizer
│       └── thermodynamics_calculator.py # Work / ergotropy calculation
└── Ws_XX_plot.png                   # Example simulation output
```

---

## Installation

**Prerequisites:** Python ≥ 3.10

```bash
# Clone the repository
git clone https://github.com/AndersonAraujoX/Mestrado-UML.git
cd Mestrado-UML

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Dependencies:**

| Package | Version | Role |
|---|---|---|
| `numpy` | ≥ 2.0 | Numerical computation |
| `scipy` | ≥ 1.13 | Matrix exponentials, linear algebra |
| `pennylane` | ≥ 0.36 | Quantum circuit simulator |
| `qutip` | ≥ 5.1 | Quantum state manipulation |
| `qutip-qip` | ≥ 0.4 | Quantum information primitives |
| `matplotlib` | ≥ 3.9 | Result visualization |
| `tqdm` | ≥ 4.67 | Progress monitoring |

---

## Usage

### Basic Workflow

```python
from framework.quantum.operations import (
    ThermalizationOperation, ImaginaryParametricCorrelation, TrotterizedHeisenbergXX
)
from framework.classical.topologies import RainbowTopology, LinearTopology
from framework.classical_quantum.ergotropy_optimizer import ErgotropyOptimizer
from framework.quantum.many_qubit_operators import many_body_hamiltonian_from_local_operators

# 1. Define the system
N_QUBITS = 4
correlation_topology = RainbowTopology().get_pairs(N_QUBITS)
work_topology = LinearTopology().get_pairs(N_QUBITS)

# Build the Hamiltonian for the internal subsystem
H_AB = many_body_hamiltonian_from_local_operators(N_QUBITS - 2, local_hamiltonians)

# 2. Define thermalization parameters (from inverse temperatures β and energy gaps ε)
import numpy as np
theta_A = 2 * np.arctan(np.exp(e_A * beta_A * 0.5))
theta_B = 2 * np.arctan(np.exp(e_B * beta_B * 0.5))

# 3. Run the optimization
ergotropy, optimal_params, loss_history = ErgotropyOptimizer.optimize(
    num_qubits=N_QUBITS,
    thermalization_operation_class=ThermalizationOperation,
    correlation_operation_class=ImaginaryParametricCorrelation,
    work_operation_class=TrotterizedHeisenbergXX,
    correlation_topology=correlation_topology,
    work_topology=work_topology,
    H_AB=H_AB,
    params_ther=[theta_A, theta_B],
    params_corr=[theta, phi] * len(correlation_topology)
)

print(f"Extracted ergotropy: {ergotropy:.6f}")
```

### Running the Full Simulation

```bash
python3 main.py
```

This executes a parallelized sweep over energy gap ratios `ε_B/ε_A` and temperature ratios `β_B/β_A`, saving the results as `Ws_XX_plot.png`.

---

## Technologies

| Technology | Role |
|---|---|
| **Python 3.10+** | Implementation language |
| **PennyLane** | Quantum circuit definition and execution (`lightning.qubit` backend) |
| **QuTiP** | Density matrix / state vector algebra, quantum information primitives |
| **NumPy / SciPy** | Numerical optimization, matrix operations |
| **`concurrent.futures`** | Parallel simulation across parameter sweeps |

---

## Academic Reference

This repository is the original software artifact described in:

> Anderson Araujo de Oliveira. *"Applying UML for Modeling a Quantum Thermal Machine Framework."* Master's thesis / research paper. Universidade [Institution], 2026.

If you use this codebase or its architecture in academic work, please cite as:

```bibtex
@misc{araujo2026qtmf,
  author       = {Anderson Araujo de Oliveira},
  title        = {Quantum Thermal Machine Framework},
  year         = {2026},
  howpublished = {\url{https://github.com/AndersonAraujoX/Mestrado-UML}},
  note         = {Original implementation basis for the paper "Applying UML for Modeling a Quantum Thermal Machine Framework"}
}
```

---

## Contributing

Contributions are welcome from both software engineers and quantum computing researchers. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting pull requests.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
