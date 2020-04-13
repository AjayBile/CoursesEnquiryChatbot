class TemplateReader:

    def __init__(self):
        pass

    def get_student_template(self,course_name):

        template_path = None

        try:
            if(course_name=='DataScienceMasters'):
                template_path = "email_templates\\DSM_Template.html"

            elif(course_name=='MachineLearningMasters'):
                template_path = "email_templates\\MLM_Template.html"

            elif(course_name == 'DeepLearningMasters'):
                template_path = "email_templates\\DLM_Template.html"

            elif(course_name == 'NLPMasters'):
                template_path = "email_templates\\NLPM_Template.html"

            elif(course_name == 'DataScienceForManagers'):
                template_path = "email_templates\\DSFM_Template.html"

            elif(course_name == 'Vision'):
                template_path = "email_templates\\Vision_Template.html"

        except Exception as e:
            print('An Exception Occured in template reader file : '+str(e))

        return template_path