import praw, time

# configuration file. store name and password here
CONFIG = 'config.txt'

# file containing all seen comments to date
COMMENT_ID_FILE = 'commentIDcache.txt'

# file containing the user ID's on the notification list
NOTIFY_FILE = 'notifications.txt'

class Bot():

    def __init__(self):
        '''
        Handle various setup functions, including logging into Reddit.
        '''
        # List of words bot looks for and their associated commands
        self.comment_words = {'!register':self.register, '!notify':self.notify}
        
        #self.registration_reply = 'Thank you for registering'

        # Subreddits to search for
        #subreddits = ['progects', 'test']
        self.subreddit_list = ['progects', 'test']

        # This is used in the runbot function to meet the criteria for
        # searching multiple subreddits, or a single subreddit
        #subredditstring = ''
        
        # set containing all comments seen so far
        self.comment_cache = self.cache_create()

        print(self.comment_cache)

        # set containing current list of users signed up for notifications
        self.notify_cache = self.notify_create()

        print(self.notify_cache)

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


    def cache_create(self):
        '''
        Pulls information from file and creates cache
        '''
        comment_cache = set()
        
        with open(COMMENT_ID_FILE, 'r') as f:

            # drop trailing newlines
            cache_read = [line.rstrip() for line in f.readlines()]

            # add them to set (this also handles duplicate entries if they occur)
            [comment_cache.add(comment) for comment in cache_read]

        return comment_cache


    def notify_create(self):
        '''
        Pulls list of user IDs who are signed up for notifications and creates
        a cache of them.
        '''
        notify_cache = set()

        with open(NOTIFY_FILE, 'r') as f:

            # drop trailing newlines
            notify_read = [line.rstrip() for line in f.readlines()]

            # add them to set (this also handles duplicate entries if they occur)
            [notify_cache.add(user) for user in notify_read]

        return notify_cache


    def notify_add(self, user):
        '''
        Add a user ID to the notify list cache.
        '''

        # because sets do not allow duplicates, we don't need to check if user
        # is already on the notify list or not, just add them
        self.notify_cache.add(user)


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


    def comment_search(self, subreddit):
        '''
        Searches for keywords in comments and responds with the appropriate
        function if a match is found.
        '''

        # this doesn't need to be 'self.comments' as it isn't used outside of
        # this method
        comment_list = subreddit.get_comments(limit=25)

        print("Reading comments...")
        for comment in comment_list:

            # should keep capitalization
            author = str(comment.author)

            if comment.id not in self.comment_cache and \
                author.lower() != self.bot_name.lower():

                comment_text = comment.body.lower().split()

                # if comment contains a keyword, call the corresponding function
                for keyword in self.comment_words:

                    if keyword in comment_text:

                        # the comment might need to be passed as an arg too, 
                        # idk how reply works yet
                        self.comment_words[keyword](author)

                        # add comment to seen list
                        self.comment_cache.add(comment.id)

                        # update comment cache file
                        self.cache_write()
            

    def cache_write(self):

        print ('Writing Comment ID to Cache')

        with open(COMMENT_ID_FILE, 'w+') as f:
                                
            for item in self.comment_cache:
                                    
                f.write(item + '\n')

        print ('Cache Updated')

                        
    def register(self, user):
        '''
        Placeholder function to register a user.
        '''

        print("I just registered %s! (obviously just a test)" % user)


    def notify(self, user):
        '''
        Placeholder function to add someone to the notification list or
        whatever. Maybe merge it with notify_add()/notify_remove()? That is,
        if we pass it some kind of 'add' or 'remove' argument.
        '''

        print("Added %s to the notification list! (obviously just a test)" % \
            user)

        self.notify_add(user)

        print(self.notify_cache)

        print("Let %s know they've been added to the list!" % user)

        # add code here to call reply_to with some kind of response

    def reply_to(self, user, message):
        '''
        Placeholder function to reply to a user's post. The functions
        register(), notify(), etc. should call this upon completion.
        '''

        pass

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

        # Used to stop bot for certain amount of time to not
        # overload the server
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
