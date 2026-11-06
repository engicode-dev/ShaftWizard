import pytest
from models import Loads
from services.mechanics import calculate_reactions, calculate_moments, calculate_min_diameter


def test_reactions():
    loads = Loads(F_t=1270, F_r=462, T=127000, L=250, a=125, b=125)
    reactions = calculate_reactions(loads)

    # Реакции должны быть равны, так как нагрузка по центру
    assert reactions["R_A"] == pytest.approx(675.71, rel=1e-2)
    assert reactions["R_B"] == pytest.approx(675.71, rel=1e-2)

    # Проверка компонентов
    assert reactions["R_Ax"] == pytest.approx(635.0)
    assert reactions["R_Ay"] == pytest.approx(231.0)


def test_moments():
    loads = Loads(F_t=1270, F_r=462, T=127000, L=250, a=125, b=125)
    moments = calculate_moments(loads)

    assert moments["M_sum"] == pytest.approx(84463.93, rel=1e-4)
    assert moments["M_eq"] == pytest.approx(152522.64, rel=1e-4)


def test_min_diameter():
    d_min = calculate_min_diameter(M_eq=152522.64, sigma_dop=60.0)
    assert d_min == pytest.approx(29.58, rel=1e-2)