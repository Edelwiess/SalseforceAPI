import re,sys
from simple_salesforce import Salesforce


class Readconf(object):
    def __init__(self, path):
        self._path = path
        def readparas():
            with open(path) as conf:
                paras = conf.read()
                paras_l = re.split('username=|password=|token=|\n', paras)
                return (paras_l)
        self.paras = readparas()
        self.username = self.paras[1]
        self.password = self.paras[3]
        self.token = self.paras[5]

    def login(self):
        try:
            session = Salesforce(username=self.username, password=self.password, security_token=self.token)
            return (session)
        except Exception as error_info:
            print('Connection failed, error info:\n%s' % error_info)
            input('Press any key to quit')
            sys.exit()

class Caseinfo(object):
    def __init__(self, session, casenumber):
        lc = len(casenumber)
        sfnumber = casenumber
        while lc < 8:
            sfnumber = '0' + sfnumber
            lc = lc + 1
        self.casenumber = sfnumber
        self.__caseobject =session

        def getcaserecord():
            # get case info
            query_text = """SELECT Id, Subject, ContactId, Type FROM Case WHERE CaseNumber = '%s'""" % self.casenumber
            case_result = self.__caseobject.query(query_text)
            records_L = case_result['records']
            if len(records_L) > 0:
                records_D = records_L[0]
                return (records_D)
            else:
                print('Case does not exist.')
                input('Press any key to quit')
                sys.exit()
        self.caserecords= getcaserecord()

        self.id = self.caserecords['Id']
        self.subject = self.caserecords['Subject']


    def type(self):
        return (self.caserecords['Type'])

    def contactid(self):
        return (self.caserecords['ContactId'])

    def ref(self):
        return ('[ ref:_00D407DsZ._%s:ref ]' % self.id)

    def mailsubject(self):
        return ('Case mail subject:\n%s - NetBrain Case#%s' % (self.subject, self.casenumber))

    def link(self):
        return ('https://nbtech.my.salesforce.com/%s' % self.id)

class Contactinfo(object):
    def __init__(self, session, contactid):
        self.records = session.Contact.get(contactid)

    def email(self):
        return (self.records['Email'])

    def firstname(self):
        return (self.records['FirstName'])

class EmailText(object):
        GREETING = ('Hi %s,\n Thanks for contacting the support team.\n')

        FEATURE = ("""This feature cannot be implemented in our software at present.
I will file a feature request on your behalf to our Product Management team, they will evaluate the request and decide how to proceed. 
I will keep you posted on the progress. Thanks for your understanding.\n""")

        QUESTION = ('I would like to answer your question.\n')

        COMPLEXISSUE=('Could you please follow below instructions to collect necessary data and send them to us for further analysis?\n'
                       'looking forward to your reply.\n')

        def greeting(self, firstname, content=GREETING ):
            print(content % firstname)

        def feature(self, content=FEATURE):
            print(content)

        def question(self, content=QUESTION):
            print(content)

        def complexissue(self, content=COMPLEXISSUE):
            print(content)




if __name__ == '__main__':
    case_number = input('Case Number: ')
    conf = Readconf('sf.ini')
    session = conf.login()
    case = Caseinfo(session, case_number)
    print('Standard Case number: %s' % case.casenumber)
    case_type = case.type()
    print('Case Type: %s\n' % case_type)
    print(case.mailsubject())
    contact_id = case.contactid()
    emailtext = EmailText()
    if contact_id:
        contact = Contactinfo(session, contact_id)
        firstname = contact.firstname()
        len1=len(firstname)
        print('To: %s' %contact.email())
        print('+' * 50)
        emailtext.greeting(firstname)
        if case_type:
            if case_type == 'Feature Request':
                emailtext.feature()
            if case_type == 'Bug' or case_type == 'Complex Issues':
                emailtext.complexissue()

            if case_type == 'Question':
                emailtext.question()
        print('Best Regards,')
    else:
        print('+'*50+'\nNo contact Info')
    print('+'*50)
    print(case.ref()+'\n')
    print('For more Case info, please visit: %s' % case.link())

    #input('Press any key to quit')
