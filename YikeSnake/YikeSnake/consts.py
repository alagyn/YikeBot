# Constants

# RegEx
YIKE_CMD = r"_(yike)"
UNYIKE_CMD = r"_(unyike)"
HELP_CMD = r"_(help)"
LIST_CMD = r"_(list)"
LOGOUT_CMD = r"_(logout)"
QUOTE_CMD = r"_(quote)"

ID_FORMAT = r"<@!?\d+>"

# Data

YIKE_USAGE = "_yike @user [optional amnt]\n" + \
             "\tAdds one or more Yikes to a user\n"
UNYIKE_USAGE = "_unyike @user [optional amnt]\n" + \
               "\tRemoves one or more Yikes from a user\n"
LIST_USAGE = "_list [optional @user]\n" + \
             "\tLists the total Yikes for every user on a server or an individual\n"
QUOTE_USAGE = "_quote @user - quote\n" + \
              "\tRecords a quote spoken by the subject"
HELP_INFO = YIKE_USAGE + "\n" + UNYIKE_USAGE + "\n" + LIST_USAGE + "\n" + \
            "_help\n\tWhat do you think?"

LOG = 'log.dat'
QUOTES = 'quotes.dat'
YIKE_ID = "614235819498143744"
ADMIN_ID = "324725726475714560"
