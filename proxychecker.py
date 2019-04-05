#!/usr/bin/env python
import time, sys, datetime
import threading, getopt
is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue
    import urllib2
else:
    import queue as Queue
    import urllib.request as urllib2

output = {
    'NOK': {
        'total': 0,
        'list': []
    },
    'OK': {
        'total': 0,
        'list': []
    },
}
if __name__ != '__main__':
    tgl = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    outfile_ok_http = open('result/http_proxy_detected_'+tgl+'.txt','w')
    outfile_ok_http = open('result/http_proxy_detected_'+tgl+'.txt','a')
    outfile_ok_https = open('result/https_proxy_detected_'+tgl+'.txt','w')
    outfile_ok_https = open('result/https_proxy_detected_'+tgl+'.txt','a')
    debug_threadURL = open('result/threadURL_debug'+tgl+'.txt','w')
    debug_threadURL = open('result/threadURL_debug'+tgl+'.txt','a')
c = 0
total_c = 0
class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        global debug_threadURL
        try:
            threading.Thread.__init__(self)
            self.queue = queue
        except Exception as e:
            debug_threadURL.write(str(datetime.datetime.now())+" - ErrException: "+str(e))
            debug_threadURL.flush()        

    def run(self):
        global outfile_ok_http, total_c, debug_threadURL
        while True:
            #grabs host from queue
            proxy_info_all = self.queue.get()
            try:
                HR_NAME, proxy_info = proxy_info_all.split('|')
            except:
                proxy_info = proxy_info_all
            try:
                proxy_handler = urllib2.ProxyHandler({
                    'http':proxy_info,
                    'https':proxy_info,
                    })
                opener = urllib2.build_opener(proxy_handler)
                opener.addheaders = [('User-agent','Mozilla/5.0')]
                urllib2.install_opener(opener)
                http_proxy_flag, https_proxy_flag = False, False
                try:
                    req = urllib2.Request("http://www.google.com")
                    sock=urllib2.urlopen(req, timeout= 1)
                    rs = sock.read(1000)
                    if '<title>Google</title>' in rs:
                        http_proxy_flag = True
                        # output['OK']['total'] += 1
                        # output['OK']['list'].append(str(proxy_info_all))
                    else:
                        http_proxy_flag = False
                        # output['NOK']['total'] += 1
                        # outfile_nok.write(proxy_info+'\n')
                        # outfile_nok.flush()
                        # output['NOK']['list'].append(proxy_info)
                except:
                    http_proxy_flag = False
                try:
                    req = urllib2.Request("https://www.google.com")
                    sock=urllib2.urlopen(req, timeout= 1)
                    rs = sock.read(1000)
                    if '<title>Google</title>' in rs:
                        https_proxy_flag = True
                        # output['OK']['total'] += 1
                        # output['OK']['list'].append(str(proxy_info_all))
                    else:
                        https_proxy_flag = False
                        # output['NOK']['total'] += 1
                        # outfile_nok.write(proxy_info+'\n')
                        # outfile_nok.flush()
                        # output['NOK']['list'].append(proxy_info)
                except:
                    https_proxy_flag = False

                if http_proxy_flag:
                    outfile_ok_http.write(str(proxy_info_all)+'\n')
                    outfile_ok_http.flush()
                if https_proxy_flag:
                    outfile_ok_https.write(str(proxy_info_all)+'\n')
                    outfile_ok_https.flush()

                # percent=int(float(float(c)/float(total_c))*100)
                # sys.stdout.write("\rTotal progress: OK: %d | NOK: %d | Total: %d  \r" % (output['OK']['total'], output['NOK']['total'], c) )
                # sys.stdout.flush()
                #signals to queue job is done
            except Exception as e:
                debug_threadURL.write(str(datetime.datetime.now())+" - ErrException: "+str(e))
                debug_threadURL.flush()
            
            self.queue.task_done()

def multicheck_proxy(input_file="list_proxy", hosts='', threads=10):
    global output, c, total_c
    queue = Queue.Queue()
    output = {
        'NOK': {
            'total': 0,
            'list': []
        },
        'OK': {
            'total': 0,
            'list': []
        },
    }
    if hosts == '':
        hosts = [host.strip() for host in open(input_file).readlines()]
    total_c = len(hosts)
    starttime = datetime.datetime.now()
    #spawn a pool of threads, and pass them queue instance
    list_threads = []
    for i in range(threads):
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()
        list_threads.append(t)

    #populate queue with data   
    for host in hosts:
        queue.put(host)

    #wait on the queue until everything has been processed     
    queue.join()

    for t in list_threads:
        t.stop = True

    endtime = datetime.datetime.now()
    processed_time = endtime - starttime
    print(str(starttime)+" Start processed")
    print(str(endtime)+" Done processed")
    print("-"*28)
    print("Duration:"+str(processed_time))
    print("Total Non-Proxy-Enabled IP",output['NOK']['total'])
    print("Total Proxy-Enabled IP",output['OK']['total'])
    print("Total List Proxy-Enabled IP",output['OK']['list'])

    outfile_ok_http.close()
    return output

def singlecheck_proxy(ip=''):
    proxy_handler = urllib2.ProxyHandler({
        'http':ip,
        'https':ip,
        })
    opener = urllib2.build_opener(proxy_handler)
    opener.addheaders = [('User-agent','Mozilla/5.0')]
    urllib2.install_opener(opener)
    try:
        req = urllib2.Request("http://www.google.com")
        sock=urllib2.urlopen(req, timeout= 1)
        rs = sock.read(1000)
        if '<title>Google</title>' in rs:
            return "http proxy detected!"
        else:
            return "http proxy undetected!"
    except Exception as e:
        return "http proxy undetected!"
    try:
        req = urllib2.Request("https://www.google.com")
        sock=urllib2.urlopen(req, timeout= 1)
        rs = sock.read(1000)
        if '<title>Google</title>' in rs:
            return "https proxy detected!"
        else:
            return "https proxy undetected!"
    except Exception as e:
        return "https proxy undetected!"

if __name__ == '__main__':
    # multicheck_proxy(input_file='proxylist', threads=100)
    argv = sys.argv[1:]
    ip = ""
    option = "singlecheck"
    try:
        opts, args = getopt.getopt(argv,"h:",[
        "option=",
        "ip=",
        ])
    except Exception as e:
        print(str(e))
        sys.exit(0)
    for opt, arg in opts:
        if opt in ("--ip"):
          ip = arg
        elif opt in ("--option"):
          option = arg
    
    if option == 'singlecheck':
        result = singlecheck_proxy(ip=ip)
        print(result)

    elif option == 'multicheck':
        tgl = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        outfile_ok_http = open('result/http_proxy_detected_'+tgl+'.txt','w')
        outfile_ok_http = open('result/http_proxy_detected_'+tgl+'.txt','a')
        outfile_ok_https = open('result/https_proxy_detected_'+tgl+'.txt','w')
        outfile_ok_https = open('result/https_proxy_detected_'+tgl+'.txt','a')
        debug_threadURL = open('result/threadURL_debug'+tgl+'.txt','w')
        debug_threadURL = open('result/threadURL_debug'+tgl+'.txt','a')
        result = multicheck_proxy(input_file="list_proxy", threads=10)
        print(result)