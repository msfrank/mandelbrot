import collections
import io
import pyparsing as pp

class Path(object):
    def __init__(self, segments):
        self.segments = segments
    def __str__(self):
        return '.'.join(self.segments) if len(self.segments) > 0 else '.'
    def __repr__(self):
        return str(self)
    def __eq__(self, other):
        return self.segments == other.segments
    def __hash__(self):
        return hash(str(self))
    def __iter__(self):
        return iter(self.segments)
    def __add__(self, other):
        if isinstance(other, Path):
            return Path(self.segments + other.segments)
        elif isinstance(other, list):
            return Path(self.segments + other)
        elif isinstance(other, str):
            return Path(self.segments + [other])
        else:
            raise ValueError("can't concatenate Path with {0}".format(type(other)))

Comment = collections.namedtuple('Comment',['value'])
ObjectDef = collections.namedtuple('ObjectDef', ['path'])
FieldDef = collections.namedtuple('FieldDef', ['field_name','field_value'])
ValueContinuation = collections.namedtuple('ValueContinuation', ['value_continuation'])
ListContinuation = collections.namedtuple('ListContinuation', ['list_continuation'])

comment_parser = pp.Literal('#') + pp.restOfLine

pathsegment_parser = pp.Word(pp.alphanums) ^ pp.quotedString
path_parser = pp.ZeroOrMore(pathsegment_parser + pp.Literal('.')) + pathsegment_parser
objectdef_parser = path_parser + pp.Literal(':')

fieldkey_parser = pp.Word(pp.alphanums) ^ pp.quotedString
fielddef_parser = fieldkey_parser + pp.Literal('=') + pp.restOfLine

valuecontinuation_parser = pp.Literal('|') + pp.restOfLine
listcontinuation_parser = pp.Literal(',') + pp.restOfLine

def comment_parse_action(tokens):
    return Comment(tokens[1])
comment_parser.setParseAction(comment_parse_action)

def path_parse_action(tokens):
    return Path(list(filter(lambda x: x != '.', tokens)))
path_parser.setParseAction(path_parse_action)

def objectdef_parse_action(tokens):
    return ObjectDef(tokens[0])
objectdef_parser.setParseAction(objectdef_parse_action)

def fielddef_parse_action(tokens):
    return FieldDef(tokens[0], tokens[2])
fielddef_parser.setParseAction(fielddef_parse_action)

def valuecontinuation_parse_action(tokens):
    return ValueContinuation(tokens[1])
valuecontinuation_parser.setParseAction(valuecontinuation_parse_action)

def listcontinuation_parse_action(tokens):
    return ListContinuation(tokens[1])
listcontinuation_parser.setParseAction(listcontinuation_parse_action)

line_parser = comment_parser ^ objectdef_parser ^ fielddef_parser ^ valuecontinuation_parser ^ listcontinuation_parser

def line_parse_action(tokens):
    return None if len(tokens) == 0 else tokens[0]
line_parser.setParseAction(line_parse_action)

def calculate_indent(text):
    """
    :param text:
    :type text: str
    :return:
    """
    indent = 0
    for c in text:
        if c is '\t':
            raise ValueError()
        if c is not ' ':
            return indent,text[indent:]
        indent += 1
    return indent,''

def parse_line(text):
    """
    :param text:
    :type text: str
    :return:
    """
    indent,text = calculate_indent(text)
    results = line_parser.parseString(text, parseAll=True).asList()
    return indent,results[0]

def iter_lines(f):
    """
    :param f:
    :type f: file
    :return:
    """
    linenum = 1
    for text in f.readlines():
        # ignore lines that consist entirely of whitespace
        if text.isspace():
            continue
        indent,value = parse_line(text)
        yield linenum,indent,value
        linenum += 1

class Frame(object):
    def __init__(self, linenum, indent):
        self.linenum = linenum
        self.indent = indent
    def __repr__(self):
        return str(self)

class ContainerFrame(Frame):
    def __init__(self, linenum, indent, path, container):
        super().__init__(linenum, indent)
        self.path = path
        self.container = container
    def __str__(self):
        return "ContainerFrame(linenum={0}, indent={1}, path={2})".format(self.linenum,self.indent,self.path)

class RootFrame(ContainerFrame):
    def __init__(self, root):
        super().__init__(None, None, Path([]), root)
    def __str__(self):
        return "RootFrame()"

class FieldFrame(Frame):
    def __init__(self, linenum, indent, container_path, field_name, field_value):
        super().__init__(linenum, indent)
        self.container_path = container_path
        self.field_name = field_name
        self.field_value = field_value
    def __str__(self):
        return "FieldFrame(linenum={0}, indent={1}, container_path={2}, field_name={3})".format(
            self.linenum,self.indent,self.container_path,self.field_name)

