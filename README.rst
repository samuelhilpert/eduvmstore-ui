EduVMStore
==========

Dieses Repo beinhaltet das UI für den EduVMStore, welcher unter folgendem Link gefunden werden kann:
https://github.com/samuelhilpert/eduvmstore.git

Installationsguide
------------------

1. Installiere DevStack.
2. Gehe in den Ordner ``Devstack``.
3. Öffne die Datei ``local.conf``.
4. Füge folgende Zeile als erste Zeile hinzu:
   
   ``ENABLE_PLUGIN eduvmstore-ui https://github.com/samuelhilpert/eduvmstore-ui main``
   
5. Führe im Ordner ``Devstack`` den Befehl aus:

   ``./stack.sh``

6. Nach erfolgreicher Ausführung ist der EduVMStore in DevStack als neues Dashboard nach der Anmeldung sichtbar.
