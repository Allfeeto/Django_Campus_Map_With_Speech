            floorMaps.forEach(floorDiv => {
                const svgContainer = floorDiv.querySelector('.svg-container');
                const floorSvg = svgContainer.querySelector('svg.floor-svg');
                const routeSvg = svgContainer.querySelector('svg.route-svg');


                let scale = 0.25;  // Начальный масштаб
                let startX, startY, touchStartX, touchStartY;
                let translateX = 0, translateY = 0; // Позиция
                let isDragging = false;

                // Применение начального масштаба
                floorSvg.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
                routeSvg.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;

                // Обработчик события масштабирования
                svgContainer.addEventListener('wheel', (e)  => {
                    e.preventDefault();

                    const scaleAmount = 0.1;
                    const oldScale = scale;

                    if (e.deltaY < 0) {
                        if (scale <= 1.7){
                            scale += scaleAmount; // Увеличение масштаба
                        }
                    } else {
                        scale = Math.max(0.25, scale - scaleAmount); // Минимальный масштаб
                    }

                    // Координаты курсора относительно контейнера
                    let rect = svgContainer.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;

                    // Вычисление сдвига для центрирования курсора
                    const offsetX = (mouseX - translateX) / oldScale;
                    const offsetY = (mouseY - translateY) / oldScale;

                    translateX = mouseX - offsetX * scale;
                    translateY = mouseY - offsetY * scale;

                    // Применяем масштаб для текущего этажа
                    clampPosition()
                    updateTransform();
                });

                // Перетаскивание карты
                svgContainer.addEventListener('mousedown', (e) => {
                    e.preventDefault(); // Отключаем выделение текста
                    isDragging = true;
                    startX = e.clientX - translateX;
                    startY = e.clientY - translateY;
                });

                svgContainer.addEventListener('mousemove', (e) => {
                    if (!isDragging) return;
                    translateX = e.clientX - startX;
                    translateY = e.clientY - startY;
                    clampPosition(); // Применить ограничения
                    updateTransform();
                });

                // Завершение перемещения карты (мышь)
                svgContainer.addEventListener('mouseup', () => isDragging = false);
                svgContainer.addEventListener('mouseleave', () => isDragging = false);

                // Функция для обновления трансформаций
                function updateTransform() {
                    // Применяем одинаковые трансформации для карты и маршрута
                    floorSvg.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
                    routeSvg.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;

                }



        let initialDistance = null;
        let initialCenter = null;
        // Хранение активных касаний
        let activeTouches = {};

        // Рассчитываем центр между двумя пальцами
        function getTouchCenter(touches) {
            const rect = svgContainer.getBoundingClientRect();
            const x = (touches[0].clientX + touches[1].clientX) / 2 - rect.left;
            const y = (touches[0].clientY + touches[1].clientY) / 2 - rect.top;
            return { x, y };
        }

        // Обработчики Pointer Events (Touch Events)
        svgContainer.addEventListener('touchstart', (e) => {
            // Добавляем активные касания
            for (let touch of e.changedTouches) {
                activeTouches[touch.identifier] = touch;
            }

            if (e.touches.length === 2) {
                // Масштабирование: два пальца
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                initialDistance = Math.sqrt(dx * dx + dy * dy);
                initialCenter = getTouchCenter(e.touches); // Сохраняем начальный центр
            } else if (e.touches.length === 1) {
                // Перетаскивание: один палец
                isDragging = true;
                const touch = e.touches[0];
                startTouchX = touch.clientX - translateX;
                startTouchY = touch.clientY - translateY;
                // e.preventDefault(); // Не требуется, если touch-action настроен правильно
            }
        }, { passive: false });

        svgContainer.addEventListener('touchmove', (e) => {
            if (e.touches.length === 2 && initialDistance) {
                e.preventDefault();

                // Вычисление расстояния между пальцами
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                const currentDistance = Math.sqrt(dx * dx + dy * dy);

                // Новый масштаб
                const scaleChange = currentDistance / initialDistance;
                const newScale = Math.max(0.25, scale * scaleChange); // Минимальный масштаб

                // Центр между пальцами относительно svgContainer
                const currentCenter = getTouchCenter(e.touches);

                // Обновляем смещение карты с учетом нового масштаба
                const offsetX = (currentCenter.x - translateX) / scale;
                const offsetY = (currentCenter.y - translateY) / scale;

                // Пересчитываем новые значения translateX и translateY относительно центра
                translateX = currentCenter.x - offsetX * newScale;
                translateY = currentCenter.y - offsetY * newScale;

                // Обновляем масштаб
                scale = newScale;
                initialDistance = currentDistance; // Обновляем расстояние

                // Применяем ограничения
                clampPosition();
                updateTransform();
            } else if (e.touches.length === 1 && isDragging) {
                // Перетаскивание с одним пальцем
                const touch = e.touches[0];
                translateX = touch.clientX - startTouchX;
                translateY = touch.clientY - startTouchY;

                // Применяем ограничения
                clampPosition();
                updateTransform();
            }
        }, { passive: false });

        // Завершаем масштабирование/перетаскивание
        svgContainer.addEventListener('touchend', (e) => {
            // Удаляем завершившиеся касания
            for (let touch of e.changedTouches) {
                delete activeTouches[touch.identifier];
            }

            if (e.touches.length === 2) {
                // Осталось два касания, продолжаем масштабирование
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                initialDistance = Math.sqrt(dx * dx + dy * dy);
                initialCenter = getTouchCenter(e.touches);
            } else if (e.touches.length === 1) {
                // Осталось одно касание, начинаем перетаскивание
                isDragging = true;
                const touch = e.touches[0];
                startTouchX = touch.clientX - translateX;
                startTouchY = touch.clientY - translateY;
                initialDistance = null;
                initialCenter = null;
            } else {
                // Нет касаний, завершаем взаимодействие
                isDragging = false;
                initialDistance = null;
                initialCenter = null;
            }
        }, { passive: false });

        svgContainer.addEventListener('touchcancel', (e) => {
            // Обработка отмены касаний
            for (let touch of e.changedTouches) {
                delete activeTouches[touch.identifier];
            }
            isDragging = false;
            initialDistance = null;
            initialCenter = null;
        }, { passive: false });








                // Ограничить координаты перемещения
                function clampPosition() {
                    // Получаем актуальные размеры контейнера
                    const containerWidth = svgContainer.offsetWidth;
                    const containerHeight = svgContainer.offsetHeight;

                    // Получаем актуальные размеры карты с учетом масштаба
                    const scaledWidth = 4500 * scale;
                    const scaledHeight = 2500 * scale;

                    // Лимиты по горизонтали
                    const minX = Math.min(0, containerWidth - scaledWidth);  // Слева (не можем выходить за пределы)
                    const maxX = 0;  // Справа (не можем двигаться вправо)

                    // Лимиты по вертикали
                    const minY = Math.min(0, containerHeight - scaledHeight);  // Снизу (не можем выходить вниз)
                    const maxY = 0;  // Сверху (не можем двигаться вверх)

                    // Применяем ограничения на координаты
                    translateX = Math.max(minX, Math.min(maxX, translateX));
                    translateY = Math.max(minY, Math.min(maxY, translateY));
                }




                // Функция для центрирования изображения в контейнере
                function centerMap() {
                    // Получаем размеры контейнера
                    const containerWidth = svgContainer.offsetWidth;
                    const containerHeight = svgContainer.offsetHeight;

                    // Получаем реальные размеры карты (например, через getBoundingClientRect)
                    const mapWidth = 4500;
                    const mapHeight = 2500;

                    // Рассчитываем смещение для центрирования карты (с учётом масштаба)
                    const scaledWidth = mapWidth * scale;
                    const scaledHeight = mapHeight * scale;

                    // Рассчитываем смещение для центрирования
                    translateX = (containerWidth - scaledWidth) / 2;
                    translateY = (containerHeight - scaledHeight) / 2;

                    // Применяем трансформацию (сдвиг и масштаб)
                    clampPosition()
                    updateTransform();
                }


                // Инициализация при загрузке страницы
                //window.addEventListener('load', centerMap);
                //window.addEventListener('resize', centerMap); // Центрируем карту при изменении размера окна// Обработчик события изменения размера окна







            });