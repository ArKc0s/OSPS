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

Cela dépends mais à premier vue ce n'est pas une très bonne idée. Sachant que le watch-dog lance déjà le serveur principal et qu'il peut être amené à stopper tous les autres processus cela semble plus logique qu'il lance également le serveur secondaire. De plus cela permet d'éviter le risque de faire perdre de la réactivité au serveur principal 

3.b) Est-ce une bonne idée d’utiliser les tubes de communication entre les serveurs pour établir une communication entre
le watchdog et les serveurs ? Quelle est la conséquence si un serveur secondaire est figé et que le watch-dog lui donne
l’ordre de redémarrer via « son » tube nommé (dwtube1..dwtuben) ?

Ce n'est pas une bonne idée que le watch-dog utilise les tubes de communication entre les serveurs pour établir une communication entre le watch-dog et les serveurs car l'intérvention d'une troisième entitié sur un tuple ne se passe pas toujours bien car si plusieurs entités ont accèes en écriture au même tuple, il peut y avoir des conflits de données si elles essaient de modifier le tuple simultanément. Si le serveur secondaire est figé et que le watch-dog lui donne l'odre de redémarrer, celui-ci ne redémarrera pas forcément car si il est complétement figé, il ne pourra pas éxécuter l'odre du watch-dog car il ne pourra pas lire la demande qui arrive dans son tube nommé. Il se peut même que le serveur principal soit entrain d'écrire dans le tube nommé, ce qui engendré des conflits d'écriture.


3.c) Comme illustré ci-dessous – sa ns forcément tout implémenter – ne serait-il pas judicieux d’utiliser des « signaux »
(au sens du système d’exploitation) ? Est-ce que le père d’un processus est informé de l’arrêt d’un processus fils par un
signal ?

L'utilisation des signaux n'est pas 

1) Le client se connecte via un socket en TCP au port 2222 du serveur principal ;
2) Le client envoie un type de requête au serveur (pour les tests, « requetetype1 » ou « requetetype2 ») ;
3) Le serveur principal retourne un numéro de port > 2222, géré (en TCP) par le serveur secondaire ;
4) Il y a établissement d’une connexion directe en TCP entre le client et le serveurs secondaire chargé de la requête
du client ;
5) Le client et le serveur secondaire échangent quelques informations et coupent la connexion ;
6) Le client coupe la connexion avec le serveur principal, sauf s’il a une autre requête à soumettre, auquel cas
retour à l’étape 2

Dans un premier temps, nous avons tester un premier parcours qui est le suivant : 
1) Le client envoie une requête au serveur principal (dispatcher) vià une socquette 
2) Le serveur principal préviens le serveur secondaire (worker) qu'il a une requête à traiter dans la mémoire partagée vià un ping dans un tuple
3) Le serveur secondaire éxécute la requête et préviens par un pong dans un tuple que le résultat de la requête se trouve dans la mémoire
4) Le serveur principal envoie la réponse au client vià une socquette 

Par la suite, nous sommes partis sur la solution alternative qui consiste : 
1) le client crée le premier contact avec le serveur principal (dispatcher) pour l'informer qu'il à une requête à lui faire faire vià une socquette 
2) le serveur principal informe le serveur secondaire (worker) qu'il a du travail pour lui et lui indique vià la mémoire partagé l'IP et le port du client (le port utilisé est le même que celui utilisé lors de la connexion initiale entre le client et le serveur principal) en envoyant un ping dans un tuple 
3) le serveur secondaire contact le client vià l'IP et le port en mémoire partagé pour lui indiquer qu'il est prêt à travailler et attends la requête grâce à une socquette 
4) le client donne la requête au serveur secondaire qu'il doit faire pour lui vià une socquette 
5) après avoir éxécuté la requête, le serveur secondaire renvoie la réponse au client par le biais d'une socquette 
6) le serveur secondaire informe le serveur principal qu'il a fini la requête du client et qu'il est de nouveau prêt à recevoir une demande en lui envoyant un pong par un tuple 

Pour finir sur la partie sans watchdog, nous avons implémenté la solution idéale :
Par rapport à la solution précédente, ce n'est plus le serveur secondaire (worker) qui contact directement le client mais c'est le client qui va contacté le serveur secondaire. Pour cela, au lieu de trasmettre l'IP et le port du client, c'est le serveur secondaire qui va indiquer au serveur principal son IP et le port sur lequel le client pourra le contacter pour sa requête. Le serveur principal transmets ces informations au client et ce dernier contact directement le serveur secondaire. Les autres étapes du procédé reste les mêmes. 
