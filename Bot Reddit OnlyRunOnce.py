"""
/u/PlayStoreLinks__Bot

A bot made by /u/cris9696

UNDER MIT LICENSE

IF YOU FIND ANY BUG OR ANYTHING EVIL
OR ANY EXPLOITABLE PART PLEASE REPORT IT TO ME
"""
import praw                     # reddit wrapper
import requests
import time
import re                       # regex stuff
import pickle                   # dump list and dict to file
import os
import sys
import atexit                   # to handle unexpected crashes or normal exiting
from bs4 import BeautifulSoup   # to parse html
import logging
import urllib

# which is the file i need to save already done applications?
dbFile = "db" + "7"

# which is the file i need to save already done comments?
cacheFile = "/tmp/botcommentscache"

categoriesFolder = "categories"
logging.basicConfig(filename="bot.log", level=logging.INFO,
                    format="%(asctime)s %(message)s")


##### class declaration ####
class App():
    """
    This is the class for an app item it has got a name, a link, a price, a rating etc.
    """
    def __init__(self):
        pass
        
        
##### function declarations #####


# called when exiting the program
def exit_handler():

    os.remove("theBotIsRunning")

    # Dump the caches
    try:
        with open(cacheFile, 'w+') as cache_file:
            pickle.dump(already_done, cache_file)
    except Exception as search_exception:
        pass

    try:
        with open(dbFile, 'w+') as db_file:
            pickle.dump(appList, db_file)
    except Exception as search_exception:
        pass

    log("Shutting Down\n\n\n")

    
    


# register the function that get called on exit
atexit.register(exit_handler)


# take care of "exploits" done by formatting the app name
def cleanString(appName):
    return appName.replace("*", "").replace("~~", "").replace("^", "").replace(
        "\"", " ").replace("]", " ").replace("[", " "). \
        replace("(", " ").replace(")", " ").strip()


#WTF IS THIS, I DONT REMBER IT
def rightTitle(appName):
    appName = appName.title()
    index = appName.find("&")
    while index != -1:
        appName = list(appName)
        appName[index + 1] = appName[index + 1].lower()
        appName = "".join(appName)
        index = int(appName.find("&", index + 1))
    return appName


#find the app name and get the url
def generateComment(comment_to_clean):
    appName = cleanString(comment_to_clean).lower()
    log("Now searching for app: " + appName)

    for app in appList:
        if app.name == appName:
        # generate the first url
            piece_of_comment = "[**" + app.name.title() + "**](" + app.link + ")  -  Price: " + app.price + " - Rating: " + app.rating + "/100 - "
            piece_of_comment += "Search for \"" + appName.encode("ascii", "ignore").title() + "\" on " + \
                                "the [**Play Store**](https://play.google.com/" + \
                                "store/search?q=" + urllib.quote_plus(appName.encode("ascii", "ignore"), "") \
                                + ")\n\n"
            log(app.name + " found on the local cache")
            return piece_of_comment

    try:
        # this is a literal search, it uses " " to match the exact same name
        # if this is not working I use similar search
        #send the request
        request = requests.get("http://play.google.com/store/search?q=\"" +
                               urllib.quote_plus(appName.encode("ascii", "ignore"), "") +
                               "\"&c=apps&hl=en")
        # parse the page we just got to so we can use it as an object for bs4
        page = BeautifulSoup(
            request.text)

        searchResults = page.findAll(attrs={"class": "card-content-link"})
        if len(searchResults) is not 0:
            # we get the link if it exists
            linkObj = searchResults[0]
           
            #if the link is not null
            if linkObj is not None:
                parent = linkObj.parent.parent
                trueName = cleanString(parent.findAll(attrs={"class": "title"})[0].get("title"))
                
                app = App()
                app.name = trueName.lower()
                app.link = "https://play.google.com" + linkObj.get("href")
                app.price = "Free" if parent.findAll(attrs={"class": "price buy"})[0].get_text().strip().lower() == "free" else "Paid"
                app.rating = parent.findAll(attrs={"class": "current-rating"})[0]["style"].strip().replace("width: ","")[:2]
                
                appList.append(app)
                #TODO PRICE AND RATIGNG 

                
                #generate the first url
                piece_of_comment = "[**" + trueName + \
                                   "**](" + app.link + ")  -  Price: " + app.price + " - Rating: " + app.rating + "/100 - "

                #generate the second url (aka search url)
                piece_of_comment += "Search for \"" + appName.encode("ascii", "ignore").title() + \
                                        "\" on" + " the [**Play Store**](https:" + \
                                        "//play.google.com" + "/store/search?q=" + \
                                        urllib.quote_plus(appName.encode("ascii", "ignore"), "") + ")\n\n"
                # log
                log("Search: " + appName + " - Found: " + app.name
                    + " - LITERAL SEARCH")
                

                return piece_of_comment
            else:
                return similarSearch(appName)
        else:
            return similarSearch(appName)
    except Exception as search_exception:
        log("Exception occurred on LITERAL SEARCH: " + str(search_exception))
        time.sleep(3)


