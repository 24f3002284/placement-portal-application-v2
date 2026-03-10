from jinja2 import Template

def render_email_template(username, applications, file_path):
    with open(file_path, "r") as file:   # fixed: was open("file_path") - string literal bug
        t = Template(file.read())
        return t.render(username=username, applications=applications)