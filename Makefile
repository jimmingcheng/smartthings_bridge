.PHONY: deploy
deploy:
	rm deploy.zip
	zip -r deploy.zip AWSIoTPythonSDK/ resources/ smartthings_bridge/ lambda_function.py
	aws lambda update-function-code --function-name smartthings_bridge --zip-file 'fileb://deploy.zip'