def similarSearch(appName):
    # similar search: only if literal search returned no results,
    # we use similar search
    # this means "what google play store thinks is the app we are looking for"
    # it should also fix spelling error
    try:
        # this is a literal search, it uses " " to match the exact same name
        # if this is not working I use similar search
        #send the request
        request = requests.get("http://play.google.com/store/search?q=" +
                               urllib.quote_plus(appName.encode("ascii", "ignore"), "") +
                               "&c=apps&hl=en")
        # parse the page we just got to so we can use it as an object for bs4
        page = BeautifulSoup(
            request.text)

        searchResults = page.findAll(attrs={"class": "card-content-link"})
        if len(searchResults) is not 0:
            # we get the link if it exists
            linkObj = searchResults[0]
           
            #if the link is not null
            if linkObj is not None:
                parent = linkObj.parent.parent
                trueName = cleanString(parent.findAll(attrs={"class": "title"})[0].get("title"))
                
                app = App()
                app.name = trueName.lower()
                app.link = "https://play.google.com" + linkObj.get("href")
                app.price = "Free" if parent.findAll(attrs={"class": "price buy"})[0].get_text().strip().lower() == "free" else "Paid"
                app.rating = parent.findAll(attrs={"class": "current-rating"})[0]["style"].strip().replace("width: ","")[:2]
                
                appList.append(app)
                #TODO PRICE AND RATIGNG 

                
                #generate the first url
                piece_of_comment = "[**" + trueName + \
                                   "**](" + app.link + ")  -  Price: " + app.price + " - Rating: " + app.rating + "/100 - "

                #generate the second url (aka search url)
                piece_of_comment += "Search for \"" + appName.encode("ascii", "ignore").title() + \
                                        "\" on" + " the [**Play Store**](https:" + \
                                        "//play.google.com" + "/store/search?q=" + \
                                        urllib.quote_plus(appName.encode("ascii", "ignore"), "") + ")\n\n"
                # log
                log("Search: " + appName + " - Found: " + app.name
                    + " - LITERAL SEARCH")
                

                return piece_of_comment
            else:
                # log
                log("Can't find an app named " + rightTitle(appName) + "!")
                return False
        else:
            # log
            log("Can't find an app named " + rightTitle(appName) + "!")
            return False
    except Exception as similar_search_exception:
        log("Exception occurred on SIMILAR SEARCH: " +
            str(similar_search_exception))
        time.sleep(3)


#function to exit the bot, will be used when logging will be implemented
def exitBot():
    sys.exit()


# this log and print everything, use this and not print
def log(what="Not defined"):
    print(str(what.encode("ascii", "ignore")))
    logging.info(what)


