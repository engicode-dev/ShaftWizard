import pytest
from services.bearings import calculate_required_capacity, select_bearing

def test_required_capacity():
    # Проверяем, что требуемая грузоподъемность считается правильно
    C_req = calculate_required_capacity(P=675.71, n=300, L_h=10000)
    assert C_req == pytest.approx(3815.20, rel=1e-3)

def test_select_bearing():
    # Проверяем, что для d=30 выбирается именно 206
    bearing = select_bearing(R=675.71, n=300, L_h=10000, d_required=30.0)
    assert bearing.designation == "206"
    assert bearing.d == 30.0
    assert bearing.C >= 3815.20

def test_select_bearing_too_large():
    # Проверяем, что если нагрузка слишком большая, будет ошибка (нет подходящего подшипника)
    with pytest.raises(ValueError):
        select_bearing(R=50000, n=300, L_h=10000, d_required=30.0)