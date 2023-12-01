# OSPS
Pas de signaux simple (unix) en python 
écriture bufferisée dans les tubes 
.flush > open close (déjà bien)
segment mémoire partagé système 

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
