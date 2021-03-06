from jinja2 import Markup
from flask import current_app
from wtforms.fields import TextAreaField
from wtforms.widgets import HTMLString, TextArea

pagedown_pre_html = '<div class="flask-pagedown">'
pagedown_post_html = '</div>'
preview_html = '''
<div class="card">
<div class="card-content">
<div class="flask-pagedown-preview" id="flask-pagedown-%(field)s-preview">这里是预览~</div></div></div>
<script type="text/javascript">
f = function() {
    if (typeof flask_pagedown_converter === "undefined")
        flask_pagedown_converter = Markdown.getSanitizingConverter().makeHtml;
    var textarea = document.getElementById("flask-pagedown-%(field)s");
    var preview = document.getElementById("flask-pagedown-%(field)s-preview");
    textarea.onkeyup = function() { preview.innerHTML = flask_pagedown_converter(textarea.value); }
    textarea.onkeyup.call(textarea);
}
if (document.readyState === 'complete')
    f();
else if (window.addEventListener)
    window.addEventListener("load", f, false);
else if (window.attachEvent)
    window.attachEvent("onload", f);
else
    f();
</script>
'''


class _pagedown(object):
    def include_pagedown(self):
        return Markup('''
<script type="text/javascript" src="/static/js/Markdown.Converter.js"></script>
<script type="text/javascript" src="/static/js/Markdown.Sanitizer.js"></script>
''')

    def html_head(self):
        return self.include_pagedown()


class PageDown(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['pagedown'] = _pagedown()
        app.context_processor(self.context_processor)

    @staticmethod
    def context_processor():
        return {'pagedown': current_app.extensions['pagedown']}


class PageDownWidget(TextArea):
    def __call__(self, field, **kwargs):
        show_input = True
        show_preview = True
        if 'only_input' in kwargs or 'only_preview' in kwargs:
            show_input = kwargs.pop('only_input', False)
            show_preview = kwargs.pop('only_preview', False)
        if not show_input and not show_preview:
            raise ValueError('One of show_input and show_preview must be true')
        html = ''
        if show_input:
            class_ = kwargs.pop('class', '').split() + \
                kwargs.pop('class_', '').split()
            class_ += ['flask-pagedown-input']
            html += pagedown_pre_html + super(PageDownWidget, self).__call__(
                field, id='flask-pagedown-' + field.name,
                class_=' '.join(class_), **kwargs) + pagedown_post_html
        if show_preview:
            html += preview_html % {'field': field.name}
        return HTMLString(html)

class PageDownField(TextAreaField):
    widget = PageDownWidget()
