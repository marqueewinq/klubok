build:
	heroku container:push web

deploy:
	heroku container:release web
