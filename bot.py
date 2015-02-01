import praw
import time

# configuration file. store name and password here
CONFIG = 'config.txt'

class Bot():

    # Cache storage
    cache = []
    cache_file = 'commentIDcache.txt'

    # List of words the bot will reply to
    comment_words = ['register']
    registration_reply = 'Thank you for registering'

    # Subreddits to search for
    subreddits = ['progects', 'test']

     # This is used in the runbot function to meet the criteria for
     # searching multiple subreddits, or a single subreddit
    subredditstring = ''

    def __init__(self, config=CONFIG):
        '''
        Logs the bot into Reddit.
        '''

        self.r = praw.Reddit(user_agent = "Test bot for /r/progects by /u/NEET_Here and /u/triple-take")

        # read in username and password from external config file
        with open(config, 'r') as txt:

            contents = [line.strip('\n') for line in txt.readlines()]

            self.bot_name = contents[0]
            self.password = contents[1]

        print("Logging in...")
        self.r.login(self.bot_name, self.password)

        print("Successfull login...")


    def cache_create(self):
        '''
        Pulls information from file and creates cache
        '''
        with open(self.cache_file, 'r') as f:
            self.cache = f.read().split('\n')
            self.cache = [x for x in self.cache if x != '']


    def comment_search(self, word_list, reply_with):
        '''
        Searches for comments in the comment_words list and replies
        to them. Reply with is the response string.
        '''

        self.comments = self.subreddit.get_comments(limit=25)

        # Search through comments, if a match is found reply
        # unless the user has already replied or if the comment
        # is by the user.

        print("Reading comments...")
        for comment in self.comments:

            # Removes any extraneous characters
            comment_text = comment.body.lower().split(' ')
            comment_text = [x.strip('?!@#$%^&*"') for x in comment_text]

            for commentWord in comment_text:
                for word in word_list:

                    #
                    author = str(comment.author).lower()
                    self.bot_name =  self.bot_name.lower()
                    if word == commentWord and comment.id not in self.cache\
                     and author != self.bot_name:
                        print("Comment found, ID: " + comment.id)
                        print ('Replying...')
                        comment.reply(reply_with)
                        print ('Writing Comment ID to Cache')

                        # add comment id to cache and cache file simultaneously
                        self.cache.append(comment.id)

                        # Updates cache file with new comment ID
                        print ('Updating cache file...')
                        with open(self.cache_file, 'w+') as f:
                            for item in self.cache:
                                f.write(item + '\n')

                        print ('Cache Updated')


    def runbot(self):
        '''
        Function to run bot.
        '''


        # Creates temp cache storage
        self.cache_create()

        # Subreddits to be checked
        print("Grabbing subreddits...")

        for subreddit in self.subreddits:
            self.subredditstring += subreddit + '+'

        self.subredditstring.rstrip('+')

        self.subreddit = self.r.get_subreddit(self.subredditstring)

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
