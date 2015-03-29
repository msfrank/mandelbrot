import collections
import io
import pyparsing as pp

class Path(object):
    def __init__(self, segments):
        self.segments = segments
    def __str__(self):
        return '.'.join(self.segments)
    def __repr__(self):
        return str(self)
    def __cmp__(self, other):
        return self.segments == other.segments

Comment = collections.namedtuple('Comment',['value'])
ObjectDef = collections.namedtuple('ObjectDef', ['path'])
FieldDef = collections.namedtuple('FieldDef', ['name','value'])
ValueContinuation = collections.namedtuple('ValueContinuation', ['value'])
ListContinuation = collections.namedtuple('ListContinuation', ['value'])

comment = pp.Literal('#') + pp.restOfLine

pathsegment = pp.Word(pp.alphanums) ^ pp.quotedString
path = pp.ZeroOrMore(pathsegment + pp.Literal('.')) + pathsegment
objectdef = path + pp.Literal(':')

fieldkey = pp.Word(pp.alphanums) ^ pp.quotedString
fielddef = fieldkey + pp.Literal('=') + pp.restOfLine

valuecontinuation = pp.Literal('|') + pp.restOfLine
listcontinuation = pp.Literal(',') + pp.restOfLine

def comment_parse_action(tokens):
    return Comment(tokens[1])
comment.setParseAction(comment_parse_action)

def path_parse_action(tokens):
    return Path(list(filter(lambda x: x != '.', tokens)))
path.setParseAction(path_parse_action)

def objectdef_parse_action(tokens):
    return ObjectDef(tokens[0])
objectdef.setParseAction(objectdef_parse_action)

def fielddef_parse_action(tokens):
    return FieldDef(tokens[0], tokens[2])
fielddef.setParseAction(fielddef_parse_action)

def valuecontinuation_parse_action(tokens):
    return ValueContinuation(tokens[1])
valuecontinuation.setParseAction(valuecontinuation_parse_action)

def listcontinuation_parse_action(tokens):
    return ListContinuation(tokens[1])
listcontinuation.setParseAction(listcontinuation_parse_action)

Line = comment ^ objectdef ^ fielddef ^ valuecontinuation ^ listcontinuation

def line_parse_action(tokens):
    return None if len(tokens) == 0 else tokens[0]
Line.setParseAction(line_parse_action)

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
    results = Line.parseString(text, parseAll=True).asList()
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

def load(f):
    """
    :param f:
    :type f: file
    :return:
    """
    Frame = collections.namedtuple('Frame', ['linenum','indent','object','field'])
    root_object = {}
    frames = [Frame(None,None,root_object,None)]

    for linenum,indent,value in iter_lines(f):
        if isinstance(value, Comment):
            continue

        if isinstance(value, ObjectDef):
            frame = frames[0]

            # we are in the root frame
            if frame.indent is None:
                print("we are in root frame: frame.indent={0} indent={1}".format(frame.indent,indent))
                if value.path in frame.object:
                    raise KeyError("path {0} exists".format(value.path))
                curr_indent = indent
                frame.object[str(value.path)] = {}
                curr_object = frame.object[str(value.path)]
                curr_field = None

            #
            elif frame.indent < indent:
                print("specificity increases: frame.indent={0} indent={1}".format(frame.indent,indent))
                if value.path in frame.object:
                    raise KeyError("path {0} exists".format(value.path))
                curr_indent = indent
                frame.object[str(value.path)] = {}
                curr_object = frame.object[str(value.path)]
                curr_field = None

            else:
                if frame.indent != indent:
                    while frame.indent != indent:
                        frames.pop(0)
                        if len(frames) == 0:
                            raise Exception("no matching indent")
                        frame = frames[0]
                        print("specificy decreases: frame.indent={0} indent={1}".format(frame.indent,indent))
                else:
                    print("specificity is unchanged: frame.indent={0} indent={1}".format(frame.indent,indent))
                #
                if value.path in frame.object:
                    raise KeyError("path {0} exists".format(value.path))
                curr_indent = indent
                frame.object[str(value.path)] = {}
                curr_object = frame.object
                curr_field = None

            frames.insert(0, Frame(linenum, curr_indent, curr_object, curr_field))
            print("inserting object {0}: stack={1}".format(value.path, frames[0]))

        if isinstance(value, FieldDef):
            frame = frames[0]
            if frame.indent is None or frame.indent < indent:
                print("inserting field: {0} => {1}".format(value.name, value.value))
                frame.object[value.name] = value.value
            else:
                while frame.indent is not None and frame.indent >= indent:
                    if len(frames) == 0:
                        raise Exception("no parent indent")
                    frames.pop(0)
                    frame = frames[0]
                    print("specificy decreases: frame.indent={0} indent={1}".format(frame.indent,indent))
                print("inserting field: {0} => {1}".format(value.name, value.value))
                frame.object[value.name] = value.value

        if isinstance(value, ValueContinuation):
            pass

        if isinstance(value, ListContinuation):
            pass

    return root_object

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
