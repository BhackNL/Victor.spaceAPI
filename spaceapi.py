from flask import Flask,jsonify, render_template
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
class Configuration(object):
	"""
	Configuration loader
	"""
	def __init__(self, *file_names):
		parser = SafeConfigParser()
		parser.optionxform = str
		found = parser.read(file_names)
		if not found:
			raise ValueError('No config file found!')
		for name in section_names:
			self.__dict__.update(parser.items(name))

config = Configuration('space.cfg')
config.state=False
config.lastchange=int(time.time())


def SlackWebhook(message,channel="#general"):
	"""
	Slack webhook for callbacks to channel

	Configure a webhook in slack and set slack.webhookurl in the config
	"""
	payload={"text": message,"channel": channel}
	r = requests.post(config.webhookurl,data=payload)
	return r.text


class SpaceApi(Resource):
	"""
	Space API endpoint

	Implements api version 0.13, see http://spaceapi.net/
	This is work in progress
	"""

	def get(self):
		"""
		Respond to GET, api version 0.13 compliant
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
		#TODO: work out ini to dictionary
		data['feeds']={"blog": {"type":"rss","url":"http://bhack.nl/feed"}}
		data['projects']=config.projects.split(',')
		return jsonify(data)


class SlackApi(Resource):
	"""
	Slack slash commands

	Endpoint for  Slack Slash Commands integration
	Configure this integration in slack en set token in de config.
	"""

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
			elif command == "state":
				if config.state:
					status="open"
				else:
					status="closed"
				return "The space is "+status+"since "+time.strftime("%d %b, %H:%M",time.localtime(config.lastchange)),200
			else:
				return "Unknown command, valid commmands are: open, close, state",403
		else:
			return "SpaceAPI, token mismatch",403

class IndexPage(Resource):
    def get(self):
        return {'page': 'notfound'}

@app.route('/SpacestateWidget')
def spacestatewidget():
	return render_template('spacestate.html',state=config.state)


api.add_resource(IndexPage, '/')

# Bhack legacy change this asap
api.add_resource(SpaceApi, '/SpaceApi')
api.add_resource(SlackApi, '/api/slack')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
