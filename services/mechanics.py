import math
from models import Loads


def calculate_reactions(loads: Loads) -> dict:
    """Расчет реакций опор в двух плоскостях."""
    # Горизонтальная (F_t)
    R_Ax = loads.F_t * loads.b / loads.L
    R_Bx = loads.F_t * loads.a / loads.L

    # Вертикальная (F_r)
    R_Ay = loads.F_r * loads.b / loads.L
    R_By = loads.F_r * loads.a / loads.L

    # Суммарные реакции
    R_A = math.sqrt(R_Ax ** 2 + R_Ay ** 2)
    R_B = math.sqrt(R_Bx ** 2 + R_By ** 2)

    return {
        "R_Ax": R_Ax, "R_Bx": R_Bx,
        "R_Ay": R_Ay, "R_By": R_By,
        "R_A": R_A, "R_B": R_B
    }


def calculate_moments(loads: Loads) -> dict:
    """Расчет изгибающих моментов в опасном сечении."""
    R_Ax = loads.F_t * loads.b / loads.L
    R_Ay = loads.F_r * loads.b / loads.L

    M_x_max = R_Ax * loads.a
    M_y_max = R_Ay * loads.a

    M_sum = math.sqrt(M_x_max ** 2 + M_y_max ** 2)
    M_eq = math.sqrt(M_sum ** 2 + loads.T ** 2)

    return {
        "M_x": M_x_max,
        "M_y": M_y_max,
        "M_sum": M_sum,
        "M_eq": M_eq
    }


def calculate_min_diameter(M_eq: float, sigma_dop: float = 60.0) -> float:
    """Минимальный диаметр вала по эквивалентному моменту."""
    return (32 * M_eq / (math.pi * sigma_dop)) ** (1 / 3)