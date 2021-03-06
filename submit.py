import datetime
import urllib.parse
import urllib.request
import lxml.html
import traceback


# --- UTILS ---
def awesomeness_file_append(fname, content):
    with open(fname, 'r+') as f:
        old_content = f.read()

    with open(fname, 'w') as f:
        f.write(old_content.replace("<!-- INSERT AWESOMENESS HERE -->",
                                    "<!-- INSERT AWESOMENESS HERE -->\n" + content))


def read_body(environ):
    return environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('utf-8')

def get_post(environ):
    qs = urllib.parse.parse_qs(read_body(environ))
    return {k: v[0] for k, v in qs.items()}


# --- APP ---
def app(environ, start_response):
    if environ['PATH_INFO'].endswith('/title/'):
        return handle_title(environ, start_response)
    if environ['REQUEST_METHOD'] == "POST":
        return handle_submit(environ, start_response)
    else:
        return handle_get(environ, start_response)


def handle_title(environ, start_response):
    url = read_body(environ)
    try:
        title = lxml.html.parse(urllib.request.urlopen(url)).find(".//title").text.encode('utf-8')
    except:
        traceback.print_exc()
        title = b""
    start_response("200 bittesehr", [("Content-Length", str(len(title))),
                                     ("Content-Type", "text/plain; charset=utf-8")])
    return [title]


def handle_submit(environ, start_response):
    post = get_post(environ)
    awesomeness_file_append("awesomeness.html",
"""
  <li>
    <span class=date>{date}</span>
    <span class=url><a href="{url}">{title}</a></span>
    <span class=awesome>{maybeAwesome}</span>
  </li>
""".format(
        maybeAwesome=("AWESOME!" if post.pop("awesome", '') == 'on' else ""),
        date=datetime.datetime.now().strftime("%h %d, %Y"),
        url=post["url"],
        title=post["title"]
    ))

    start_response("302 hier geht's weiter", [("Location", "..")])
    return []

def handle_get(environ, start_response):
    with open("submit.html") as f:
        form = f.read().encode('utf-8')
    start_response("200 bittesehr", [("Content-Length", str(len(form)))])
    return [form]


# --- MAIN ---
if __name__ == '__main__':
    import wsgiref.simple_server
    import config
    server = wsgiref.simple_server.make_server(config.HOST, config.PORT, app)
    server.serve_forever()
else:
    application = app
