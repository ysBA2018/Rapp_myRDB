# vim:set ft=Makefile ts=8:

it: clean netzwerk mariadb phpmyadmin

clean:
	-docker rm -f phpmyadmin
	-docker rm -f mariadb
	-docker network rm mariaNetz

netzwerk:
	docker network create mariaNetz

mariadb:
	docker run -d \
		--name mariadb \
		--network mariaNetz \
		--network-alias mysql \
		-p 13306:3306 \
		-e MYSQL_ROOT_PASSWORD=geheim \
		-v /home/lutz/datadir:/var/lib/mysql \
		mariadb:5.5.61-trusty


phpmyadmin:
	docker run -d \
		-p 8088:80 \
		--name phpmyadmin \
		--network mariaNetz \
		-e PMA_HOST=mysql \
		phpmyadmin/phpmyadmin

phpmyadmin_pma:
	docker run -d \
		-p 8088:80 \
		--name phpmyadmin \
		--network mariaNetz \
		-e PMA_HOST=mysql \
		-e PMA_CONTROLUSER=pma \
		-e PMA_CONTROLPASS=0oWiPLfdhAcSqy9TnmhKcI222QQIO87BvvjiHX9r57\
		phpmyadmin/phpmyadmin

