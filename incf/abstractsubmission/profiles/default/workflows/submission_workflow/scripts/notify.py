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
    
    subject = "Your submission to neuroinformatics 2011 has been accepted"
    
    name = user.getProperty('fullname')
    message = "Hello " + name
    message += '\n'
    message += "Your contribution " 
    message += object.Title()
    message += " has been accepted for presentation at the INCF Neuroinformatics Congress 2011. "
    message += '\n'
    message += object.absolute_url()
    message += '\n'
    message += """
    
    Kind regards, 
    """
    message += from_name
    
    mailhost.secureSend(message, user_email, from_email, subject = subject)

else:
    print "No user found"
    return printed
