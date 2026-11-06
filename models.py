from dataclasses import dataclass
from typing import Optional

@dataclass
class Loads:
    """Нагрузки, действующие на вал."""
    F_t: float              # Окружная сила, Н
    F_r: float              # Радиальная сила, Н
    T: float                # Крутящий момент, Н*мм
    L: float                # Расстояние между опорами, мм
    a: float                # Плечо до колеса (слева), мм
    b: float                # Плечо до колеса (справа), мм

@dataclass
class ShaftGeometry:
    """Геометрия ступеней вала."""
    # Пока опишем только те ступени, которые нужны для расчета
    d_under_seal: float = 25.0
    d_under_bearing: float = 30.0
    d_under_gear: float = 40.0
    l_under_seal: float = 42.0
    l_under_bearing: float = 20.0
    l_under_gear: float = 50.0

@dataclass
class Bearing:
    """Модель подшипника из справочника."""
    designation: str        # Обозначение (например, "206")
    d: float                # Внутренний диаметр, мм
    D: float                # Наружный диаметр, мм
    B: float                # Ширина, мм
    C: float                # Динамическая грузоподъемность, Н
    C0: float               # Статическая грузоподъемность, Н