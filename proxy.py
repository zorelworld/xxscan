import urllib2
import re
import threading
import time


rawProxyList = []
checkedProxyList = []

targets = []
for i in xrange(1,10):
        target = r"http://www.samair.ru/proxy/proxy-0%d.htm" % i
        targets.append(target)


p = re.compile(r'\d+\.\d+\.\d+\.\d+:\d+')


class ProxyGet(threading.Thread):
    def __init__(self,target):
        threading.Thread.__init__(self)
        self.target = target

    def getProxy(self):
        print self.target
        req = urllib2.urlopen(self.target)
        result = req.read()
        rawProxyList.extend(re.findall('\d+\.\d+\.\d+\.\d+:\d+', result))
    def run(self):
        self.getProxy()


class ProxyCheck(threading.Thread):
    def __init__(self,proxyList):
        threading.Thread.__init__(self)
        self.proxyList = proxyList
        self.timeout = 5
        #self.testUrl = "http://www.baidu.com/"
        #self.testStr = "030173"
        self.testUrl = "http://www.google.com"
        self.testStr = "googleg_lodp.ico"

    def checkProxy(self):
        cookies = urllib2.HTTPCookieProcessor()
        for proxy in self.proxyList:
            proxyHandler = urllib2.ProxyHandler({"http" : r'http://%s' % proxy})
            #print r'http://%s:%s' %(proxy[0],proxy[1])
            opener = urllib2.build_opener(cookies,proxyHandler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0')]
            #urllib2.install_opener(opener)
            t1 = time.time()

            try:
                #req = urllib2.urlopen("http://www.baidu.com", timeout=self.timeout)
                req = opener.open(self.testUrl, timeout=self.timeout)
                #print "urlopen is ok...."
                result = req.read()
                #print "read html...."
                timeused = time.time() - t1
                pos = result.find(self.testStr)
                #print "pos is %s" %pos

                if pos > 1:
                    checkedProxyList.append((proxy,timeused))
                    #print "ok ip: %s %s %s %s" %(proxy[0],proxy[1],proxy[2],timeused)
                else:
                     continue
            except Exception,e:
                #print e.message
                continue

    def run(self):
        self.checkProxy()

if __name__ == "__main__":
    getThreads = []
    checkThreads = []


for i in range(len(targets)):
    t = ProxyGet(targets[i])
    getThreads.append(t)

for i in range(len(getThreads)):
    getThreads[i].start()

for i in range(len(getThreads)):
    getThreads[i].join()

print '.'*10+"%s proxys" %len(rawProxyList) +'.'*10


for i in range(20):
    t = ProxyCheck(rawProxyList[((len(rawProxyList)+19)/20) * i:((len(rawProxyList)+19)/20) * (i+1)])
    checkThreads.append(t)

for i in range(len(checkThreads)):
    checkThreads[i].start()

for i in range(len(checkThreads)):
    checkThreads[i].join()

print '.'*10+"%s proxy is right" %len(checkedProxyList) +'.'*10


proxy_ok = []
f= open("proxy_list.txt",'w+')
for proxy in sorted(checkedProxyList,cmp=lambda x,y:cmp(x[1],y[1])):
    if proxy[1] < 8:
        #print "checked proxy is: %s:%s\t%s\t%s" %(proxy[0],proxy[1],proxy[2],proxy[3])
        proxy_ok.append((proxy[0],proxy[1]))
        f.write("%s\t%s\n"%(proxy[0],proxy[1]))
f.close()


#db_insert(proxy_ok)
