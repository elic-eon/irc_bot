import socket
import sys
import logging
import time
import operator
import win32api
import win32con

VK_CODE = {
    'backspace':0x08,
    'enter':0x0D,
    'left':0x4C,
    'up':0x49,
    'right':0x4B,
    'down':0x4A,
    'x':0x58,
    'z':0x5A
}
def press(i):
    win32api.keybd_event(VK_CODE[i], 0, 0, 0)
    time.sleep(0.2)
    win32api.keybd_event(VK_CODE[i],0 ,win32con.KEYEVENTF_KEYUP ,0)

def splitword(cmd):
    cmd_len = len(cmd)
    start_pos = 0
    ret = dict()
    ret["up"] = 0
    ret["down"] = 0
    ret["left"] = 0
    ret["right"] = 0
    ret["start"] = 0
    ret["select"] = 0
    ret["a"] = 0
    ret["b"] = 0

    while cmd_len > 0:
        if cmd.startswith("up", start_pos) == True:
            ret["up"] += 1
            cmd_len -= 2
            start_pos += 2
        elif cmd.startswith("down", start_pos) == True:
            ret["down"] += 1
            cmd_len -= 4
            start_pos += 4
        elif cmd.startswith("left", start_pos) == True:
            ret["left"] += 1
            cmd_len -= 4
            start_pos += 4
        elif cmd.startswith("right", start_pos) == True:
            ret["right"] += 1
            cmd_len -= 5
            start_pos += 5
        elif cmd.startswith("start", start_pos) == True:
            ret["start"] += 1
            cmd_len -= 5
            start_pos += 5
        elif cmd.startswith("select", start_pos) == True:
            ret["select"] += 1
            cmd_len -= 6
            start_pos += 6
        elif cmd.startswith("a", start_pos) == True:
            ret["a"] += 1
            cmd_len -= 1
            start_pos += 1
        elif cmd.startswith("b", start_pos) == True:
            ret["b"] += 1
            cmd_len -= 1
            start_pos += 1
        else:
            return None
    return ret

def voting(cmd_dict, result):
    result["up"] += cmd_dict["up"]
    result["down"] += cmd_dict["down"]
    result["left"] += cmd_dict["left"]
    result["right"] += cmd_dict["right"]
    result["start"] += cmd_dict["start"]
    result["select"] += cmd_dict["select"]
    result["a"] += cmd_dict["a"]
    result["b"] += cmd_dict["b"]
    return result

def sendkey(cmd):
    cmd_len = len(cmd)
    start_pos = 0

    while cmd_len > 0:
        if cmd.startswith("up", start_pos) == True:
            press("up")
            cmd_len -= 2
            start_pos += 2
        elif cmd.startswith("down", start_pos) == True:
            press("down")
            cmd_len -= 4
            start_pos += 4
        elif cmd.startswith("left", start_pos) == True:
            press("left")
            cmd_len -= 4
            start_pos += 4
        elif cmd.startswith("right", start_pos) == True:
            press("right")
            cmd_len -= 5
            start_pos += 5
        elif cmd.startswith("start", start_pos) == True:
            press("enter")
            cmd_len -= 5
            start_pos += 5
        elif cmd.startswith("select", start_pos) == True:
            press("backspace")
            cmd_len -= 6
            start_pos += 6
        elif cmd.startswith("a", start_pos) == True:
            press("z")
            cmd_len -= 1
            start_pos += 1
        elif cmd.startswith("b", start_pos) == True:
            press("x")
            cmd_len -= 1
            start_pos += 1
        else:
            return
server = "irc.twitch.tw"
channel = "#k6074282"
botnick = "irc_bot25638201"
mode = "normal"
auth = "wemhbtwacmyu7sl70h1yxkxoktoek0"
timer = None
vote = dict()
longest = ""
repeat = 0
longest_name = ""

logger = logging.getLogger('irc_log')
hdlr = logging.FileHandler('irc.log')
formatter = logging.Formatter('%(asctime)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ("connect to:"+server)
irc.connect((server, 6667))
irc.send(("USER k6074282\r\n").encode("ascii"))
irc.send(("PASS "+ auth + "\r\n").encode("ascii"))
irc.send(("NICK "+ botnick +"\n").encode("ascii"))
irc.send(("PRIVMSG nickserv :iNOOPE\r\n").encode("ascii"))
irc.send(("JOIN "+ channel +"\n").encode("ascii"))

while 1:
    text=irc.recv(2040).decode("ascii")
    print (text)

    if text.find('PING') != -1:
        irc.send(('PONG ' + text.split()[1] + '\r\n').encode("ascii"))

    if text.find(("PRIVMSG "+channel +" :")) != -1:
        msgs = text.split()
        nick = msgs[0].split(":")[1].split("!")[0]
        cmd = msgs[3].split(":")[1]
        if mode == "normal":
            msg = "User: " + nick + " cmd: " + cmd + "(" + cmd + ")"
            print (msg)
            logger.info(msg)
            sendkey(cmd)
        elif mode == "democracy":
            if timer == None:
                timer = time.time()
                vote["up"] = 0
                vote["down"] = 0
                vote["left"] = 0
                vote["right"] = 0
                vote["start"] = 0
                vote["select"] = 0
                vote["a"] = 0
                vote["b"] = 0
                irc.send(("PRIVMSG " + channel + ": Start voting\r\n").encode("ascii"))
                print (('PRIVMSG ' + channel + " Start voting"))
            elif time.time() - timer > 6.0:
                timer = time.time()
                if vote != None:
                    cmd = max(vote.items(), key=operator.itemgetter(1))[0]
                    nick = "democracy"
                    msg = "User: " + nick + " cmd: " + cmd + "(" + cmd + ")"
                    print (vote)
                    print (msg)
                    logger.info(msg)
                    sendkey(cmd)
                vote["up"] = 0
                vote["down"] = 0
                vote["left"] = 0
                vote["right"] = 0
                vote["start"] = 0
                vote["select"] = 0
                vote["a"] = 0
                vote["b"] = 0
                irc.send(("PRIVMSG " + channel + ": Start voting\r\n").encode("ascii"))
                print (('PRIVMSG ' + channel + " Start voting\n"))
            parsed = splitword(cmd)
            if parsed != None:
                vote = voting(parsed, vote)
        elif mode == "violence":
            if timer == None:
                timer = time.time()
                longest = ""
                repeat = 0
            elif time.time() - timer > 6.0:
                timer = time.time()
                if longest != "":
                    nick = "violence"
                    msg = "User: " + nick + " cmd: "
                    for i in range(repeat):
                        msg += longest
                        sendkey(longest)
                    print (msg)
                    logger.info(msg)
                longest = ""
                repeat = 0
            parsed = splitword(cmd)
            print (parsed)
            long_cmd = max(parsed.items(), key=operator.itemgetter(1))[0]
            if parsed[long_cmd] > repeat:
                longest = long_cmd
                repeat = parsed[long_cmd]
                print(longest)
    if text.find(("PRIVMSG "+botnick +" :")) != -1:
        msgs = text.split()
        nick = msgs[0].split(":")[1].split("!")[0]
        cmd = msgs[3].split(":")[1]
        if nick == "ssuyi":
            mode = cmd
            irc.send(("PRIVMSG " + nick + " : mode changed\r\n").encode("ascii"))
