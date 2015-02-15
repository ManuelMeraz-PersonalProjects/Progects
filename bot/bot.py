import praw, time, cache, configparser, schedule, datetime, traceback, mailme
from pprint import pprint

# configuration file. store name and password here
CONFIG = 'config.txt'

# file containing all seen comments to date
ID_FILE = 'IDcache.txt'

# file containing the user ID's on the notification list
NOTIFY_FILE = 'notifications.txt'

# file containing event teams
REGISTRY = 'registry.txt'

class Bot():

    def __init__(self):
        '''
        Handle various setup functions, including logging into Reddit.
        '''
        
        # Open config file for reading
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG)
        
        # List of words bot looks for and their associated commands
        self.commands = {
                        '!register':self.register,
                         '!unregister':self.unregister,
                          '!team':self.team_check,
                          '!help':self.help,
                          '!notify':self.notify
                          }

        self.languages = [lang for lang in self.config['Languages']]
        self.experience = [exp for exp in self.config['Experience']]

        # Subreddits to search for
        self.subreddit_list = [sub for sub in self.config['Subreddits']]

        # set containing all comments seen so far
        self.ID_cache = cache.cachelist(ID_FILE)

        # set containing current list of users signed up for notifications
        self.notify_cache = cache.cachelist(NOTIFY_FILE)

        # dictionary containing all registered users and teams
        self.registry_cache = cache.cachedict(REGISTRY)
        
        # time until next event in seconds
        self.datetime = None
        
        # Thread ID for event thread
        threadID = None

        self.r = praw.Reddit(user_agent = "Test bot for /r/progects by /u/NEET_Here, /u/triple-take, and /u/prog_quest")

        # read in username and password from external config file
        self.botname = self.config['BotLogin']['username']
        self.password = self.config['BotLogin']['password']

        # create PRAW subreddit objects
        self.subreddits = self.get_subreddits()

        # login
        print("Logging in...")
        self.r.login(self.botname, self.password)

        print("Successfull login...")

    def unregister(self, user, message_text, message):
        '''
        Try to remove a user ID from the notify list. If the ID isn't found,
        raise an exception, but don't do anything because it's not a big deal.
        '''
        notify_remove = False
        register_remove = False

        try:

            self.notify_cache.remove(user)
            cache.writefile(NOTIFY_FILE, self.notify_cache)
            notify_remove =  True

        except KeyError:

            print("User not on notify list")


        try:
            del self.registry_cache[user]
            cache.writefile(REGISTRY, self.registry_cache)
            register_remove = True

        except KeyError:

            print("User not on registry.")

        if notify_remove == True and register_remove == True:
            print ('Removing user from registry and notifications...')
            message.reply('You have been removed from the event and '
                            'notifications list.')
        elif notify_remove == True and register_remove == False:
            print ('Removing user from notifications...')
            message.reply('You have been removed from the notifications list.')
        else:
            print ('Replying to unregistered user...')
            message.reply('It looks like you aren\'t registered.')

        pprint (self.registry_cache)

    def message_search(self):
        '''
        Searches for keywords in private messages and respods with
        appropriate function if a match is found.
        '''
        print ('Reading unread messages...')
        message = self.r.get_unread(limit=25)

        for msg in message:

            msg_text = (str(msg.body).replace('\n', ' ').lower().split(' '))
            user = str(msg.author)

            msg_text = [x.strip('@#$%^&*.,') for x in msg_text]
            msg_text = [x.rstrip('!') for x in msg_text]

            # If bot gets a reply to a comment. It will also get an
            # unread message, this clears the unread message if it pops
            # up in the inbox.
            for command in self.commands:
                if command in msg_text:
                    user = user.lower()
                    self.commands[command](user, msg_text, msg)
                    msg.mark_as_read()

    def comment_search(self, subreddit):
        '''
        Searches for keywords in comments and responds with the appropriate
        function if a match is found.
        '''

        comment_list = subreddit.get_comments(limit=25)

        print("Reading comments in subreddit {0}...".format(subreddit))
        for comment in comment_list:


            # should keep capitalization
            user = str(comment.author)

            if comment.id not in self.ID_cache and \
                user.lower() != self.botname.lower():

                comment_text = comment.body.lower().split()

                comment_text = [x.strip('@#$%^&*.,') for x in comment_text]
                comment_text = [x.rstrip('!') for x in comment_text]

                # if comment contains a keyword, call the corresponding function
                for command in self.commands:

                    if command in comment_text:

                        # Executes command
                        user = user.lower()
                        self.commands[command](user, comment_text, comment)


                        message = self.r.get_unread(limit=25)
                        for msg in message:
                            msg.mark_as_read()
                            
                        # Update cache files
                        self.ID_cache.add(comment.id)
                        
                        # update comment cache file
                        cache.writefile(ID_FILE, self.ID_cache)

    def check_registry(self, item):
        '''
        Item can be either a team or a user. This function checks
        to see if there are similar teams for a user, if teams are full,
        and if a user is in the registry
        '''

        amount = 0

        # Checks if teams are full and available for the language/experience
        if 'Team' in item:

            for key in self.registry_cache:

                if self.registry_cache[key][2] == item:
                    amount += 1
            if amount == 0:
                return 0
            elif 1 <= amount < 5:
                return key
            else:
                return False

        # Checks for users
        elif item in self.registry_cache:
            return True

        else:
            return False

    def team(self, language, experience):

        '''
        Creates teams by checking to see if teams are full for the
        given language and experience.
        '''


        team_number = 1
        while True:
            team_name = 'Team_{0}'.format(team_number)
            print (team_name)
            check_reg = self.check_registry(team_name)
            # Checking if teams are full
            if type(check_reg) == str:

                # If not full, then check to see if that team matches
                # the language and experience
                if language == self.registry_cache[check_reg][0] and self.registry_cache[check_reg][1] == experience:

                    # If they match, return the person will join their team
                    return team_name
                else:
                    team_number += 1
            elif check_reg == 0:
                return team_name
            else:
                team_number += 1

    def team_check(self, user, message_text, message):
        '''
        Command allows user to check their team members by using !team
        '''
        print ('!team command initialized')
        try:
            team = self.registry_cache[user][2].replace('_', ' ').lower()
            string = "You're in {0} with: \n\n\t\t".format(team)

            for key in self.registry_cache:
                if self.registry_cache[key][2].replace('_', ' ').lower() == team:

                    # If user has custom team the bot will reply with just the names
                    if 'custom' in self.registry_cache[key]:
                        string += '/u/{0} \n\n\t\t'.format(key)

                    # Replies with all information for bot made teams
                    else:
                        string += '/u/{0} using the language {1} with {2} experience\n\n\t\t'.format(key,\
                            self.registry_cache[key][0], self.registry_cache[key][1])

            print ('Replying to message...')
            message.reply(string)
            print ('Reply sent')

        except ValueError:

            message.reply('Sorry, but you currently aren\'t registered.')

        except KeyError:

            message.reply('Sorry, but you currently aren\'t registered.')

    def help(self, user, message_text, message):
        '''
        This command (!commands) send a message to the user explaining
        the commands that the bot has available and what they do
        '''
        print ('!help command initialized')

        help_text = ''
        with open('help.txt', 'r') as f:
            help_text = f.read()

        self.r.send_message(user, 'Help with /u/PROGECTS_BOT1', help_text)

        print ('Messsage sent')

    def unreg(self, user):
        '''
        Unregister user without replying
        '''
        try:
            del self.registry_cache[user]

        except KeyError:

            pass

    def register(self, user, message_text, message):
        '''
        The registration command (!register) will register a user for events.
        message_text is the text for the message that the user is registering
        with.
        '''
        print ('Register command initialized')

        language = False
        experience =  False
        same_team =  None
        team = False
        team_list = []
        friend = None
        user_team = None



        # Searches for languages in command
        for lang in self.languages:
            if lang in message_text:
                language = lang
        # Searches for experience level in command
        for exp in self.experience:
            if exp in message_text:
                experience = exp

        # Searches to see if someone would like to be in the same team
        # as someone else

        if 'same' in message_text and 'team' in message_text:
            for people in message_text:
                if '/u/' in people:
                    people = people.lstrip('/u/').rstrip('.,').lower()

                    if self.check_registry(people) == True:
                        same_team = True
                        friend = people
                    else:
                        same_team = False

        if ((('own' or 'my') and 'team')) and ('me' and 'with') in message_text:
            for people in message_text:
                if '/u/' in people:
                    people = people.lstrip('/u/').lower()
                    team_list.append(people)
                    team = True

        # Registers person to the same team as a friend
        if (language and experience) != False and team == False and same_team == True:
            if type(self.check_registry(self.registry_cache[friend][2])) == str:

                print ('Replying to same team command...')
                message.reply('Thank you for registering. You will be on'
                                ' the same team as /u/{0}'.format(friend))
                print ('Adding user to registry...')
                self.unreg(user)
                self.registry_cache[user] = [language,
                                            experience,
                                            self.registry_cache[friend][2]]


                print ('Added')
                self.notify_add(user)

            else:
                print ('Replying to bad (full) same team command...')
                message.reply('Sorry, /u/' + friend + "'s team is full.")
                print ('Reply sent')


        # Tells user to try registering again if the person they want to be on the
        # same team as isn't registered
        elif (language and experience) != False and team == False and same_team == False:
            print ('Replying to bad command...')
            message.reply('The person you are trying to be on the same team'
                            ' with isn\'t registered. Please try registering'
                            ' again')
            print ('Reply sent')

        # Registers custom teams
        elif team == True:
            if user in team_list: team_list.remove(user)

            # Checks to see if there are enough or too many members in team
            try:
                print ('Trying')
                if 1 <= len(team_list) < 5:

                    for team_mem in team_list:


                        print ('Messaging team member...')
                        self.r.send_message(team_mem, 'Registered for /r/Progects hackathon', \
                                        'You were registered by /u/' + user + ' if you would like to '
                                        'unregister reply with !unregister.')
                        print ('Message sent')
                        self.unreg(team_mem)
                        self.registry_cache[team_mem] = ['custom', 'custom', user + "'s_Team"]
                        self.notify_add(team_mem)


                    print ('Replying to custom team command...')
                    message.reply('Thank you for registering your team. '
                                    ' A confirmation message will be sent to '
                                    'your team members.')
                    print ('Reply sent')


                    # registers the user
                    self.unreg(user)
                    self.registry_cache[user] = ['custom', 'custom', user + "'s_Team"]
                    self.notify_add(user)
                else:
                    print ('Replying to bad command...')
                    message.reply('Sorry, you have either registered too many'
                                    ' or too few members. The minimum for a team'
                                    ' is 2 members and the max is 5')
                    print ('Reply sent')




            # Need to fix this exception eventually.

            except:
                print ('User put a fake username. Replying to message...')
                message.reply('Please use valid usernames for your team mates.')
                print ('Reply sent')



        # Registers new user. Checks to see if there are any teams with
        # people of similar experience and language.
        elif (language and experience) != False and team == False:
            print ('Replying to new user command...')
            message.reply('Thank you for registering.')

            print ('Looking for team...')
            self.unreg(user)
            self.registry_cache[user] = [language, experience, self.team(language, experience)]
            print ('Found team, registering user')

            self.notify_add(user)


        else:
            print ('Replying to bad command...')
            message.reply('Your command was not valid. If you were registering'
                            ' yourself, don\'t forget to add your preferred'
                            ' programming language and your experience level(beginner, intermediate, advanced).'
                            ' If there are any other issues, please try the !help command.')
            print ('Reply sent')

        # Updates registry file
        cache.writefile(REGISTRY, self.registry_cache)

    def notify_add(self, user):
        '''
        Updates notification cache
        '''

        print("Adding {0} to notifications list.".format(user))

        self.notify_cache.add(user)
        cache.writefile(NOTIFY_FILE, self.notify_cache)


        print('{0} added to notifications list.'.format(user))
        pprint (self.registry_cache)

    def notify(self, user, message_text, message ):
        '''
        Adds user to notification list with the !notify command
        '''

        print("!notify command initialized. Adding {0} to notifications list.".format(user))

        self.notify_cache.add(user)
        cache.writefile(NOTIFY_FILE, self.notify_cache)


        print('{0} added to notifications list.'.format(user))

        print("Replying to {0} .".format(user))

        message.reply('You have been added to the notification list')

        print ('Reply sent')
    
    def get_subreddits(self):
        '''
        For each specified subreddit, use get_subreddit to create a
        subreddit object for it and store them in a list.
        '''

        print("Grabbing subreddits...")

        subreddits = []

        for sub in self.subreddit_list:

            subreddits.append(self.r.get_subreddit(sub))

        return subreddits

    def event(self, subreddit):
        '''
        Searches for dates in events and notifies people of upcoming events
        '''
        message = None
        msg_title = None
        new_thread = subreddit.get_new(limit = 5)
        
        if self.datetime == None:
            print ('Datetime not set. Searching for datetime in subreddit {0}'.format(subreddit))
            for thread in new_thread:
                title = thread.title
                dateseconds = schedule.date(title)
                if dateseconds != False and thread.id not in self.ID_cache:
                    self.threadID = thread.id
                    self.datetime = dateseconds
                    print ('Datetime is set')   
                                    
                    print ('Notifying users of upcoming event')
                    for name in self.notify_cache:
                        if name != '':
                            self.r.send_message(name, 'A Progect has been posted for /r/Progects!'\
                                                    , 'new event!')  
                    print ('Users have been notified')
                    
        elif self.datetime != None:
            print ('Checking time until event...')       
            message, msg_title = schedule.confirm(self.datetime)
            print ('Checked')
            if type(message) == str:
                ('Event will be soon, notifying users')
                for name in self.notify_cache:
                    if name != '':
                        self.r.send_message(name, msg_title, message)
                ('All users have been notified')
                
            elif message == True:
                print ('The event date has passed. Adding Thread ID to cache...')
                self.datetime = None
                print ('Adding thread ID {0} to cache file'.format(self.threadID))
                self.ID_cache.add(self.threadID)
                print ('Thread ID added')
                cache.writefile(ID_FILE, self.ID_cache)
                
        if self.datetime == None:
            print ('Datetime not found')
                
                
            
            
    def runbot(self):
        '''
        Function to run bot.
        '''

        # Search each subreddit for comments
        for subreddit in self.subreddits:

            self.comment_search(subreddit)
            self.event(subreddit)

        self.message_search()
        


        # Used to stop bot for certain amount of time to not
        # overload the server
        print ('Iteration complete')
        time.sleep(30)


def main():
    bot = Bot()
    email = {}
    for key in bot.config['Email']:
        email[key] = bot.config['Email'][key]

    
    i = 1
    exception = 0
    while True:

        print ('Iteration: %d' % i)
        try:
            bot.runbot()
            exception = 0
            i += 1
        except KeyboardInterrupt:
            raise
        
        except:
            timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
            error_message = traceback.format_exc()

            with open('errorlog.txt', 'a+') as f:
                f.write(timestamp + ' - Error:\n' + error_message + '\n\n\n')
                
            print ('Sending email with error attached...')
            
            # Access email settings through email dictionary
            mail = mailme.MailMe(email['e_username'], email['e_password'])
            mail.input_address(email['to_addr'], email['from_addr'])
            mail.email_content('Bot Error', 'Log attached', ['errorlog.txt'])
            mail.server(email['smtp'], email['port'])
            mail.sendmail()
            print('Email sent')

            time.sleep(60)
            print('Sleeping....zzzzzz')
            exception += 1
        
        if exception >= 3:
            break


if __name__ == '__main__':
    main()
