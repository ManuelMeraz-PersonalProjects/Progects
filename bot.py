import praw
import time

# configuration file. store name and password here
CONFIG = 'config.txt'

# file containing all seen comments to date
COMMENT_ID_FILE = 'commentIDcache.txt'

# file containing the user ID's on the notification list
NOTIFY_FILE = 'notifications.txt'

class Bot():

    # List of words the bot will reply to
    comment_words = ['register', 'notify']
    registration_reply = 'Thank you for registering'

    # Subreddits to search for
    #subreddits = ['progects', 'test']
    subreddit_list = ['progects', 'test']

    # This is used in the runbot function to meet the criteria for
    # searching multiple subreddits, or a single subreddit
    #subredditstring = ''

    def __init__(self, config=CONFIG):
        '''
        Handle various setup functions, including logging into Reddit.
        '''
        
        # set containing all comments seen so far
        self.comment_cache = self.cache_create()

        print(self.comment_cache)

        # set containing current list of users signed up for notifications
        self.notify_cache = self.notify_create()

        print(self.notify_cache)

        self.r = praw.Reddit(user_agent = "Test bot for /r/progects by /u/NEET_Here and /u/triple-take")

        # read in username and password from external config file
        with open(config, 'r') as txt:

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

            # or, post a response


    def comment_search(self, word_list, reply_with):
        '''
        Searches for comments in the comment_words list and replies
        to them. Reply with is the response string.
        '''

        # this function needs a total rewrite to handle each keyword differently
        # like: if comment contains keyword, call the function for that keyword
        # register, notify, etc. each containing their own response

        # broke this up to handle each subreddit seperately
        for subreddit in self.subreddits:

            self.comments = subreddit.get_comments(limit=25)

            # Search through comments, if a match is found reply
            # unless the user has already replied or if the comment
            # is by the user.

            print("Reading comments...")
            for comment in self.comments:

                # Removes any extraneous characters
                comment_text = comment.body.lower().split(' ')
                comment_text = [x.strip('?!@#$%^&*"') for x in comment_text]

                #print(comment_text)

                for commentWord in comment_text:
                    
                    for word in word_list:

                        #
                        author = str(comment.author).lower()
                        self.bot_name =  self.bot_name.lower()

                        # here we should probably avoid passing in the variables
                        # word_list and reply_with, instead just checking
                        # against self.whatever, since we are not changing them
                        # or returning anything

                        # instead, just check for a match and decide what
                        # function to call to handle it
                        
                        if word == commentWord and comment.id not in \
                            self.comment_cache and author != self.bot_name:
                                
                            print("Comment found, ID: " + comment.id)
                            print ('Replying...')
                            #comment.reply(reply_with)
                            # I disabled for my testing, cuz i an exception thrown for spamming
                            print ('Writing Comment ID to Cache')

                            # add comment id to cache and cache file simultaneously
                            self.comment_cache.add(comment.id)

                            # Updates cache file with new comment ID
                            print ('Updating cache file...')
                            
                            with open(COMMENT_ID_FILE, 'w+') as f:
                                
                                for item in self.comment_cache:
                                    
                                    f.write(item + '\n')

                            print ('Cache Updated')


    def get_subreddits(self):
        '''
        For each specified subreddit, use get_subreddit to create a
        subreddit object for it and store them in a list.
        '''

        subreddits = []

        for sub in self.subreddit_list:

            subreddits.append(self.r.get_subreddit(sub))

        return subreddits
        

    def runbot(self):
        '''
        Function to run bot.
        '''
        """
        # Creates temp cache storage
        #self.cache_create() <- this is an __init__ thing, should only need
        # to run once at bot startup

        # Subreddits to be checked
        print("Grabbing subreddits...")

        for subreddit in self.subreddits:
            self.subredditstring += subreddit + '+'

        print(self.subreddits)

        #self.subredditstring.rstrip('+')

        self.subreddit = self.r.get_subreddit(self.subredditstring)

        print("subreddit string: %r" % self.subredditstring)
        print(self.subredditstring)

        print("\nsubreddit: %r" % self.subreddit)
        print(self.subreddit)
        """
        # Searches comments
        self.comment_search(self.comment_words, self.registration_reply)

        # Used to stop bot for certain amount of time to not
        # overload the server
        time.sleep(30)

def main():

    bot = Bot(CONFIG)

    i = 1
    while True:
        print ('Iteration: {0}'.format(i))
        bot.runbot()
        i += 1


if __name__ == '__main__':
    main()
