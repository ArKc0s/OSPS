# OSPS
Pas de signaux simple (unix) en python 
écriture bufferisée dans les tubes 
.flush > open close (déjà bien)
segment mémoire partagé système 

1.a) Quel module utilisez-vous pour manipuler un segment mémoire partagé en Python 3 ?
Veillez à utiliser le module le plus « simple » possible tout en choisissant un module « officiel/maintenu/à jour ».

Pour manipuler un segment de mémoire partagé en Python 3 on utilise la librairie mmap. On crée une variable shared_mem qui contient un object mmap. On peut lire et écrire dans cette mémoire partagée à l'aide des fonctions .write pour écrire dedans et .read pour lire le contenue de la mémoire partagée. 

2.a) Prévoyez le code nécessaire pour arrêter proprement les serveurs après un certain nombre d’échanges (ping-pong).

2.b) Quel serveur doit s’arrêter en premier pour éviter les zombies ? Qu’est ce qu’un zombie au sens informatique /
système d’opération ?

C'est le serveur qui lance l'autre serveur qui doit s'arrêter en premier car si le serveur qui lance le second
Un zombie dans le sens informatique / système d'opération est un processus qui a terminé son éxécution, mais qui n'a pas encore été complétement supprimer du système car tant que le processus parent ne récupére pas les informations que le processus fils, le processus fils ne se termine pas et il passe en état de processus zombie.

3.a) Est-ce une bonne idée de lancer le serveur principal depuis le watch-dog puis les serveurs secondaires depuis le
serveur principal ? Sachant que le watch-dog peut être amené à stopper et redémarrer [tous] les autres processus ? Doit-il
déléguer le redémarrage d’un serveur secondaire au serveur principal, au risque de lui faire perdre en réactivité ?

3.b) Est-ce une bonne idée d’utiliser les tubes de communication entre les serveurs pour établir une communication entre
le watchdog et les serveurs ? Quelle est la conséquence si un serveur secondaire est figé et que le watch-dog lui donne
l’ordre de redémarrer via « son » tube nommé (dwtube1..dwtuben) ?

3.c) Comme illustré ci-dessous – sa ns forcément tout implémenter – ne serait-il pas judicieux d’utiliser des « signaux »
(au sens du système d’exploitation) ? Est-ce que le père d’un processus est informé de l’arrêt d’un processus fils par un
signal ?

1) Le client se connecte via un socket en TCP au port 2222 du serveur principal ;
2) Le client envoie un type de requête au serveur (pour les tests, « requetetype1 » ou « requetetype2 ») ;
3) Le serveur principal retourne un numéro de port > 2222, géré (en TCP) par le serveur secondaire ;
4) Il y a établissement d’une connexion directe en TCP entre le client et le serveurs secondaire chargé de la requête
du client ;
5) Le client et le serveur secondaire échangent quelques informations et coupent la connexion ;
6) Le client coupe la connexion avec le serveur principal, sauf s’il a une autre requête à soumettre, auquel cas
retour à l’étape 2
