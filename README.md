# DVMP

BENÖTIGTE SOFTWARE: 
    - Blender >3.0
    - Python
    - cv2
    - numpy 
    - diese Dinger installieren !!!!!!!!!

Falls gewünscht kann ein eigenes Pattern erstellt werden. Es sind jedoch Test Pattern im Ordner zu finden: 
    - \DVMP\Pattern

EIGENE PATTERN ERSTELLEN:
    1. Diese 4 Farben nutzen
        Gras: green = (0, 255, 0)
        Busch: darkGreen = (53, 101, 20)
        Baum: brown = (143, 86, 59)
        Stein: blue = (0, 0, 255)

    2. Ein Pixel entspricht einer Unit in Blender (20 x 20 Meter)

    3. Mit einem Tool deiner Wahl ein Pattern erstellen als PNG abspeichern und in den Pattern Ordner legen.


PROGRAMM STARTEN:
    1. Blender starten

    2. Programmcode öffnen
        - Unter "terrainGeneratorPlugin.py" den "import_path" wie folgt anpassen.
            - C:/Users/.../DVMP/Exports/Gras
    
    3. In Blender Add-on installieren
        - Preferneces -> Add-ons -> terrainGeneratorPlugin.py installieren
        - Add-on aktivieren

    4. Import Pattern
        - Unter File -> Import -> Terrain Generator -> gewünschtes Pattern auswählen

Nun sollte eine Landschaft gemäß des Pattern in Blender angezeigt werden.
