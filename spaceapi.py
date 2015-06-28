from flask import Flask,jsonify
from flask_restful import Resource, Api, reqparse
from ConfigParser import SafeConfigParser
import time
import requests

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('token', type=str)
parser.add_argument('text', type=str)
parser.add_argument('user_name', type=str)


section_names = 'spaceapi', 'slack'
class SpaceConfiguration(object):

    def __init__(self, *file_names):
        parser = SafeConfigParser()
        parser.optionxform = str 
        found = parser.read(file_names)
        if not found:
            raise ValueError('No config file found!')
        for name in section_names:
            self.__dict__.update(parser.items(name)) 
			
config = SpaceConfiguration('space.cfg')
config.state=False
config.lastchange=int(time.time())

def SlackWebhook(message,channel="#general"):
	payload={"text": message,"channel": channel}
	r = requests.post(config.slackwebhookurl,data=payload)
	return r.text

class SpaceApi(Resource):
	"""Space Stub at first"""
	
	def __init__(self):
		"""Check space config ?"""

	def get(self):
		"""Respond to GET, api version 0.13 compliant
		Validate spaceapi json at http://spaceapi.net/validator
		"""
		data={}
		data['api']=config.apiversion
		data['space']=config.spacename
		data['logo']=config.logo
		data['url']=config.url
		data['location']={"address":config.address,"lat": config.lat,"lon": config.lon}
		data['state']={"open": config.state,"lastchange": config.lastchange,"trigger_person":config.trigger_person,"message": config.message}
		data['contact']={"irc":config.irc,"twitter":config.twitter,"email":config.email}
		data['issue_report_channels']=config.issue_report_channels.split(',')
		data['feeds']={"blog": {"type":"rss","url":"http://bhack.nl/feed"}}
		data['projects']=config.projects.split(',')
		return jsonify(data)

class SlackApi(Resource):
	"""Slack slash commands integration"""
	
	def get(self):
		return {}
		
	def post(self):
		args = parser.parse_args()
		if args['token'] == config.token:
			command=args['text'].split()[0]
			if command == "open":
				config.state=True
				config.trigger_person=args['user_name']
				config.lastchange=time.time() 
 				return "The space is now open",200			
			elif command == "close":
				config.state=False
				config.trigger_person=args['user_name']
				config.lastchange=time.time() 
				return "The space is now closed",200
			else:
				return "Unknown command, valid commmands are: open, close",403
		else:
			return "SpaceAPI, token mismatch",403

class IndexPage(Resource):
    def get(self):
        return {'space': 'bhack'}


api.add_resource(IndexPage, '/')

# Bhack legacy remove this asap
api.add_resource(SpaceApi, '/SpaceApi') 

api.add_resource(SpaceApi, '/api/space')
api.add_resource(SlackApi, '/api/slack')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')