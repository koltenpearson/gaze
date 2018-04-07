
#helper class for building html pages
class PageTemplate :

    def __init__(self) :
        self.head = HTMLComponent('head')

    def render(self, body) :
        result = HTMLComponent('html')
        result.append(self.head)
        result.append(body)
        return result.to_text().encode('utf-16', 'replace').decode('utf-16')

    def add_title(self, title) :
        self.title_node = self.head.child('title')
        self.title_node.append(title)

    def set_title(self, title) :
        self.title_node.content[0] = title

    def add_style(self, style_text) :
        style_node = self.head.child('style')
        style_node.append(style_text)

    def link_style(self, style_path) :
        style_node = self.head.child('link')
        style_node['rel'] = 'stylesheet'
        style_node['type'] = 'text/css'
        style_node['href'] = style_path
    
    def link_script(self, script_path) :
        script_node = self.head.child('script')
        script_node['type'] = 'text/javascript'
        script_node['src'] = script_path
        script_node['defer'] = None

class HTMLComponent :

    def __init__(self, tag, _id=None, _class=None, **attrs) :
        self.tag = tag
        self.attributes = {}
        self.content = []
        if _id is not None :
            self.attributes['id'] = _id
        if _class is not None :
            self.attributes['class'] = _class
        for key,value in attrs.items() :
            self.attributes[key] = value

    def __getitem__(self, key) :
        return self.attributes[key]

    def __setitem__(self, key, value) :
        self.attributes[key] = value

    def child(self, tag, _id=None, _class=None, **attrs) :
        result = HTMLComponent(tag, _id=_id, _class=_class, **attrs)
        self.content.append(result)
        return result

    def append(self, component) :
        self.content.append(component)

    def format_tag(self) :
        result = f'<{self.tag} '
        for key, value in self.attributes.items() :
            result += f'{key}'
            if value is not None :
                result += f"={value}"
            result += ' '
        result = result[:-1]
        result += '>'
        return result

    def to_text(self) :
        result = self.format_tag()

        for c in self.content :
            try :
                result += c.to_text()
            except AttributeError :
                result += c

        result += f'</{self.tag}>'

        return result


class JSONComponent :

    def __init__(self) :
        self._content = {}
        self._content_list = None

    def __getattr__(self, name) :
        if name not in self._content :
            self._content[name] = JSONComponent()

        return self._content[name]

    def __setattr__(self, name, value) :
        if name[0] == '_' :
            object.__setattr__(self, name, value)
            return

        self._content[name] = value

    def next(self) :
        if self._content_list is None :
            self._content_list = []
        child = JSONComponent()
        child._content = self._content
        self._content_list.append(child)
        self._content = {}

    def to_json_dict(self) :
        result = {}
        for key,value in self._content.items() :
            try :
                result[key] = value.to_json_dict()
            except AttributeError:
                result[key] = value

        if self._content_list is not None :
            final_result = result
            result = []
            for c in self._content_list :
                try :
                    result.append(c.to_json_dict())
                except AttributeError :
                    result.append(c)
            if len(final_result) > 0 :
                result.append(final_result)

        return result



