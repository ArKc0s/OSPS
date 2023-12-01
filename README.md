# OSPS

## Instructions de lancement du projet

<b>Il faut d'abord executer le ficher watchdog.py qui se chargera de lancer lui même les deux serveurs.</b>

```
python3 watchdog.py
```

<b>Lorsque les deux serveurs sont prêts, on peut lancer le client</b>

```
python3 client.py
```


## Parcours de réflexion 

### Dans un premier temps, nous avons testé un premier parcours
1) Le client envoie une requête au serveur principal (dispatcher) vià une socquette 
2) Le serveur principal préviens le serveur secondaire (worker) qu'il a une requête à traiter dans la mémoire partagée vià un ping dans un tuple
3) Le serveur secondaire éxécute la requête et préviens par un pong dans un tuple que le résultat de la requête se trouve dans la mémoire
4) Le serveur principal envoie la réponse au client vià une socquette 

### Par la suite, nous sommes partis sur la solution alternative
1) le client crée le premier contact avec le serveur principal (dispatcher) pour l'informer qu'il à une requête à lui faire faire vià une socquette 
2) le serveur principal informe le serveur secondaire (worker) qu'il a du travail pour lui et lui indique vià la mémoire partagé l'IP et le port du client (le port utilisé est le même que celui utilisé lors de la connexion initiale entre le client et le serveur principal) en envoyant un ping dans un tuple 
3) le serveur secondaire contact le client vià l'IP et le port en mémoire partagé pour lui indiquer qu'il est prêt à travailler et attends la requête grâce à une socquette 
4) le client donne la requête au serveur secondaire qu'il doit faire pour lui vià une socquette 
5) après avoir éxécuté la requête, le serveur secondaire renvoie la réponse au client par le biais d'une socquette 
6) le serveur secondaire informe le serveur principal qu'il a fini la requête du client et qu'il est de nouveau prêt à recevoir une demande en lui envoyant un pong par un tuple 

### Pour finir sur la partie sans watchdog, nous avons implémenté la solution idéale
Par rapport à la solution précédente, ce n'est plus le serveur secondaire (worker) qui contact directement le client mais c'est le client qui va contacter le serveur secondaire. Pour cela, au lieu de trasmettre l'IP et le port du client, c'est le serveur secondaire qui va indiquer au serveur principal son IP et le port sur lequel le client pourra le contacter pour sa requête. Le serveur principal transmets ces informations au client et ce dernier contact directement le serveur secondaire. Les autres étapes du procédé reste les mêmes. 

### Implémentation du Watchdog

Nous avons réussi à implémenter un watchdog fonctionnel, cependant il n'est pas parfait. Nous sommes partis sur la piste du socket : le watchdog se connecte par socket aux deux serveurs et les ping en atttendant un pong. Si le délai d'attente est dépassé le watchdog redémarre les serveurs.

Le seul problème étant l'absence de réponse quand le serveur traite une autre requête, ce qui entraine un kill des serveurs inutiles. Pour contourner ce problème nous avons choisi de placer le ping/pong du watchdog dans des threads séparés sur les serveurs. C'est là que notre watchdog n'est pas parfait car, si le serveur plante, le thread plantera aussi et le watchdog redémarrera le serveur. Par contre, si le serveur reste bloqué dans l'execution d'un requête, le thread continuera de répondre aux pings du watchdog et le serveur ne sera pas tué.


