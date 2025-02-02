DOCK_COMPOSE_CMD :=	docker compose
DOCK_COMPOSE_FILE :=	docker-compose.yaml

all: build_folder build updetach

build_folder:
	mkdir -p $(HOME)/.tranceanddance/pgdata
	mkdir -p $(HOME)/.tranceanddance/backenddata

build up:
	$(DOCK_COMPOSE_CMD) -f $(DOCK_COMPOSE_FILE) $@

down kill:
	$(DOCK_COMPOSE_CMD) -f $(DOCK_COMPOSE_FILE) $@

buildclean:
	$(DOCK_COMPOSE_CMD) -f $(DOCK_COMPOSE_FILE) build --no-cache
	
updetach:
	$(DOCK_COMPOSE_CMD) -f $(DOCK_COMPOSE_FILE) up -d

show:
	@echo "\n Images:"
	@docker images
	@echo "\n Containers: "
	@docker ps
	@echo "\n Volumes: "
	@docker volume ls
	@echo "\n Networks: "
	@docker network ls --filter type=custom

run: down build updetach

re: down buildclean updetach

rmi:
	docker rmi $(shell docker images -aq) -f | true

clean:
	$(DOCK_COMPOSE_CMD) -f $(DOCK_COMPOSE_FILE) down --rmi local --remove-orphans

fclean: rmi
	$(DOCK_COMPOSE_CMD) -f $(DOCK_COMPOSE_FILE) down --rmi all -v --remove-orphans

resetall:
	@docker system prune -af
	@docker volume prune -af
	@docker image prune -af
	@rm -rf $(HOME)/.tranceanddance

.PHONY: all build up down kill updateach buildclean show run re clean fclean