# check if a comment object is already done
def isDone(comment_to_check):
    # if it is not in the already_done array it means i need to work on it.
    if comment_to_check.id not in already_done:

        # i get its replies
        comment_replies = comment_to_check.replies

        # for each reply
        for reply_to_check in comment_replies:

            # i check if i answered
            if reply_to_check.author.name == "cris9696":

                # i add it to the list
                already_done.append(comment_to_check.id)
                return True
        return False
    else:
        return True


# reply to a comment object with the what string
def reply(what, comment_to_reply_to):
    what += "\n\n------\n\n[^Source ^Code](https://github.com/cris9696/PlayStoreLinks_Bot) ^| [^Feedback/Bug ^report](http://www.reddit.com/r/cris9696) ^| ^Bot ^by ^/u/cris9696 "
    # i try to reply to the comment
    try:
        comment_to_reply_to.reply(what)
    except praw.errors.RateLimitExceeded as rl_error:
        log("Doing too much, sleeping for " + str(rl_error.sleep_time))
        time.sleep(rl_error.sleep_time)
    except Exception as reply_exception:
        log("Exception occurred while replying: " + str(reply_exception))
        time.sleep(3)


# link to a full category of apps, like all reddit apps or facebook apps
def generateCategory(categoryName):
    log("Searching for category: " + categoryName)

    # noinspection PyUnusedLocal
    text = ""

    # noinspection PyUnusedLocal
    dictOfApps = dict()

    categoryName = cleanString(categoryName).lower()

    redditCat = ["reddit", "reddit app", "reddit apps", "reddit client",
                 "reddit clients"]
    facebookCat = ["facebook", "facebook apps", "facebook app",
                   "facebook client", "facebook clients"]
    keyboardCat = ["keyboard", "keyboards"]
    smsCat = ["sms", "sms app", "sms apps", "sms client", "sms clients"]
    if categoryName in redditCat:
        text = "List of **Reddit Apps**:\n\n"
        dictOfApps = pickle.load(open(categoriesFolder + "/reddit", "r+"))
    elif categoryName in facebookCat:
        text = "List of **Facebook Apps**:\n\n"
        dictOfApps = pickle.load(open(categoriesFolder + "/facebook", "r+"))
    elif categoryName in keyboardCat:
        text = "List of **Keyboards**:\n\n"
        dictOfApps = pickle.load(open(categoriesFolder + "/keyboard", "r+"))
    elif categoryName in smsCat:
        text = "List of **SMS Apps**:\n\n"
        dictOfApps = pickle.load(open(categoriesFolder + "/sms", "r+"))
    else:
        return False

    for key in sorted(dictOfApps.iterkeys()):
        text += "[**" + key.title() + "**](" + dictOfApps[key] + ")\n\n"
    return text + "\n\n^(An app is missing? Please write to my author about" + \
        " it)\n\n"


