#!/usr/bin/env python3

import socket
import ssl
import sys

from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse

##########################################################################

HOST = "proj5.3700.network"
PORT = 443
BUFFER = 1000000
CRLF = "\r\n"

# Internal HTTP Response Parse Fields
BODY = "body"
STATUS = "status"
HEADERS = "headers"
COOKIES = "cookies"

# HTTP Status Codes
SUCCESS = 200
FOUND = 302
REDIRECT = 302
FORBIDDEN = 403
NOT_FOUND = 404
ERROR = 503

##########################################################################

socket.setdefaulttimeout(30)


class FakebookHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = list()
        self.secret_flags = list()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for key, value in attrs:
                if key == "href":
                    self.links.append(value)

    def handle_data(self, data):
        if "FLAG: " in data:
            secret_flag = data.split(": ")[1]
            self.secret_flags.append(secret_flag)


class FakebookCrawler:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.csrf_token = None
        self.session_id = None
        self.__login()

    def __login(self):
        """ Log in to CCS Fakebook and store CSRF and session tokens. """
        login_url = f"http://{HOST}/accounts/login/?next=/fakebook/"
        get_login_page_response = self.__get(login_url)

        # Get CSRF token cookie.
        for cookie in get_login_page_response[COOKIES]:
            if "csrftoken" in cookie:
                self.csrf_token = cookie.split("; ")[0].split("=")[1]
        assert self.csrf_token is not None, "ERROR: Failed to get CSRF token from login page."

        # Log in and get session cookie.
        login_content = f"username={self.username}&password={self.password}&csrfmiddlewaretoken={self.csrf_token}&next="
        post_login_page_response = self.__post(login_url, login_content)

        for cookie in post_login_page_response[COOKIES]:
            if "sessionid" in cookie:
                self.session_id = cookie.split("; ")[0].split("=")[1]
        assert self.session_id is not None, "ERROR: Failed to get Session ID after login."

    def __get_cookies(self):
        cookies = dict()
        if self.csrf_token is not None:
            cookies["csrftoken"] = self.csrf_token
        if self.session_id is not None:
            cookies["sessionid"] = self.session_id
        return cookies

    def __parse_http_response(self, data):
        """ Parse raw HTTP response. """
        data = data.strip().split(2 * CRLF)
        response = dict()
        response[BODY] = data[-1] if len(data) > 1 else None
        status_and_headers = data[0].split(CRLF)

        initial_response_line = status_and_headers[0]
        status = int(initial_response_line.split(" ")[1])
        response[STATUS] = status

        response[HEADERS] = dict()
        response[COOKIES] = list()
        headers = status_and_headers[1:]
        for header in headers:
            (key, value) = header.split(": ")
            if key == "Set-Cookie":
                response[COOKIES].append(value)
            else:
                response[HEADERS][key] = value

        return response

    def __send_request(self, request):
        """ Send HTTP request and return parsed response. """
        so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = ssl.wrap_socket(so)
        sock.connect((HOST, PORT))
        sock.send(request.encode())
        response_data = sock.recv(BUFFER).decode()
        sock.close()
        return self.__parse_http_response(response_data)

    def __get(self, url):
        """ Send a HTTP/1.1 GET request. """
        assert HOST in url, f"ERROR: Crawler should only traverse URLs that point to pages on {HOST}"
        url = urlparse(url)

        # Create HTTP initial request line and headers.
        initial_request_line = f"GET {url.path} HTTP/1.1{CRLF}"
        host = f"Host: {url.netloc}{CRLF}"

        # Add cookies.
        request = f"{initial_request_line}{host}{CRLF}"
        cookies = self.__get_cookies()
        if len(cookies) > 0:
            cookies = '; '.join(f'{key}={value}' for key, value in cookies.items())
            cookie_header = f"Cookie: {cookies}{CRLF}"
            request = f"{initial_request_line}{host}{cookie_header}{CRLF}"

        return self.__send_request(request)

    def __post(self, url, content):
        """ Send a HTTP/1.1 POST request. """
        assert HOST in url, f"ERROR: Crawler should only traverse URLs that point to pages on {HOST}"
        url = urlparse(url)

        # Create HTTP initial request line and headers.
        initial_request_line = f"POST {url.path} HTTP/1.1{CRLF}"
        host = f"Host: {url.netloc}{CRLF}"
        from_line = f"From: clauss.b@husky.neu.edu{CRLF}"
        user_agent = f"User-Agent: cs3700-webcrawler/1.0{CRLF}"
        content_type = f"Content-Type: application/x-www-form-urlencoded{CRLF}"
        content_length = f"Content-Length: {len(content)}{CRLF}"

        # Add cookies.
        request = f"{initial_request_line}{host}{from_line}{user_agent}{content_type}{content_length}{CRLF}{content}"
        cookies = self.__get_cookies()
        if len(cookies) > 0:
            cookies = '; '.join(f'{key}={value}' for key, value in cookies.items())
            cookie_header = f"Cookie: {cookies}{CRLF}"
            request = f"{initial_request_line}{host}{from_line}{user_agent}{content_type}{content_length}{cookie_header}{CRLF}{content}"

        return self.__send_request(request)

    def crawl(self):
        """ Crawl CCS Fakebook and return secret flags. """
        secret_flags = list()
        root_page_url = f"http://{HOST}/fakebook/"
        unvisited_pages = deque()
        unvisited_pages.append(root_page_url)
        visisted_pages = set()

        while len(unvisited_pages) > 0:
            next_page_url = unvisited_pages.popleft()
            # print('next page to read: ', next_page_url)

            try:
                get_page_response = self.__get(next_page_url)
                # Mark page as visited.
                visisted_pages.add(next_page_url)

                status = get_page_response[STATUS]
                if status == SUCCESS:
                    # Parse HTML.
                    html = get_page_response[BODY]
                    if html is not None:
                        # print('HTML: ', html)
                        # print('-------------------------')
                        html_parser = FakebookHTMLParser()
                        html_parser.feed(html)

                        # Only crawl the target domain.
                        links = html_parser.links
                        filtered_links = list(filter(lambda link: "/fakebook/" in link, links))
                        for link in filtered_links:
                            link_url = f"http://{HOST}{link}"
                            if link_url not in visisted_pages and link_url not in unvisited_pages:
                                unvisited_pages.append(link_url)

                        # Get any flags for page.
                        secret_flags.extend(html_parser.secret_flags)
                        # Terminate if 5 flags are found.
                        if len(secret_flags) == 5:
                            return secret_flags
                elif status == FOUND or status == REDIRECT:
                    # Crawler tries the request again using the new URL given by the server in the Location header.
                    move_or_redirect_url = get_page_response[HEADERS]["Location"]
                    unvisited_pages.appendleft(move_or_redirect_url)
                elif status == FORBIDDEN or status == NOT_FOUND:
                    # Crawler abandons the URL that generated the error code.
                    pass
                elif status == ERROR:
                    # Crawler re-tries the request for the URL until the request is successful.
                    unvisited_pages.append(next_page_url)
                else:
                    raise Exception(f"ERROR: Unrecognized Status: {status}")
            except socket.timeout:
                raise Exception(f"ERROR: Socket timeout.")

        return secret_flags


def main():
    # Get login information.
    args = sys.argv
    username = args[1]
    password = args[2]

    crawler = FakebookCrawler(username, password)
    secret_flags = crawler.crawl()

    for secret_flag in secret_flags:
        print(secret_flag)


if __name__ == "__main__":
    main()