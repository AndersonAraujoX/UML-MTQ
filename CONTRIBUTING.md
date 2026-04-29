# Contributing to the Quantum Thermal Machine Framework

Thank you for your interest in contributing. This project is simultaneously a **software framework** and a **research artifact** — contributions are expected to maintain the quality and integrity of both dimensions. Please read this document carefully before opening issues or submitting pull requests.

---

## Nature of This Project

This repository exists at the intersection of software engineering and quantum computing research. It is the original implementation basis for the paper *"Applying UML for Modeling a Quantum Thermal Machine Framework"*, and it continues to serve as:

- A **working simulation framework** for quantum thermodynamics experiments.
- A **modeling reference** for UML-based analysis of hybrid quantum-classical software architecture.

Contributions that affect the architecture — adding components, refactoring existing classes, introducing new operation types — have implications for both the software and the published models. This must be considered in every non-trivial change.

---

## How to Contribute

### Workflow

1. **Fork** the repository on GitHub.
2. **Create a branch** from `main` using the naming convention described below.
3. **Implement your changes**, following the code style and architecture rules in this document.
4. **Write or update tests** to cover your changes.
5. **Open a Pull Request** against `main` with a complete description.

### Branch Naming

```
feat/<short-description>       # New features or components
fix/<short-description>        # Bug fixes
refactor/<short-description>   # Structural changes without behavior change
docs/<short-description>       # Documentation only
research/<short-description>   # Experimental or research-only branches
```

---

## Development Setup

```bash
# Fork and clone
git clone https://github.com/<your-username>/Mestrado-UML.git
cd Mestrado-UML

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-mock
```

### Running Tests

```bash
PYTHONPATH=. pytest tests/ -v
```

All tests must pass before a pull request will be reviewed.

---

## Code Style

This codebase targets an audience of both developers and academic researchers in quantum software engineering. Style must reflect this dual audience.

### General Rules

