## Script (Python) "notify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_change
##title=
##
object = state_change.object
mailhost = object.MailHost

user = context.portal_membership.getMemberById(object.Creator())  # is Creator the right thing to use here?

if user:
    user_email = user.getProperty('email')
    from_email = object.portal_url.getPortalObject().getProperty('email_from_address')
    from_name = object.portal_url.getPortalObject().getProperty('email_from_name')

    id = object.getIdentifier()
    subject = "Your submission to neuroinformatics 2011 has been accepted (%s)" % id

    cc = from_email

    session = ' and '.join(object.getSessionType())
    if session == 'Poster Session 1':
        session = '1 (September 4)'

    if session == 'Poster Session 2':
        session = '2 (September 5)'

    data = {'name': user.getProperty('fullname'),
            'title': object.Title(),
            'id': id,
            'session': session,
            'sender': from_name,
            }

    body = object.getAcceptanceLetterText()   

    message = body%data 
    
    mailhost.secureSend(message, user_email, from_email, subject = subject, mcc = cc)

    object.setNotificationDate()

else:
    print "No user found"
    return printed
