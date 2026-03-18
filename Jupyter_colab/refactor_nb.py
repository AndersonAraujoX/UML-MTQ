import json
import sys

def refactor_notebook(filepath):
    print(f"Refactoring {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = "".join(cell.get('source', []))
            
            # Substituto para Quantum_Circuits_Emulation e Quantum_Circuits
            if "class Quantum_Circuits_Emulation:" in source or "class Quantum_Circuits:" in source:
                print(f"  - Encontrado Quantum_Circuits_Emulation/Quantum_Circuits. Substituindo por imports.")
                cell['source'] = [
                    "from src.core.quantum_system import QuantumThermalMachine\n",
                    "from src.core.hamiltonians import IsotropicHeisenberg, HeisenbergXY, HeisenbergXX\n",
                    "from src.core.operations import ThermalizationOperation, ParametricCorrelation, IsotropicCorrelation\n"
                ]
            
            # Substituto para QuantumMachineLearning
            if "class QuantumMachineLearning:" in source:
                print(f"  - Encontrado QuantumMachineLearning. Substituindo por imports.")
                cell['source'] = [
                    "from src.optimization.ergotropy_optimizer import ErgotropyOptimizer\n"
                ]
                
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print(f"Finished {filepath}.")

if __name__ == '__main__':
    refactor_notebook('RO_19.ipynb')
    refactor_notebook('RO_20.ipynb')
