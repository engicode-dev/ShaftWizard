import FreeCAD as App
import Part


def build_shaft(steps, filename):
    doc = App.newDocument("Shaft")

    # Строим точки профиля
    points = [App.Vector(0, 0, 0)]
    current_x = 0.0

    for d, length in steps:
        radius = d / 2.0
        points.append(App.Vector(current_x, radius, 0))
        current_x += length
        points.append(App.Vector(current_x, radius, 0))

    points.append(App.Vector(current_x, 0, 0))

    # Вращаем
    wire = Part.makePolygon(points)
    face = Part.Face(wire)
    shaft = face.revolve(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 360)

    part_obj = doc.addObject("Part::Feature", "Shaft")
    part_obj.Shape = shaft

    # Сохраняем файл с заданным именем
    doc.saveAs(filename)
    print(f"✅ Файл сохранен: {filename}")


# Для теста из консоли:
if __name__ == "__main__":
    test_steps = [(25, 42), (30, 20), (35, 10), (40, 50), (45, 10), (35, 10), (30, 20), (25, 30)]
    build_shaft(test_steps, "shaft_output.FCStd")