from random import randint


def getRandomIntFrom1toGiven(top):
    if top <= 1:
        return 1
    else:
        return randint(1, top)



def getCategory(txt):
    if txt == 'mbpst':
        return "MBP Script Tutorial"
    elif txt == "mbpfaq":
        return "MBP FAQ"
    elif txt == "video":
        return "Video Demos"
    elif txt == "mqarules":
        return "MQA Rules"
    elif txt == "mqafaq":
        return "MQA FAQ"
    elif txt == "blog":
        return "Blog"

    return "Not Categorized."