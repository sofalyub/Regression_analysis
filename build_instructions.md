# Инструкция по сборке и запуску приложения Regression_Analysis

## Требования

Убедитесь, что у вас установлен Python 3.8 или выше, а также все зависимости из файла `requirements.txt`:

```
pip install -r requirements.txt
```

## Сборка приложения с помощью PyInstaller

### Шаг 1: Установка PyInstaller

```
pip install pyinstaller
```

### Шаг 2: Сборка приложения

Для создания автономного исполняемого файла выполните:

```
pyinstaller --name Regression_Analysis --onefile --windowed --icon=fonts/app_icon.ico main.py
```

Параметры:
- `--name Regression_Analysis` - задает имя выходного файла
- `--onefile` - создает один исполняемый файл вместо папки с файлами
- `--windowed` - запуск без консольного окна (для GUI-приложений)
- `--icon=fonts/app_icon.ico` - задает иконку приложения (путь может отличаться)

### Шаг 3: Дополнительные файлы (опционально)

Если ваше приложение использует внешние файлы (например, конфигурационные файлы, шрифты), которые должны находиться рядом с исполняемым файлом, добавьте их с помощью параметра `--add-data`:

```
pyinstaller --name Regression_Analysis --onefile --windowed --icon=fonts/app_icon.ico --add-data "fonts/*;fonts/" main.py
```

## Местоположение скомпилированного приложения

После успешной сборки исполняемый файл будет находиться в папке `dist/`:
- Windows: `dist/Regression_Analysis.exe`

## Процесс запуска приложения

1. Когда пользователь запускает файл `Regression_Analysis.exe`, PyInstaller сначала создает временную папку в системном временном каталоге.
2. В эту папку распаковываются все необходимые библиотеки, модули Python и другие зависимости.
3. Запускается Python интерпретатор, который загружает ваш скрипт `main.py` и выполняет его.
4. После завершения работы программы временная папка автоматически удаляется.

## Создание установщика (опционально)

Для создания полноценного установщика можно использовать:
- NSIS (Nullsoft Scriptable Install System) - для Windows
- Inno Setup - для Windows

## Возможные проблемы и их решения

1. **Скрытые импорты**: PyInstaller может не обнаружить некоторые динамические импорты. Если возникают ошибки, используйте опцию `--hidden-import`:
   ```
   pyinstaller --hidden-import=имя_модуля main.py
   ```

2. **Проблемы с путями к файлам**: В скомпилированном приложении пути к файлам работают иначе. Вместо относительных путей используйте:
   ```python
   import os
   import sys
   
   # Получение пути к директории с исполняемым файлом
   if getattr(sys, 'frozen', False):
       # Путь при запуске скомпилированного приложения
       application_path = os.path.dirname(sys.executable)
   else:
       # Путь при запуске из Python
       application_path = os.path.dirname(os.path.abspath(__file__))
   
   # Пример использования пути к файлу
   config_path = os.path.join(application_path, 'config.ini')
   ```

3. **Уменьшение размера**: Для уменьшения размера используйте UPX:
   ```
   pip install pyinstaller-hooks-contrib
   pyinstaller --onefile --windowed --upx-dir=путь/к/upx main.py
   ``` 