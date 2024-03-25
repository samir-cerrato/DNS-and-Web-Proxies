# DNS-and-Web-Proxies
Extend web proxy to include a cache, use conditional GET requests, and work with a real web browser.

# Part 2: Proxy cache. 
Part 2 is an intermediate step on the way to making the web proxy
more realistic. The purpose of Part 2 is simply to store the responses from the various web servers
to which clients connect.

# What to cache?
An HTTP response message has the format below. You may additionally see
the header line, Last-Modified:<date> in the HTTP response. In a real web proxy, you would
store only the entity-body along with the URL and date. However, for simplicity, and so that you
don’t have to parse the HTTP responses, you will save the entire HTTP response in your cache.
You will want to keep track of the HTTP response itself, the URL it is associated with, and the
Last-Modified date returned in the response indicating when it was last updated (or simply the
Date value if there is no Last-Modified field). 

# Cache data structure.
You are free to choose whatever approach you’d like to organize your
cache, which might range from a simple dictionary data structure, to storing webpages in files. I
suggest starting with something very simple like a dictionary, so that you can move on to Part 3.

# Part 3: Conditional GET requests.
Rather than have the web proxy automatically forward
on the client’s GET request to the web server, the web proxy will now forward on a modified version
of the GET request. How the request is modified depends on whether the webpage object for the
desired URL is stored in the proxy cache. If the object for the desired URL is not stored in the
proxy cache, the web proxy forwards on the client’s GET request unmodified. If the object for
the desired URL is stored in the proxy cache, the web proxy turns the client’s GET request into
a conditional GET request, using the date information stored in the cache. A conditional HTTP
GET request has the following format:

GET /mathcs/index.html HTTP/1.1\r\n

Host: www.wesleyan.edu\r\n

If-Modified-Since: Sun, 18 Jan 2018 20:43:27 GMT\r\n\r\n

In the response to the conditional GET request, one of two things may occur:

(1) The URL object has changed, or the If-Modified-Since is ignored. In this case,
the web server’s response will be as in Part 1, and the web proxy forwards the web server’s
HTTP response directly to the client.

(2) The URL object has not changed. The web server will return a 304 Not Modified
status code in its response rather than a 200 OK status code. In this case what the web
proxy has stored in its cache is what is returned to the client. The web proxy creates an
HTTP response containing the information in its cache, and forwards this response to the
client. If the web proxy is storing entire responses in its cache, rather than just the entity-
body, as you will be doing, then the web proxy simply returns what is stored in its cache,
which should be a validly formatted HTTP Response.

Several websites you might wish to use to test conditional requests include example.com and
httpforever.com.

# Part 4: Testing with a web browser. 
In Part 4, you will test your web proxy using a web
browser as a client instead of your web client. To do this, choose your favourite browser and change
the proxy settings to use the web proxy listening on localhost:50007: i.e., to use your web proxy.
Pathname parsing. When a web browser uses a proxy, it includes the full URL ncluding
the hostname as the path in the GET line of the request. This pathname, however, will not be
parseable by web servers. Therefore, the web proxy must now check the pathname it is given,
identify whether it is a complete URL, and if so create a new HTTP request that includes only the
path and object portion of the URL in its GET line.

You may find the following helpful when looking at HTTP requests and responses.

•RFC 2616: Hypertext Transfer Protocol – HTTP/1.1. https://tools.ietf.org/html/rfc2616

•RFC 7232: Hypertext Transfer Protocol (HTTP/1.1): Conditional Requests.

https://tools.ietf.org/html/rfc7232
