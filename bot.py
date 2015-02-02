import praw, time

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
        self.commands = {'!register':self.register, '!notify':self.notify}
        self.languages = ('python', 'c++', 'java', 'javascript', 'ruby')
        self.experience = ('beginner', 'intermediate', 'advanced')
        # Subreddits to search for
        self.subreddit_list = ['progects', 'test']
        
        # set containing all comments seen so far
        self.comment_cache = self.cache_create(COMMENT_ID_FILE)

        # set containing current list of users signed up for notifications
        self.notify_cache = self.cache_create(NOTIFY_FILE)
        
        # dictionary containing all registered users and teams
        self.registry_cache = self.cache_create(REGISTRY)

        self.r = praw.Reddit(user_agent = "Test bot for /r/progects by /u/NEET_Here and /u/triple-take")

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




    def notify_remove(self, user):
        '''
        Try to remove a user ID from the notify list. If the ID isn't found,
        raise an exception, but don't do anything because it's not a big deal.
        '''

        try:
            
            self.notify_cache.remove(user)

            # here is where we would have code to respond with a confirmation

        except KeyError:

            print("User not on notify list. Nothing happened")

            # or, post a response or something
            
    def message_search(self):
        '''
        Searches for keywords in private messages and respods with
        appropriate function if a match is found.
        '''
        print ('Reading unread messages...')
        message = self.r.get_unread(limit=25)
        for msg in message:
            msg_text = (str(msg).replace('\n', ' ').lower().split(' '))
            user = str(msg.author)
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

                # if comment contains a keyword, call the corresponding function
                for command in self.commands:

                    if command in comment_text:

                        # Executes command
                        self.commands[command](user, comment_text, comment)
                        

                        # Update cache files
                        self.comment_cache.add(comment.id)

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
                        f.write(value + ' ')
                    f.write('\n')
            else:
                for item in cache:                   
                    f.write(item + '\n')

        print('The file {0} has been updated'.format(filename))

                        
    def register(self, user, message_text, message):
        '''
        The registration command will register a user for events. 
        Message is the text for the message that the user is registering
        with.
        '''
        language = False
        experience =  False
        
        
        for lang in self.languages:
            if lang in message_text:
                language = lang
                
        for exp in self.experience:
            if exp in message_text:
                experience = exp
                
        if (language and experience) != False:
            print ('Replying to good command...')
            #message.reply('Thank you for registering')
            print ('Adding user to registry...')
            self.registry_cache[user] = [language, experience]
            self.write_file(REGISTRY, self.registry_cache)
            self.notify(user)

        else:
            print ('Replying to bad command...')
            #message.reply('Sorry try adding your language and'
            #               ' experience to your command please')
        
        


    def notify(self, user):
        '''
        Placeholder function to add someone to the notification list or
        whatever. Maybe merge it with notify_add()/notify_remove()? That is,
        if we pass it some kind of 'add' or 'remove' argument.
        '''

        print("Added %s to the notification list!" % \
            user)

        self.notify_cache.add(user)
        self.write_file(NOTIFY_FILE, self.notify_cache)

        print(self.notify_cache)

        print("Let %s know they've been added to the list!" % user)
        
        



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
        time.sleep(5)


def main():

    bot = Bot()

    i = 1
    while True:
        
        print ('Iteration: %d' % i)
        bot.runbot()
        
        i += 1


if __name__ == '__main__':
    main()
