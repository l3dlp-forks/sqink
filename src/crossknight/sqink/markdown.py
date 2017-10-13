# coding:utf-8
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import markdown
import mistune
from time import time


def _formatDatetime(dt):
    now = time()
    tzOffset = (datetime.fromtimestamp(now) - datetime.utcfromtimestamp(now)).total_seconds()
    tzInfo = timezone(timedelta(seconds=tzOffset))
    return str(dt.replace(tzinfo=timezone.utc).astimezone(tzInfo).replace(tzinfo=None))


def renderHtml(note):
    docTitle = note.title if note.title else ""
    title = ""
    if note.title or note.starred:
        title = "<h2 class=\"note-info\">"
        if note.starred:
            title += "<img src=\"images/star-16x16.png\"/> "
        if note.title:
            title += note.title
        title += "</h2>"
    dates = ""
    if note.createdOn or note.lastModified:
        dates += "<div class=\"note-info note-dates\">"
        if note.createdOn:
            dates += " <img src=\"images/created-16x16.png\"/> <span>" + _formatDatetime(note.createdOn) +\
                     "</span> &nbsp"
        if note.lastModified:
            dates += " <img src=\"images/modified-16x16.png\"/> <span>" + _formatDatetime(note.lastModified) + "</span>"
        dates += "</div>"
    tags = ""
    if note.tags:
        tags = "<div class=\"note-info note-tags\"> <img src=\"images/tag-16x16.png\"/> "
        for tag in note.tags:
            tags += "<span>" + tag + "</span> "
        tags += "</div>"
    separator = "<div class=\"note-separator\"></div>" if title or dates or tags else ""
    photo = "<p class=\"note-photo\"><img src=\"notes/" + note.uuid + ".jpg\"/></p>" if note.photo is not None else ""
    content, diagram = _renderHtmlWithMistune(note.text) if note.text else ("", False)
    styles = ""
    if diagram:
        styles = "<link type=\"text/css\" rel=\"stylesheet\" href=\"styles/mermaid.forest.min.css\"/>"
    javascript = ""
    if diagram:
        javascript = "<script type=\"text/javascript\" src=\"js/mermaid.min.js\"></script>" +\
                "<script type=\"text/javascript\">mermaid.initialize({startOnLoad:true," +\
                "flowchart:{useMaxWidth:false},sequenceDiagram:{useMaxWidth:false}});</script>"

    html = "<!DOCTYPE html><html><head>" +\
           "<meta charset=\"UTF-8\"/>" +\
           styles +\
           "<link type=\"text/css\" rel=\"stylesheet\" href=\"styles/note.css\"/>" +\
           "<title>" + docTitle + "</title>" +\
           javascript +\
           "</head><body class=\"note\">" +\
           title +\
           dates +\
           tags +\
           separator +\
           photo +\
           content +\
           "</body></html>"
    note.html = html
    return note


def _renderHtmlWithMarkdown(text):
    return markdown.markdown(text, output_format="xhtml1"), False


def _renderHtmlWithMistune(text):
    options = {
        "escape": True,
        "use_xhtml": True
    }
    renderer = _MermaidRenderer(**options)
    return mistune.markdown(text, renderer=renderer, **options), renderer.hasDiagram


class _MermaidRenderer(mistune.Renderer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hasDiagram = False

    def block_code(self, code, lang=None):
        if code.split(maxsplit=1)[0] in ["graph", "sequenceDiagram", "gantt"]:
            self.hasDiagram = True
            return "<div class=\"mermaid\">\n" + code + "\n</div>\n"
        return super().block_code(code, lang)
