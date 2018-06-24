rm -rf *.zip
zip -r userAdd.zip pymysql/ useradd.py
aws lambda update-function-code --function-name user_add --zip-file fileb://userAdd.zip --profile=dev
aws lambda update-function-configuration --function-name user_add --handler useradd.handler --profile=dev
