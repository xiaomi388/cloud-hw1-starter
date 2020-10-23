#!/bin/bash

OLDPWD=$(dirname "$0")

# shellcheck disable=SC2164
cd "${OLDPWD}/package"
zip -r9 "${OLDPWD}/function.zip" .

# shellcheck disable=SC2164
cd "${OLDPWD}"
zip -g function.zip lambda_function.py credential.py
aws lambda update-function-code --function-name cloud-hw1-lf2 --zip-file fileb://function.zip --region us-west-1

