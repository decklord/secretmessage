from django import template
import settings

register = template.Library()

class MediaNode(template.Node):
    def __init__(self, file_type, file_path):
        self.file_type = file_type
        if not file_path.endswith(file_type) and file_type != "img":
            file_path = "%s.%s" % (file_path, file_type)
        self.file_path = file_path

    def render(self, context):
        if self.file_type == 'js':
            tag = "<script type='text/javascript' src='%sjs/%s'></script>" % (settings.MEDIA_URL, self.file_path)
        if self.file_type == 'css':
            tag = "<link rel='stylesheet' type='text/css' href='%scss/%s'>" % (settings.MEDIA_URL, self.file_path)
        if self.file_type == 'img':
            tag = "<img src='%simg/%s'/>" % (settings.MEDIA_URL, self.file_path)

        return tag


def media_tag(parser, token):
    (media_type, media_file) = tuple(token.split_contents()[1].split(":"))
    return MediaNode(media_type, media_file)

register.tag('media',media_tag)
