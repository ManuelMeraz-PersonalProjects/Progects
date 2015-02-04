import praw, time
from pprint import pprint
# configuration file. store name and password here
CONFIG = 'config.txt'

# file containing all seen comments to date
COMMENT_ID_FILE = 'commentIDcache.txt'

# file containing the user ID's on the notification list
NOTIFY_FILE = 'notifications.txt'

# file containing event teams
REGISTRY = 'registry.txt'

class Bot():

    def __init__(self):
        '''
        Handle various setup functions, including logging into Reddit.
        '''
        # List of words bot looks for and their associated commands
        self.commands = {
                        '!register':self.register,
                         '!unregister':self.unregister,
                          '!team':self.team_check,
                          '!help':self.help,
                          '!notify':self.notify
                          }
                          
        self.languages = ('python', 'c++', 'java', 'javascript', 'ruby',
                            'c','perl', 'shell')
        self.experience = ('beginner', 'intermediate', 'advanced')

        # Subreddits to search for
        self.subreddit_list = ['progects', 'test']
        
        # set containing all comments seen so far
        self.comment_cache = self.cache_create(COMMENT_ID_FILE)

        # set containing current list of users signed up for notifications
        self.notify_cache = self.cache_create(NOTIFY_FILE)
        
        # dictionary containing all registered users and teams
        self.registry_cache = self.cache_create(REGISTRY)

        self.r = praw.Reddit(user_agent = "Test bot for /r/progects by /u/NEET_Here, /u/triple-take, and /u/prog_quest")

        # read in username and password from external config file
        with open(CONFIG, 'r') as txt:

            contents = [line.strip('\n') for line in txt.readlines()]

            self.bot_name = contents[0]
            self.password = contents[1]

        # create PRAW subreddit objects
        # did some testing, this only needs to be done once,
        # that's why its in __init__ now
        self.subreddits = self.get_subreddits()

        # login
        print("Logging in...")
        self.r.login(self.bot_name, self.password)

        print("Successfull login...")
    



    def cache_create(self, filename):
        '''
        Pulls information from file and creates cache
        '''
        
        # Checks if dictionary cache will be created
        if filename == REGISTRY:
            
            cache = {}
            
            with open(filename, 'r') as f:
                try:
                
                    # separates the lines in file
                    for item in f.read().splitlines():
                        
                        # Creates 2 variables with the key and value
                        (key, value) = item.rstrip().split(None, 1)
                        
                        # Splits the value string into a list
                        value = value.split(' ')
                        
                        cache[key] = value
                except ValueError:
                    print ('Registry empty')
         
         # else it creates normal cache set   
        else:
                
            cache = set()
            
            with open(filename, 'r') as f:

                # drop trailing newlines
                cache_read = [line.rstrip() for line in f.readlines()]

                # add them to set (this also handles duplicate entries if they occur)
                [cache.add(comment) for comment in cache_read]

        return cache




    def unregister(self, user, message_text, message):
        '''
        Try to remove a user ID from the notify list. If the ID isn't found,
        raise an exception, but don't do anything because it's not a big deal.
        '''
        notify_remove = False
        register_remove = False
        
        try:
            
            self.notify_cache.remove(user)
            self.write_file(NOTIFY_FILE, self.notify_cache)
            notify_remove =  True
            
        except KeyError:

            print("User not on notify list")

            
        try:
            del self.registry_cache[user]            
            self.write_file(REGISTRY, self.registry_cache)
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

            if comment.id not in self.comment_cache and \
                user.lower() != self.bot_name.lower():

                comment_text = comment.body.lower().split()
                
                comment_text = [x.strip('@#$%^&*.,') for x in comment_text]
                comment_text = [x.rstrip('!') for x in comment_text]

                # if comment contains a keyword, call the corresponding function
                for command in self.commands:

                    if command in comment_text:

                        # Executes command
                        self.commands[command](user, comment_text, comment)
                        

                        # Update cache files
                        self.comment_cache.add(comment.id)
                        
                        message = self.r.get_unread(limit=25)
                        for msg in message:
                            msg.mark_as_read()

                        # update comment cache file
                        self.write_file(COMMENT_ID_FILE, self.comment_cache)
            

    def write_file(self, filename, cache):
        ''' Function to write cache data to a file'''

        print('Writing data to {0}'.format(filename))

        with open(filename, 'w+') as f:
            if type(cache) == dict:
                for key in cache:
                    f.write(key + ' ',)
                    for value in cache[key]:
                        f.write(str(value) + ' ')
                    f.write('\n')
            else:
                for item in cache:                   
                    f.write(item + '\n')

        print('The file {0} has been updated'.format(filename))
    

    def check_registry(self, item, language=None, experience=None):
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
                    print ('Almost, not quite')
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
            team = self.registry_cache[user.lower()][2].replace('_', ' ').lower()
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
        self.r.send_message(user, 'Help with /u/PROGECTS_BOT1', '''
        PORGECTS_BOT1 registers users for /r/Progects events. 
        
        You can reply to this message with commands or make a post anywhere
        in the subreddit with a command. 
        
        The commands that are available are:
            !register:
                       Use this command to register yourself or a team
                       to the event. Include the language and experience
                       level (beginner, intermediate, or advanced) if you 
                       are registering yourself. If you are registering as 
                       a team, then simply include the usernames of your
                        teammates. You can also register in the same team 
                        as a friend if their team isn't full. The register
                       command will also add you to the notifications list
                       which means that even after the event, you will be
                       notified of upcoming events.
                       
                       If you would like to change something such as the
                       language, then use the !register command again and
                       it will override your past settings.
                       
                        If you would like to be
                       removed, simply use the command !unregister.
                       
                       .
                       Examples:
                                !register me as a python beginner
                                !register self python advanced
                                !register me using c++ as an intermediate user
                                !register me on the same team as /u/user
                                !register my team /u/user1 and /u/user2
                                !register my own team /u/user1, /u/user2, /u/user3
                                !register me with /u/user
            
            !unregister:
                        Use this command to unregister from the event
                        and be removed from the notifications list.
                        
                        Example:
                                !unregister
            
            !team:
                        Returns the users in your team. If you are in a custom
                        team it will return the usernames only. If you registered
                        by yourself, you can see who is currently on your team.
                    
                        Example:
                                !team
                                
            !notify:
                        If you would like to be kept updated, but can't participate
                        in the next event, then use this command. You will be
                        added to the notifications list. If you would like to
                        unsubcribe from the notifications, then use the 
                        !unregister command.
                        
                        Example:
                                !notify
                    ''')
                    
        print ('Messsage sent')

                        
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
        
        user = user.lower()
        
        
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
                        
        if ((('own' or 'my') and 'team')) or ('me' and 'with') in message_text:
            for people in message_text:
                if '/u/' in people:
                    people = people.lstrip('/u/').lower()
                    team_list.append(people)
                    team = True
                        
        # Registers person to the same team as a friend
        if (language and experience) != False and team == False and same_team == True:
            if type(check_registry(registry_cache[friend][2])) == str:
                
                print ('Replying to same team command...')
                message.reply('Thank you for registering. You will be on'
                                ' the same team as /u/{0}'.format(friend))
                print ('Adding user to registry...')        
                self.registry_cache[user] = [language,
                                            experience,
                                            self.registry_cache[friend][2]]
                print ('Added')
                
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
                        
                        self.registry_cache[team_mem] = ['custom', 'custom', user + "'s_Team"]
                        print("!notify command initialized. Adding {0} to notifications list.".format(team_mem))

                        self.notify_cache.add(team_mem)
                        self.write_file(NOTIFY_FILE, self.notify_cache)


                        print('{0} added to notifications list.'.format(user))

                    
                    print ('Replying to custom team command...')
                    message.reply('Thank you for registering your team. '
                                    ' A confirmation message will be sent to '
                                    'your team members.')
                    print ('Reply sent')
                    
                    # registers the user
                    self.registry_cache[user] = ['custom', 'custom', user + "'s_Team"]
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
            self.registry_cache[user] = [language, experience, self.team(language, experience)]
            print ('Found team, registering user')
            

        else:
            print ('Replying to bad command...')
            message.reply('Your command was not valid. Try the !help command.')
            print ('Reply sent')
                          
                          
        self.write_file(REGISTRY, self.registry_cache)
        print("!notify command initialized. Adding {0} to notifications list.".format(user))

        self.notify_cache.add(user)
        self.write_file(NOTIFY_FILE, self.notify_cache)


        print('{0} added to notifications list.'.format(user))
        pprint (self.registry_cache)
        
        


    def notify(self, user, message_text, message ):
        '''
        Adds user to notification list
        '''

        print("!notify command initialized. Adding {0} to notifications list.".format(user))

        self.notify_cache.add(user)
        self.write_file(NOTIFY_FILE, self.notify_cache)


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
        

    def runbot(self):
        '''
        Function to run bot.
        '''

        # Search each subreddit for comments
        for subreddit in self.subreddits:
            
            self.comment_search(subreddit)
        
        self.message_search()

        # Used to stop bot for certain amount of time to not
        # overload the server
        print ('Iteration complete')
        time.sleep(30)


def main():

    bot = Bot()

    i = 1
    while True:
        
        print ('Iteration: %d' % i)
        bot.runbot()

        
        i += 1


if __name__ == '__main__':
    main()
