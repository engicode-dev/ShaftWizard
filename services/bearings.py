import json
import math
from pathlib import Path
from models import Bearing


def load_bearings() -> list[Bearing]:
    """Загружает справочник подшипников из JSON."""
    # Ищем файл data/bearings.json относительно корня проекта
    base_dir = Path(__file__).resolve().parent.parent
    json_path = base_dir / "data" / "bearings.json"

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return [Bearing(**item) for item in data]


def calculate_required_capacity(P: float, n: float, L_h: float) -> float:
    """
    Вычисляет требуемую динамическую грузоподъемность (C_req).
    P - эквивалентная динамическая нагрузка (Н)
    n - частота вращения (об/мин)
    L_h - ресурс в часах
    """
    # Формула: C_req = P * (60 * n * L_h / 10^6)^(1/3)
    # Для шарикоподшипников показатель степени p = 3
    term = (60 * n * L_h) / 1_000_000
    return P * (term ** (1 / 3))


def select_bearing(R: float, n: float, L_h: float = 10000.0, d_required: float = None) -> Bearing:
    """
    Подбирает подшипник по радиальной нагрузке R и требуемому диаметру d_required.
    """
    # 1. Эквивалентная динамическая нагрузка (упрощенно, без осевой силы)
    # P = V * X * F_r * K_б * K_т
    # V=1, X=1, K_б=1, K_т=1
    P = R

    # 2. Требуемая грузоподъемность
    C_req = calculate_required_capacity(P, n, L_h)

    # 3. Загружаем справочник
    bearings = load_bearings()

    # 4. Фильтруем по диаметру (если задан) и по грузоподъемности
    suitable = []
    for b in bearings:
        if d_required is not None and b.d != d_required:
            continue
        if b.C >= C_req:
            suitable.append(b)

    # 5. Сортируем по грузоподъемности (берем самый близкий по запасу)
    if not suitable:
        raise ValueError(f"Нет подшипника с d={d_required} и C >= {C_req:.1f} Н")

    suitable.sort(key=lambda b: b.C)
    return suitable[0]