import json
import jinja2

class HTML:
    def __init__(self, blogname):
        with open("data/"+blogname+".json", 'r', encoding='utf8') as fp:
            self.data = json.load(fp)
            
    def saveHTML(self):
        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        templateFile = "templates/template.html"
        template = templateEnv.get_template(templateFile)
        outputText = template.render(data=self.data)
        with open("html/"+self.data["blogname"]+".html", "w", encoding="utf8") as fp:
            fp.write(outputText)
