// Скрипт для переименования точек в Adobe Illustrator
function renameObjects() {
    if (app.documents.length === 0) {
        alert("Откройте документ с объектами!");
        return;
    }

    var doc = app.activeDocument;
    var selection = doc.selection;

    if (selection.length === 0) {
        alert("Выделите объекты, которые нужно переименовать.");
        return;
    }
    var k=55
    for (var i = 0; i < selection.length; i++) {
        var obj = selection[i];
        k++
        obj.name = "Node_" + (k); // Присваиваем уникальное имя, например, "Node_1", "Node_2"
    }

    alert("Переименование завершено! Присвоены имена: Node_k+1, Node_k+2, ...");
}

renameObjects();
