venv: requirements.txt
	rm -rf venv/
	virtualenv -p python3.6 venv
	venv/bin/pip install -r requirements.txt

.PHONY: package
package: venv
	rm -rf build/
	mkdir build/
	cp -r venv/lib/python3.6/site-packages/* build/
	cp -r resources/ build/
	cp -r smartthings_bridge/ build/
	cp -r lambda_function.py build/
	cd build;zip -r deploy.zip .

.PHONY: deploy
deploy: package
	aws lambda update-function-code \
	--function-name $(ALEXA_FUNC_NAME) \
	--region $(ALEXA_REGION) \
	--zip-file 'fileb://build/deploy.zip'

.PHONY: clean
clean:
	rm -rf venv/
	rm -rf build/
