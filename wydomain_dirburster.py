import sys
import requests
import random
import string
import multiprocessing

def brutedir(url, dictname='dir.csv'):
    try:
        result=[]
        if url[:-1] != "/":
            url = url + "/"
        pattern = ""
        rnd = random.randint(5, 30)
        rnd_string = ''.join([random.choice(string.letters) for c in xrange(0,rnd)])
        requests.packages.urllib3.disable_warnings()
        response = requests.get(url + rnd_string,headers={"referer": url},verify=False)
        if "404" in response.text:
            pattern = "404"
        elif "not found" in response.text:
            pattern = "not found"
        for line in [line.strip() for line in open(dictname)]:
            response = requests.get(url + line,headers={"referer": url},verify=False)
            if response.status_code == 200 and pattern not in response.text:
                print "   [+] %s" % url+line
                result.append(url+line)
        return result

    except Exception, e:
        return ""


def start_attack(reverse_info):
    domains=[]
    result=[]
    for i in reverse_info:
        for j in i:
            domains.append(j)

    pool = multiprocessing.Pool(processes=60)
    reverse_info = {}
    result = []
    for i in xrange(len(domains)):
        domain=domains[i]
        result.append(pool.apply_async(brutedir,(domain,)))
    pool.close()
    pool.join()
    return result

if __name__ == "__main__":
    if len(sys.argv) == 2:
        brutedir(sys.argv[1])
        #print get_subdomain_run(sys.argv[1])
        sys.exit(0)
    else:
        print ("usage: %s domain" % sys.argv[0])
        sys.exit(-1)
