from flask import Flask, request, make_response
import os, json
from flask_cors import cross_origin
from Scripts import logger
from Scripts import template_reader
from Scripts.config_reader import ConfigReader
from Scripts.MailSending import SendMails
import pymongo

app = Flask(__name__)

"""geting and sending response to dialogflow"""

@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():

    req = request.get_json(silent=True, force=True)

    """Stored the incoming data in MongoDB"""

    conn = pymongo.MongoClient("mongodb+srv://ml:ml123@mlcluster-jnf6v.mongodb.net/test?retryWrites=true&w=majority")

    db = conn['chatbotdb']
    coll = db['ajayinfotechcoll']
    doc = coll.insert(req, check_keys=False)

    print("Documet insertion id "+str(doc))

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

    intent: str = result.get("intent").get('displayName')

    print("Intent name is "+intent)

    if (intent=='course_selection'):

        print("BOT will proceed for processing incoming request")

        parameters = result.get("parameters")

        print("Data recieved from customer is " + str(parameters))

        """Creating Dictionary Of Customer Data"""

        custInfoDict = {}
        custInfoDict['cust_name'] = parameters.get("name")
        custInfoDict['cust_email'] = parameters.get("email")
        custInfoDict['course_name'] = parameters.get("courses")[0]
        custInfoDict['cust_contact'] = parameters.get("phone")

        print("customer data dict created ")

        """Reading Default Configuration File"""

        config_reader = ConfigReader()
        configuration = config_reader.read_default_config()

        print("config file read")

        """Initialize Email Sending Part"""

        email = SendMails(mailServer='smtp.gmail.com', mailPort=587, emailUser=configuration['SENDER_EMAIL'],emailPass=configuration['PASSWORD'])


        print("Initialization of Email Sending Completed")

        """Get the path of HTML template"""

        template= template_reader.TemplateReader()
        template_path: str = template.get_student_template(course_name=custInfoDict.get('course_name'))

        print("Fetching Path of HTML template part Completed")


        """Send An Email to Student with Template as an Attachment"""

        email.SendMail(senderAddress=configuration['SENDER_EMAIL'], toAddress=custInfoDict.get('cust_email'), subject=str(configuration['EMAIL_SUBJECT']), mailBody="Hello, \n \n Please find attached course details. \n \n Regards,\n Ajay Bile",
                     attachmentPath=template_path, attachmentFileName=str(custInfoDict.get('course_name')+".html"))


        print("An email has sent to student")

        """Sending An Email To Support Team with Details Of Student"""

        email.SendMail(senderAddress=configuration['SENDER_EMAIL'], toAddress=configuration['SALES_TEAM_EMAIL'],
                       subject=configuration['SALES_TEAM_EMAIL_SUBJECT'], mailBody=configuration['SALES_MAIL_BODY'],
                       intendedPerson='SalesTeam', customerInfo=custInfoDict)


        print("An Email has been send to support team")

        fulfillmentText="We have sent the course syllabus and other relevant details to you via email. An email has been sent to the Support Team with your contact information, you'll be contacted soon. Do you have further queries?"


        return {"fulfillmentText": fulfillmentText}
        # return {"fulfillmentText": "Text response", "fulfillmentMessages": [{"text": {"text": [fulfillmentText]}}]}

    else:
        print("Data stored in mongodb for intent "+str(intent))
        return {"fulfillmentText": result['fulfillmentText']}


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