- **Python 3.10+** syntax only.
- Follow [PEP 8](https://pep8.org/) for formatting. Use 4-space indentation throughout.
- Use **type annotations** on all public method signatures.
- Write **docstrings** for all public classes and methods. Use Google-style docstring format.
- Avoid magic numbers — use named constants or parameters.
- Use descriptive variable names that reflect the physical meaning of the quantity (e.g., `theta_A`, `coupling_constants`, `beta_B`), not abbreviated identifiers.

### Modularity and Separation of Concerns

The single most important architectural constraint in this codebase is the **strict separation of classical, quantum, and hybrid logic**. This separation is not merely organizational — it is required for the UML models derived from this codebase to remain valid and meaningful.

- **`framework/classical/`** — No PennyLane or QuTiP imports. Pure Python logic only.
- **`framework/quantum/`** — PennyLane quantum circuits only. No optimization logic. No classical control flow beyond gate parameterization.
- **`framework/classical_quantum/`** — Hybrid classes that bridge the two. May import from both layers but must not contain raw gate definitions.

Any violation of this boundary is a blocking issue in code review.

### Readability for Modeling

Because this codebase is intended to be analyzed and modeled (UML extraction), clarity of intent is prioritized over brevity:

- Prefer explicit class hierarchies over duck typing.
- Use abstract base classes (`ABC`) for all families of interchangeable components.
- Avoid closures, lambdas, or anonymous functions in the core framework modules — these cannot be represented in UML.
- Prefer `@staticmethod` or `@classmethod` over module-level functions for utilities that belong to a class conceptually.

---

## Architecture Rules

The framework follows a strict three-layer architecture. Contributors **must not** mix responsibilities across layers.

### Layer Definitions

| Layer | Path | Responsibility |
|---|---|---|
| Classical | `framework/classical/` | Topology strategies, configuration, pure data structures |
| Quantum | `framework/quantum/` | Quantum gate sequences, Hamiltonian construction, PennyLane operations |
| Hybrid | `framework/classical_quantum/` | QNode orchestration, gradient estimation, optimization loops |

### Adding New Operation Types

When adding a new quantum operation (e.g., a new correlation model or Hamiltonian):

1. Create a subclass of the appropriate abstract base class (`CorrelationOperation`, `WorkOperation`, etc.) in `framework/quantum/operations.py`.
2. Implement the required abstract methods (`apply`, `_get_hamiltonian`, `_get_initial_params`).
3. Add unit tests in `tests/` verifying the circuit output shape and behavior.
4. Update the UML class diagram (see *UML Contributions* below) to include the new class.

### Adding New Topology Strategies

1. Subclass `Topology` from `framework/classical/topologies.py`.
2. Implement `get_pairs(num_qubits: int) -> list`.
3. Add unit tests covering all relevant values of `num_qubits`.
4. Do not import any quantum library in topology classes.

### Modifying `QuantumThermalMachine` or `ErgotropyOptimizer`

These are the highest-impact classes in the framework. Changes here affect:
- All simulation results.
- The sequence diagrams in the UML model.
- Any downstream academic analysis.

Changes to these classes require:
- A clear rationale in the PR description.
- Full test coverage.
- Explicit statement of architectural impact.
- Update to any relevant UML diagrams.

---

## UML Contributions

This project uses UML to formally model its architecture. The models are maintained in parallel with the code and must stay consistent with the implementation.

### When to Update UML Diagrams

Update the relevant diagrams whenever you:

- Add or remove a class, interface, or abstract class from the framework.
- Change the inheritance or dependency relationships between components.
- Add a new stage to the quantum thermodynamic cycle.
- Modify the interaction sequence between `ErgotropyOptimizer` and `QuantumThermalMachine`.

### Which Diagrams Are Affected

| Change Type | Affected Diagram(s) |
|---|---|
| New class / interface | Class Diagram |
| New operation or topology | Class Diagram |
| Modified optimization loop | Sequence Diagram |
| New thermodynamic stage | Activity Diagram + Sequence Diagram |

### Diagram Consistency Rules

- Every public class in `framework/` must have a corresponding element in the class diagram.
- Inheritance relationships in code must be represented as UML generalization arrows.
- Interface implementations must be represented as UML realization arrows.
- Dependency injection (receiving an operation class as a parameter) must be represented as UML dependency.

If you are unfamiliar with the UML Profile extensions used in this project (Pérez-Castillo or QuanUML stereotypes), note this in your PR and request a review from a maintainer with modeling expertise.

---

## Commit Messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/). All commit messages must follow this format:

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

### Types

| Type | When to Use |
|---|---|
| `feat` | New feature or component |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `docs` | Documentation changes only |
| `test` | Adding or modifying tests |
| `chore` | Tooling, configuration, dependency updates |
| `research` | Experimental changes not intended for production |

### Scope (optional but encouraged)

Use the module or component name: `topology`, `optimizer`, `operations`, `machine`, `thermodynamics`.

### Examples

```
feat(topology): add PairInternalRainbowTopology class
fix(optimizer): correct central finite difference sign convention
refactor(machine): decouple QNode initialization from device selection
docs(readme): update architecture overview with three-stage description
```

---

## Pull Requests

All pull requests must include the following in their description:

### Required Sections

```
## What This PR Does
[Brief description of the change and its purpose]

## Motivation
[Why this change is needed — problem being solved or improvement being made]

## Architectural Impact
[Which layers are affected? Does this change any class interfaces, hierarchies,
or dependency relationships? Are there implications for the hybrid execution model?]

## UML Updates
[List of UML diagrams that were updated, or explicit statement that no update
is required and why]

## Test Coverage
[Description of what was tested and how. Link to test files if applicable]
```

### Review Criteria

Pull requests will be evaluated on:

- Correctness of simulation behavior (verified by tests).
- Adherence to the three-layer architecture.
- Consistency with existing naming conventions.
- Completeness of docstrings.
- Consistency between code and UML diagrams (if applicable).
- Readability for the target audience (researchers and engineers).

---

## Issues

When opening an issue, choose the appropriate category:

### Bug Report

Include:
- Python version and OS.
- Minimal reproducible example.
- Observed vs. expected behavior.
- Stack trace (if applicable).

### Feature Request

Include:
- Physical or algorithmic motivation (not just implementation preference).
- Which framework layer the feature belongs to.
- Whether it would affect the UML models.

### Research Discussion

Issues may also be used to open discussions about:
- Alternative quantum thermodynamic models to implement.
- New UML Profile stereotypes for quantum constructs.
- Architectural decisions with implications for academic modeling.

Label these with `research` or `discussion` to distinguish them from implementation tasks.

---

## Questions

For questions about the physics, the UML models, or the research context, open an issue with the `question` label or contact the maintainers directly via the repository's contact information.
