# Victor.spaceAPI
Simple Python spaceAPI server with Slack integration

A simple Python server implementing space api 0.13 with slack integration

## Install
Clone the latest version

## Configure 
Adjust space.cfg and enter your space settings.


## Run
Running it with docker saves you the hassle of installing dependencies.

docker build -t spaceapi .

Start container

	docker run -d -p <external port>:5000 spaceapi
		
## Security
Don't enable slack integration when running on http (unencrypted)


## Enhance
Open an issue and we might add your feature or fix defects.

Fork and give back ;-)
