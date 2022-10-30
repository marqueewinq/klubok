build:
	heroku container:push web

deploy: push
	heroku container:release web