####### main method #######
if __name__ == "__main__":

    # if the bot is already running
    if os.path.isfile("theBotIsRunning"):
        log("Bot already running!")
        exitBot()

    # the bot was not running
    # create the file that tell the bot is running
    open("theBotIsRunning", "w").close()

    try:
	
        # reading login info from a file
        # it should be username (newline) password
        with open("login.txt", "r") as loginFile:
            loginInfo = loginFile.readlines()

        loginInfo[0] = loginInfo[0].replace("\n", "")
        loginInfo[1] = loginInfo[1].replace("\n", "")

        r = praw.Reddit("/u/PlayStoreLinks__Bot by /u/cris9696")
        r.login(loginInfo[0], loginInfo[1])

        # which subreddits i need to work on?
        subreddit = r.get_subreddit("cris9696+AndroidGaming+AndroidQuestio" +
                                    "ns+Android+AndroidUsers+twitaaa+Andro" +
                                    "idApps+AndroidThemes+harley+supermoto+" +
                                    "bikebuilders+careerguidance+mentalflos" +
                                    "s+nexus7+redditsync+nexus5+tasker+LGG2" +
                                    "+androidtechsupport")

        # debug
        # subreddit = r.get_subreddit("cris9696")
    except praw.errors.RateLimitExceeded as error:
        log("Doing too much, sleeping for " + str(error.sleep_time))
        time.sleep(error.sleep_time)
    except Exception as e:
        log("Exception occured on login: " + str(e))
        exitBot()

    log("Logging in succesfull")

    # my regexes
    regex = re.compile("\\blink[\s]*me[\s]*:[\s]*(.*?)(?:\.|$)", re.M)
    regexCategory = re.compile(
        "\\blink[\s]*me[\s]*category[\s]*:[\s]*(.*?)(?:\.|$)", re.M)

    # my debug regex
    # regex = re.compile("\\blink[\s]*medebug[\s]*:[\s]*(.*?)(?:\.|$)",re.M)

    ######### COMMENTS CACHE to avoid analyzing already done comments #########
    # the array filled with entries i already analyzed
    
    if os.path.isfile(cacheFile):
        already_done = []
        # my cache
        with open(cacheFile, "r+") as f:

            # if the file isn"t at its end or empty
            if f.tell() != os.fstat(f.fileno()).st_size:
                already_done = pickle.load(f)

    ########### LINKS CACHE to avoid useless search requests ###########
    appList = []
    if os.path.isfile(dbFile):

        # my cache for links
        with open(dbFile, "r+") as fi:

            # if the file isn"t at its end or empty
            if fi.tell() != os.fstat(fi.fileno()).st_size:
                appList = pickle.load(fi)

################################################################################

    # i try to get the comments
    try:
        log("Getting the comments")

        # noinspection PyUnboundLocalVariable
        subreddit_comments = subreddit.get_comments()
    except Exception as e:
        log("Exception occurred while getting the comments: " + str(e))
        exitBot()

    log("Comments OK")
    try:
        print("Here")
        # for each comment in the subreddit
        # noinspection PyUnboundLocalVariable
        for comment in subreddit_comments:
            alreadyAnswered = False
            generatedComment = ""

            # i get the regex match
            normalMatches = regex.findall(
                comment.body.lower().replace("*", "").replace("~~", "").
                replace("^", ""))

            # i get the regex match for the categories
            categoryMatches = regexCategory.findall(
                comment.body.lower().replace("*", "").replace("~~", "").
                replace("^", ""))

            if len(categoryMatches) > 0:
                alreadyAnswered = isDone(comment)
                generatedComment = ""

                # i need to answer
                if not alreadyAnswered:
                    for match in categoryMatches:

                        # split the match.
                        match = match.split(",")
                        for app in match:
                            toAdd = generateCategory(app)
                            if toAdd is not False:
                                generatedComment += toAdd
                    if len(generatedComment) > 0:
                        reply(generatedComment, comment)

            # if it is something (aka valid comment)
            elif len(normalMatches) > 0:
                alreadyAnswered = isDone(comment)

                # i need to answer
                if not alreadyAnswered:
                    nFound = 0
                    i = 0
                    for match in normalMatches:

                        # split the match.
                        match = match.split(",")
                        if len(match) > 10:
                            generatedComment += "You requested more than 10" + \
                                                " apps. I will only link to" + \
                                                " the first 10.\n\n"
                            log("More than 10 apps found in a comment")

                        # foreach app
                        for app in match:
                            if i < 10:
                                # i check if i need to remove a dot
                                ind = app.find(".")
                                if ind != -1:
                                    app = app[:ind]
                                if len(app.strip()) > 0:
                                    #i generate the comment
                                    toAdd = generateComment(app)
                                    if toAdd is not False:
                                        generatedComment += toAdd
                                        nFound += 1
                                    else:
                                        generatedComment += \
                                            "I am sorry, I can't find " + \
                                            app.title() + ". \n\n"
                                    i += 1
                            else:
                                break
                    if nFound > 0:
                        reply(generatedComment, comment)
    except Exception as e:
        log("Exception occurred in the main try-catch: " + str(e))

    exitBot()
