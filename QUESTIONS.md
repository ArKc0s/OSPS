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

Cela dépends mais à premier vue ce n'est pas une très bonne idée. Sachant que le watch-dog lance déjà le serveur principal et qu'il peut être amené à stopper tous les autres processus cela semble plus logique qu'il lance également le serveur secondaire. De plus cela permet d'éviter le risque de faire perdre de la réactivité au serveur principal 

3.b) Est-ce une bonne idée d’utiliser les tubes de communication entre les serveurs pour établir une communication entre
le watchdog et les serveurs ? Quelle est la conséquence si un serveur secondaire est figé et que le watch-dog lui donne
l’ordre de redémarrer via « son » tube nommé (dwtube1..dwtuben) ?

Ce n'est pas une bonne idée que le watch-dog utilise les tubes de communication entre les serveurs pour établir une communication entre le watch-dog et les serveurs car l'intérvention d'une troisième entitié sur un tuple ne se passe pas toujours bien car si plusieurs entités ont accèes en écriture au même tuple, il peut y avoir des conflits de données si elles essaient de modifier le tuple simultanément. Si le serveur secondaire est figé et que le watch-dog lui donne l'odre de redémarrer, celui-ci ne redémarrera pas forcément car si il est complétement figé, il ne pourra pas éxécuter l'odre du watch-dog car il ne pourra pas lire la demande qui arrive dans son tube nommé. Il se peut même que le serveur principal soit entrain d'écrire dans le tube nommé, ce qui engendré des conflits d'écriture.


3.c) Comme illustré ci-dessous – sa ns forcément tout implémenter – ne serait-il pas judicieux d’utiliser des « signaux »
(au sens du système d’exploitation) ? Est-ce que le père d’un processus est informé de l’arrêt d’un processus fils par un
signal ?

Utiliser des signaux pour surveiller les processus présente des défis. Les signaux peuvent entraîner des problèmes de synchronisation et des comportements inattendus s'ils ne sont pas correctement gérés. Par exemple, l'envoi multiple de signaux pourrait écraser des signaux précédents non traités. De plus, les erreurs dans la gestion des signaux peuvent causer la terminaison imprévue de processus. Ainsi, bien que les signaux offrent une manière de recevoir des notifications des processus fils, leur utilisation nécessite une grande prudence et une gestion attentive. Le père d'un processus est informé de l'arrêt d'un processus fils par l'intermédiaire de signaux et peut récupérer des informations supplémentaires sur l'état de sortie du processus fils
