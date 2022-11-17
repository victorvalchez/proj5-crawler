## Project 5:  Web Crawler
### Description  
This project is intended to get familiar with the HTTP protocol. HTTP is (arguably) the most important application-level protocol on the Internet today: the Web runs on HTTP, and increasingly other applications use HTTP as well (including BitTorrent, streaming video, Facebook and Twitter’s social APIs, etc.).

The goal of this assignment is to implement a web crawler that gathers data from a fake social networking website that the University has set up. There are several educational goals of this project:
- To get exposed to the HTTP protocol, which underlies a large (and growing) number of applications and services today.
- To see how web pages are structured using HTML.
- To give experience implementing a client for a well-specified network protocol.
- To understand how web crawlers work, and how they are used to implement popular web services today.

### Approach  
We started with the code provided by the professors, which implements basic argument parsing and the sending of a GET request that was not even working to get started with the idea. 

There is one main method that does all the crawling, that method is _run_, which first calls the method _login_ (explained later) and then adds the homepage to a queue of unvisited pages which will be used to crawl through all of them. To feed the queue we use another data structure, a set, that keeps track of all the pages visited or pending to visit: if a page is already in that set, we know that there’s no need to add it again in the queue.

After that, it will get in a loop until all the pages have been visited or the 5 flags have been found, and that loop will check the HTTP code received, parse it out,  and do the appropriate thing as mentioned in the statement of the project.

Now, we are going to comment on the main methods used for this project.

#### Login
The _login_ method first sends the URL using the _send_get_and_receive_ method, gets the response and parses it, then gets the CSRF Token and uses it to send the login credentials to the Fakebook server using the _send_login_ method, retrieving the SessionID and storing it for later use.

#### Send_Get_And_Receive
This method is used to send a GET request. It first checks if we can send that URL because it corresponds to our server domain, then we parse it and build the request with the appropriate fields, and lastly, we open an SSL socket and send the request to the server and port and then read and return the received data.

#### Parse_Response
This method basically gets the response from the server and removes all spaces in order to read it more easily, then creates a dictionary with the corresponding needed keys and stores each value there. Finally returning the created dictionary.

#### Send_Login
The _send_login_ function is very similar to _send_get_and_receive_. The only difference is that here we send a POST request, and so the headers we need to add are different: from_line, user_agent, content_type, and content_length. Also, the cookie_header here does not contain the sessionID, as it is something we get after login.

#### CustomHTMLParser
CustomHTMLParser is a child of the class HTMLParser, that provides all the necessary tools to parse an HTML document. we just need to send the HTML as a parameter of the function _feed_ that this parent class provides, and the class will make all the necessary calls to other methods of the class called _handle_”something”_ with the parsed information. Then, in our custom class we override the methods _handle_starttag_ and _handle_data_:

    _handle_starttag_: is being called after the parser reads an HTML tag, and then we call our _feed_queue_ method in case it is an ‘a’ tag (hyperlink).

    _handle_data_: is being called after the parser reads arbitrary data, like the content in an h2 header. If the data contains the flag, then we call our _add_flag_method to save the flag.

### Run
This method contains the algorithm to crawl the website. First of all, we call the login method and then we start the loop that goes over all the URLs. In every iteration, we just pop the next page in the queue, send the request and read and parse the response, and depending on the status code received we take the following actions:

- OK (200) : Parse the HTML. Our _CustomHTMLParser_ will automatically make the calls to the methods _feed_queue_ and _add_flag_ that respectively update the queue with new links (if they are on the specified server and not in the visited set) and save the flags found (if any).
- FOUND (302) : Append the URL found at the beginning of the queue, to make the crawler try the request again using this new URL.
- FORBIDDEN (403) : Abandon the URL
- NOT_FOUND (404) : Abandon the URL
- UNAVAILABLE (503) : Retry the request, by adding it again in the queue, until it is successful

Finally, we exit the loop if there are no more pages to visit or if all the flags have been found.


### Challenges and difficulties
The most challenging part was figuring out how to start the connection and do the login at the beginning. We were not very familiar with HTTP, but the recommended tutorial “HTTP Made Really Easy” helped us a lot. After understanding the syntax (and doing the parsing job), it was not that hard to establish the connection, as we have been working with sockets all semester. 

Moreover, we were unsure of how to parse the HTML, and discovering that we could use this HTMLParser overriding its methods was incredibly useful. We were not familiar with how inheritance works in Python but it was pretty straightforward.

Finally, an issue that was hard to detect but easy to solve was how we treated the response_dict['status'] == FOUND case. Our code was taking too long to find the flags and the issue was that we were adding these “FOUND” locations at the end of the queue. By putting them at the beginning, the runtime decreased significantly, but we had to stop using the Queue built-in structure to use a deque instead.
 
### Testing and debugging
We tested and debugged our code by constantly printing all the received data and checking what issues we were getting. For example, we solved a login issue by printing all the messages and responses, to realize that our _cookie_header_ was not correct.

However, to do all the “parse” logic we created small python programs with some message examples. We developed and tested all this code there, before adding it to the main program. By doing this, when we were getting errors in the main program we knew that all this parsing functionality was not the issue because it was already tested.

