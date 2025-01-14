// Создание файла для записи координат
var doc = app.activeDocument; // Получаем активный документ
var file = new File("C:/Users/10509/OneDrive/Documentos/Adobe Scripts/nodes2.csv"); // Файл будет сохранен на рабочем столе
file.open("w");

// Запись заголовков для CSV
file.writeln("id,x,y,floor");

// Перебор всех объектов на слое "nodes"
var layer = doc.layers.getByName("nodes"); // Слой с именем "nodes"

// Получаем первую монтажную область (artboard)
var artboard = doc.artboards[0]; // Если используется другая монтажная область, укажите её индекс
var artboardRect = artboard.artboardRect; // Координаты монтажной области [лево, верх, право, низ]
var artboardHeight = artboardRect[1] - artboardRect[3]; // Высота монтажной области
$.writeln("Высота монтажной области: " + artboardHeight);

var counter = 1; // Счетчик для автоматических имен

// Функция для обработки объектов на слое
function processItem(item, counter) {
    if (item.typename === "PathItem" && item.closed) {
        // Проверяем, есть ли имя у объекта
        var name = (item.name && item.name !== "Adobe Illustrator") ? item.name : "point_" + counter;

        // Получаем координаты центра объекта
        var position = item.position;
        var x = Math.round(position[0] + item.width / 2); // Центр по X с округлением
        var y = Math.round(artboardRect[1] - (position[1] + item.height / 2)); // Центр по Y с округлением
        var floor = 2; // Этаж (в данном случае всегда 1)

        // Записываем в CSV
        file.writeln(name + "," + x + "," + y + "," + floor);
        counter++;
    } else if (item.typename === "GroupItem" || item.typename === "CompoundPathItem") {
        // Если это группа или составной объект, обрабатываем его содержимое
        for (var j = 0; j < item.pageItems.length; j++) {
            counter = processItem(item.pageItems[j], counter);
        }
    }
    return counter;
}

// Перебор всех объектов на слое "nodes"
for (var i = 0; i < layer.pageItems.length; i++) {
    counter = processItem(layer.pageItems[i], counter);
}

// Закрытие файла
file.close();
