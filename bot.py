import praw
import time


class Bot():
    
    # Cache storage
    cache = []
    cache_file = 'commentIDcache.txt'
    notif_list = []
    notif_file = 'registered_for_notifications.txt'
    
    # List of words the bot will reply to
    comment_words = ['!register']
    registration_reply = 'Thank you for registering'
    
    # Subreddits to search for
    subreddits = ['progects', 'test']
    
     # This is used in the runbot function to meet the criteria for
     # searching multiple subreddits, or a single subreddit
    subredditstring = ''
                    
    def __init__(self):
        ''' 
        Logs the bot into Reddit. 
        '''
            
                
        self.r = praw.Reddit(user_agent = "Test bot for /r/progects by /u/NEET_Here and /u/triple-take")

        # store user for later use, but not password
        self.bot_name = 'progects_bot1'
        self.password = 'B0tP@ssword'
        print("Logging in...")
        self.r.login(self.bot_name, self.password)


        print("Successfull login...")
        
        
    def cache_create(self, filename, cache_list):
        ''' 
        Pulls information from file and creates cache
        '''
        with open(filename, 'r') as f:
            cache_list = f.read().split('\n')
            cache_list = [x for x in cache_list if x != '']
            
    def update_file(self, filename, cache_list, item):
        '''
        Updates cache list and updates text file for that list.
        Arguments are the filename, cache list and the item to append
        to the list.
        '''
        cache_list.append(item)
        				
        with open(filename, 'w+') as f:
            for thing in cache_list:
                f.write(thing + '\n')
    
    def notify(self, username):
        self.cache_create(self.notif_file, self.notif_list)
        if username not in self.notif_list:
            self.update_file(self.notif_file, self.notif_list, username)
            
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
            comment_text = [x.rstrip('?!@#$%^&*"') for x in comment_text]
            comment_text = [x.lstrip('?@#$%^&*"') for x in comment_text]
            
            for commentWord in comment_text:
                for word in word_list:
                    
                    author = str(comment.author).lower()
                    self.bot_name =  self.bot_name.lower()
                    
                    if word == commentWord and comment.id not in self.cache\
                     and author != self.bot_name:
                        print("Comment found, ID: " + comment.id)
                        print ('Replying...')
                        comment.reply(reply_with)
                        print ('Writing Comment ID to Cache')
                        self.update_file(self.cache_file, self.cache, comment.id)
                        print('Registering User...')
                        self.notify(author)
                        print('Registered')
                        
                    

    def runbot(self):
        ''' 
        Function to run bot.
        '''
        
        
        # Creates temp cache storage
        self.cache_create(self.cache_file, self.cache)
        
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
    
    bot = Bot()
    
    i = 1
    while True:
        print ('Iteration: {0}'.format(i))
        bot.runbot()
        i += 1



if __name__ == '__main__':
    main()
