# Tools
## 1. Login Checker
Checks the login form specified by URL to form by user.

REQUIRED CLI TOOLS:
* Hydra
* Wordlist [ex1](https://github.com/kkrypt0nn/wordlists/tree/main/passwords)
* Redis with VectorSearch docker run
```console 
$ docker run -d --name redis-stack -p 6379:6379 redis/redis-stack-server:latest
$ docker exec -it redis-stack redis-cli
```