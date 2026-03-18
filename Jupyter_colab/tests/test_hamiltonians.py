import pytest
import pennylane as qml
from src.core.hamiltonians import HeisenbergXX, HeisenbergXY, IsotropicHeisenberg

def test_heisenberg_xx():
    pairs = [(0, 1), (1, 2)]
    couplings = [1.0, 1.5]
    builder = HeisenbergXX(pairs, couplings)
    obs = builder.build()
    
    # Verifica o tipo do observável (SProd ou Sum dependendo de como qml.dot retorna)
    assert obs is not None
    # Podemos avaliar os termos
    coeffs, terms = obs.terms()
    assert len(terms) == 2
    assert coeffs == [1.0, 1.5]
    assert type(terms[0]) == qml.ops.Prod
    
def test_heisenberg_xy():
    pairs = [(0, 1)]
    # XY precisa de Y e X, logo 2 couplins por par
    couplings = [1.0, 1.5]
    builder = HeisenbergXY(pairs, couplings)
    obs = builder.build()
    
    coeffs, terms = obs.terms()
    assert len(terms) == 2
    assert coeffs == [1.0, 1.5]
    assert type(terms[0]) == qml.ops.Prod

def test_isotropic_heisenberg():
    pairs = [(0, 1)]
    # XYZ precisa de 3 couplins por par
    couplings = [1.0, 1.5, 2.0]
    builder = IsotropicHeisenberg(pairs, couplings)
    obs = builder.build()
    
    coeffs, terms = obs.terms()
    assert len(terms) == 3
    assert coeffs == [1.0, 1.5, 2.0]
    assert type(terms[0]) == qml.ops.Prod
