lint:
	pylint --rcfile=.pylintrc ./collector/ --init-hook='sys.path.extend(["./collector/"])'
build:
	docker build -t spentless-collector .
