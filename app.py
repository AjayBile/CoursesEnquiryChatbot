from flask import Flask, request, make_response
import os, json
from flask_cors import cross_origin
from Scripts import logger
from Scripts import template_reader
from Scripts.config_reader import ConfigReader
from Scripts.MailSending import SendMails

app = Flask(__name__)

"""geting and sending response to dialogflow"""

@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():

    req = request.get_json(silent=True, force=True)

    """Sending an Input Student Request Data For Processing"""
    res = processRequest(req)

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

"""processing the request from dialogflow"""

def processRequest(req):
    log = logger.Log()

    sessionID=req.get('responseId')

    result = req.get("queryResult")
    user_says=result.get("queryText")
    log.write_log(sessionID, "User Says: "+user_says)
    parameters = result.get("parameters")

    log.write_log(sessionID, "Data recieved from customer is "+str(parameters))

    """Creating Dictionary Of Customer Data"""

    custInfoDict = {}
    custInfoDict['cust_name'] = parameters.get("name")
    custInfoDict['cust_email'] = parameters.get("email")
    custInfoDict['course_name'] = parameters.get("courses")[0]
    custInfoDict['cust_contact'] = parameters.get("phone")

    intent: str = result.get("intent").get('displayName')

    if (intent=='course_selection'):

        """Reading Default Configuration File"""

        config_reader = ConfigReader()
        configuration = config_reader.read_default_config()

        log.write_log(sessionID, "Configuration File Read Completed")

        """Initialize Email Sending Part"""

        email = SendMails(mailServer='smtp.gmail.com', mailPort=587, emailUser=configuration['SENDER_EMAIL'],emailPass=configuration['PASSWORD'])

        log.write_log(sessionID, "Initialization of Email Sending Completed")

        """Get the path of HTML template"""

        template= template_reader.TemplateReader()
        template_path: str = template.get_student_template(course_name=custInfoDict.get('course_name'))

        log.write_log(sessionID, "Fetching Path of HTML template part Completed")


        """Send An Email to Student with Template as an Attachment"""

        email.SendMail(senderAddress=configuration['SENDER_EMAIL'], toAddress=custInfoDict.get('cust_email'), subject=str(configuration['EMAIL_SUBJECT']), mailBody=configuration['EMAIL_BODY'],
                     attachmentPath=template_path, attachmentFileName=str(custInfoDict.get('course_name'))+".html")

        log.write_log(sessionID, "An email has sent to student")

        """Sending An Email To Support Team with Details Of Student"""

        email.SendMail(senderAddress=configuration['SENDER_EMAIL'], toAddress=configuration['SALES_TEAM_EMAIL'],
                       subject=configuration['SALES_TEAM_EMAIL_SUBJECT'], mailBody=configuration['SALES_MAIL_BODY'],
                       intendedPerson='SalesTeam', customerInfo=custInfoDict)

        log.write_log(sessionID, "An Email has been send to support team")

        fulfillmentText="We have sent the course syllabus and other relevant details to you via email. An email has been sent to the Support Team with your contact information, you'll be contacted soon. Do you have further queries?"

        log.write_log(sessionID, "Bot Says: "+fulfillmentText)

        return {"fulfillmentText": fulfillmentText}
        # return {"fulfillmentText": "Text response", "fulfillmentMessages": [{"text": {"text": [fulfillmentText]}}]}

    else:
        log.write_log(sessionID, "Bot Says: " + result.fulfillmentText)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