class ValueContinuationFrame(Frame):
    def __init__(self, linenum, indent, container_path, field_name):
        super().__init__(linenum, indent)
        self.container_path = container_path
        self.field_name = field_name

class Parser(object):
    """
    """
    def __init__(self):
        self.root = {}
        self.root_frame = RootFrame(self.root)
        self.frames = [self.root_frame]

    def current_frame(self):
        return self.frames[0]

    def current_indent(self):
        return self.frames[0].indent

    def push_frame(self, frame):
        self.frames.insert(0, frame)

    def pop_frame(self):
        self.frames.pop(0)
        if len(self.frames) == 0:
            raise Exception("stack is exhausted")
        return self.frames[0]

    def append_child_object(self, linenum, indent, path):
        frame = self.current_frame()
        assert isinstance(frame,RootFrame) or isinstance(frame,ContainerFrame) and frame.indent < indent
        assert len(path.segments) > 0
        # create intermediate paths if necessary
        container = frame.container
        for segment in path.segments[0:-1]:
            if not segment in container:
                container[segment] = {}
                container = container[segment]
        container_name = path.segments[-1]
        if container_name in frame.container:
            raise KeyError("container exists at path {0}".format(path))
        container[container_name] = {}
        container = container[container_name]
        path = frame.path + path
        frame = ContainerFrame(linenum, indent, path, container)
        self.push_frame(frame)
        print("created container for path {0}".format(path))

    def append_sibling_object(self, linenum, indent, path):
        frame = self.current_frame()
        assert frame.indent is not None and frame.indent == indent
        self.pop_frame()
        self.append_child_object(linenum, indent, path)

    def append_parent_object(self, linenum, indent, path):
        frame = self.current_frame()
        assert frame.indent is not None and frame.indent > indent
        while frame.indent != indent:
            frame = self.pop_frame()
        self.append_sibling_object(linenum, indent, path)

    def append_child_field(self, linenum, indent, field_name, field_value):
        frame = self.current_frame()
        assert isinstance(frame,RootFrame) or isinstance(frame,ContainerFrame) and frame.indent < indent
        if field_name in frame.container:
            raise KeyError("field {0} exists in container at path {1}".format(field_name, frame.path))
        frame.container[field_name] = field_value
        frame = FieldFrame(linenum, indent, frame.path, field_name, field_value)
        self.push_frame(frame)
        print("created field {0} in container at path {1}".format(field_name, frame.container_path))

    def append_sibling_field(self, linenum, indent, field_name, field_value):
        frame = self.current_frame()
        assert frame.indent is not None and frame.indent == indent
        self.pop_frame()
        self.append_child_field(linenum, indent, field_name, field_value)

    def append_parent_field(self, linenum, indent, field_name, field_value):
        frame = self.current_frame()
        assert frame.indent is not None and frame.indent > indent
        while frame.indent != indent:
            frame = self.pop_frame()
        self.append_sibling_field(linenum, indent, field_name, field_value)

def load(f):
    """
    :param f:
    :type f: file
    :return:
    """
    parser = Parser()

    for linenum,indent,value in iter_lines(f):

        print("root is {0}".format(parser.root))
        print("stack is {0}".format(parser.frames))

        if isinstance(value, Comment):
            continue

        current_indent = parser.current_indent()

        if isinstance(value, ObjectDef):
            # object is a child of the root
            if current_indent is None:
                parser.append_child_object(linenum, indent, value.path)
            # object is a child of the current object
            elif current_indent < indent:
                parser.append_child_object(linenum, indent, value.path)
            # object is a sibling of the current object
            elif current_indent == indent:
                parser.append_sibling_object(linenum, indent, value.path)
            # object is a parent of the current object
            else:
                parser.append_parent_object(linenum, indent, value.path)

        if isinstance(value, FieldDef):
            if current_indent is None:
                parser.append_child_field(linenum, indent, value.field_name, value.field_value)
            elif current_indent < indent:
                parser.append_child_field(linenum, indent, value.field_name, value.field_value)
            elif current_indent == indent:
                parser.append_sibling_field(linenum, indent, value.field_name, value.field_value)
            else:
                parser.append_parent_field(linenum, indent, value.field_name, value.field_value)

        if isinstance(value, ValueContinuation):
            pass

        if isinstance(value, ListContinuation):
            pass

    return parser.root

def loads(s):
    """
    :param s:
    :type s: str
    :return:
    """
    return load(io.StringIO(s))

def debug(f):
    for linenum,indent,value in iter_lines(f):
        print("{0}{1}|{2}".format(str(linenum).rjust(3), ' ' * indent, value))

def debugs(s):
    debug(io.StringIO(s))
