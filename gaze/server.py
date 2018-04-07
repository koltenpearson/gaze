import cherrypy
import pkgutil
from .build import PageTemplate, HTMLComponent
from pathlib import Path
import pygments
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename, guess_lexer

#########################################################################
## server


class Gaze :

    def __init__(self, root_dir) :
        self.debug=True

        self.root_dir = Path(root_dir)

        self.template = PageTemplate()
        self.template.add_title("Gaze")
        self.template.link_style('/style.css')
        self.template.link_script('/script.js')

        self.style = pkgutil.get_data(__name__, 'style.css').decode('ascii')
        self.script = pkgutil.get_data(__name__, 'script.js').decode('ascii')

        self.formatter = HtmlFormatter(linenos=True, style='solarizeddark')
        self.template.add_style(self.formatter.get_style_defs('.highlight'))


    @cherrypy.expose
    def script_js(self) :
        cherrypy.response.headers['Content-Type'] = 'text/javascript'
        if self.debug :
            return  pkgutil.get_data(__name__, 'script.js').decode('ascii')
        return self.script

    @cherrypy.expose
    def style_css(self) :
        cherrypy.response.headers['Content-Type'] = 'text/css'
        if self.debug :
            return  pkgutil.get_data(__name__, 'style.css').decode('ascii')
        return self.style



    @cherrypy.expose
    def default(self, *pathargs) :
        print(pathargs)
        current_path = Path(self.root_dir, *pathargs)
        if current_path.is_dir() :
            return self.render_path(current_path)
        else :
            return self.render_file(current_path)

    def render_path(self, path) :
        filelist = []
        pathlist = []
        for d in path.iterdir() :
            if d.is_dir() :
                pathlist.append(d)
            else :
                filelist.append(d)

        filelist.sort()
        pathlist.sort()

        result = HTMLComponent('body', _class='path-content')
        result.append(self.render_header(path))

        path_nav = result.child('div', _class='path-list')
        for p in pathlist :
            cont = path_nav.child('div', _class='path-container')
            link = cont.child('a')
            link['href'] = '/'+str(p.relative_to(self.root_dir))
            link.append(p.parts[-1] + '/')

        file_nav = result.child('div', _class="file-list")

        for f in filelist :
            cont = file_nav.child('div', _class='file-container')
            link = cont.child('a')
            link['href'] = '/'+str(f.relative_to(self.root_dir))
            link.append(f.parts[-1])

        self.template.set_title(f'Gaze - {path.parts[-1]}')
        return self.template.render(result)

    def render_file(self, filepath) :

        with open(filepath) as infile :
            contents = infile.read()

        filename = filepath.parts[-1]

        try :
            lexer = get_lexer_for_filename(filename)

        except pygments.util.ClassNotFound :

            lexer = guess_lexer(contents)

        processed_contents = highlight(contents, lexer, self.formatter)

        result = HTMLComponent('body', _class='file-viewer')
        result.append(self.render_header(filepath))

        source_view = result.child('div', _class='source-view')
        source_view.append(processed_contents)

        self.template.set_title(f'Gaze - {filename}')
        return self.template.render(result)


    def render_header(self, path) :
        header = HTMLComponent('div', _class='nav-header')
        path_parts = path.relative_to(self.root_dir).parts
        part_link = header.child('a')
        part_link.append('/')
        part_link['href'] = '/'

        if path.is_file() :
            filename = path_parts[-1]
            path_parts = path_parts[:-1]

        for i in range(len(path_parts)) :
            part_link = header.child('a')
            part_link.append(path_parts[i]+'/')
            part_link['href'] = '/' + '/'.join(path_parts[:i+1])

        if path.is_file() :
            header.append(filename)

        return header

def run_server(root_dir, port) :
    cherrypy.config.update({
        'server.socket_port' : port,
    })

    # server.route = object() creates a sub server of sorts

    cherrypy.tree.mount(Gaze(root_dir), '/')

    cherrypy.engine.start()
    cherrypy.engine.block()



