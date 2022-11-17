## Project 5:  Web Crawler
### Description  
This project is intended to get familiar with the HTTP protocol. HTTP is (arguably) the most important application-level protocol on the Internet today: the Web runs on HTTP, and increasingly other applications use HTTP as well (including BitTorrent, streaming video, Facebook and Twitter’s social APIs, etc.).

- The goal of this assignment is to implement a web crawler that gathers data from a fake social networking website that the University has set up. There are several educational goals of this project:
- To get exposed to the HTTP protocol, which underlies a large (and growing) number of applications and services today.
- To see how web pages are structured using HTML.
- To give experience implementing a client for a well-specified network protocol.
- To understand how web crawlers work, and how they are used to implement popular web services today.

### Approach  
We started with the code provided by the professors, which implements basic argument parsing and the sending of a GET request that was not even working to get started with the idea. 
There is one main method that does all the crawling, that method is _run_, which first calls the method _login_ (explained later) and then adds the homepage to a queue of unvisited pages which will be used to crawl through all of them and with another variable that stores all the pages visited will store the pages that we have left to visit. After that, it will get in a loop until all the pages have been visited or the 5 flags have been found, and that loop will check the HTTP code received and do the appropriate thing as mentioned in the statement of the project. (maybe add lo de HTTP parser)
Now, we are going to comment on the main methods used for this project.

#### Login
The _login_ method first sends the URL using the _send_get_and_receive_ method, gets the response and parses it, then gets the CSRF Token and uses it to send the login credentials to the Fakebook server using the _send_login_ method, retrieving the SessionID and storing it for later use.

#### Send_Get_And_Receive
Used to send a GET request. It first checks if we can send that URL because it corresponds to our server domain, then we parse it and build the request with the appropriate fields, and lastly, we open an SSL socket and send the request to the server and port and then read and return the received data.

#### Parse_Response
This method basically gets the response from the server and removes all spaces in order to read it more easily, then creates a dictionary with the corresponding needed keys and stores each value there. Finally returning the created dictionary.

#### Send_Login
sjkfksjf

#### Get_Cookies
jksfkshf

#### CustomHTMLParser
ksjfksfs
 
### Challenges and difficulties
kshfkhsf
 
### Testing and debugging
We could only test and debug by constantly printing all the received data and checking what issues we were getting.

