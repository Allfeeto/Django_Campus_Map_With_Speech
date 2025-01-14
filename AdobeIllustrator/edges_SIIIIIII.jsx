// Скрипт для создания рёбер графа с учётом стен (существующие имена узлов)

function createEdges() {
    // Проверяем наличие документа
    if (app.documents.length === 0) {
        alert("Откройте документ с узлами и стенами.");
        return;
    }

    var doc = app.activeDocument;

    // Слой с узлами
    var nodesLayer = doc.layers.getByName("nodes"); // Укажите имя слоя с узлами
    // Слой с стенами
    var wallsLayer = doc.layers.getByName("Стены"); // Укажите имя слоя с контурами стен

    if (!nodesLayer || !wallsLayer) {
        alert("Убедитесь, что у вас есть слои с именами 'Узлы' и 'Стены'.");
        return;
    }

    var nodes = nodesLayer.pathItems;
    var walls = wallsLayer.pathItems;

    // Собираем координаты и имена узлов
    var nodeCoords = [];
    for (var i = 0; i < nodes.length; i++) {
        var node = nodes[i];
        if (node.name) {
            nodeCoords.push({
                id: node.name, // Берём существующее имя объекта
                x: node.position[0],
                y: node.position[1]
            });
        } else {
            alert("Узлу " + (i + 1) + " не задано имя. Пожалуйста, задайте имена всем узлам!");
            return;
        }
    }

    // Функция для проверки пересечения линии с контурами стен
    function intersectsWall(x1, y1, x2, y2) {
        for (var i = 0; i < walls.length; i++) {
            var wall = walls[i];
            var wallPath = wall.pathPoints;

            for (var j = 0; j < wallPath.length - 1; j++) {
                var wx1 = wallPath[j].anchor[0];
                var wy1 = wallPath[j].anchor[1];
                var wx2 = wallPath[j + 1].anchor[0];
                var wy2 = wallPath[j + 1].anchor[1];

                // Проверяем пересечение линии (x1, y1) -> (x2, y2) с отрезком (wx1, wy1) -> (wx2, wy2)
                if (checkLineIntersection(x1, y1, x2, y2, wx1, wy1, wx2, wy2)) {
                    return true;
                }
            }
        }
        return false;
    }

    // Алгоритм для проверки пересечения двух отрезков
    function checkLineIntersection(x1, y1, x2, y2, x3, y3, x4, y4) {
        var det = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3);
        if (det === 0) return false; // Линии параллельны

        var lambda = ((y4 - y3) * (x4 - x1) + (x3 - x4) * (y4 - y1)) / det;
        var gamma = ((y1 - y2) * (x4 - x1) + (x2 - x1) * (y4 - y1)) / det;

        return (0 < lambda && lambda < 1) && (0 < gamma && gamma < 1);
    }

    // Генерация рёбер
    var edges = [];
    for (var i = 0; i < nodeCoords.length; i++) {
        for (var j = i + 1; j < nodeCoords.length; j++) {
            var nodeA = nodeCoords[i];
            var nodeB = nodeCoords[j];

            // Проверяем, пересекает ли линия стену
            if (!intersectsWall(nodeA.x, nodeA.y, nodeB.x, nodeB.y)) {
                edges.push({
                    from: nodeA.id,
                    to: nodeB.id,
                    distance: Math.sqrt(
                        Math.pow(nodeB.x - nodeA.x, 2) + Math.pow(nodeB.y - nodeA.y, 2)
                    )
                });
            }
        }
    }

    // Сохраняем рёбра в файл CSV
    var file = File.saveDialog("Сохранить рёбра в CSV");
    if (file) {
        file.open("w");
        file.writeln("from,to,weight");
        for (var i = 0; i < edges.length; i++) {
            var edge = edges[i];
            file.writeln(edge.from + "," + edge.to + "," + Math.floor(edge.distance / 10));
        }
        file.close();
        alert("Рёбра сохранены в " + file.fullName);
    } else {
        alert("Сохранение отменено.");
    }
}

createEdges();
