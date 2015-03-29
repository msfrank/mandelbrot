import bootstrap

import unittest

import mandelbrot.mcon

class TestMCON(unittest.TestCase):

    single_line_data = "foo = bar"

    multi_line_data = \
"""
field1 = value1
field2 = value2
object1:
    field3 = value3
    object2:
        field4 = value4
        object3:
            field5 = value5
    field6 = value6
    object4:
        field7 = value7
field8 = value8
object5:
        field9 = value9
"""

    deep_path_data = \
"""
toplevel:
    this.is.deep:
        field1 = value1
    shallow:
        field2 = value2
"""

    def test_parse_comment_line(self):
        indent,result = mandelbrot.mcon.parse_line("# this is a comment")
        self.assertIsInstance(result, mandelbrot.mcon.Comment)
        result_fields = vars(result)
        other_fields = vars(mandelbrot.mcon.Comment(" this is a comment"))
        self.assertDictEqual(result_fields, other_fields)

    def test_parse_objectdef_line(self):
        indent,result = mandelbrot.mcon.parse_line("object:")
        self.assertIsInstance(result, mandelbrot.mcon.ObjectDef)
        result_fields = vars(result)
        other_fields = vars(mandelbrot.mcon.ObjectDef(mandelbrot.mcon.Path(['object'])))
        self.assertDictEqual(result_fields, other_fields)

    def test_parse_deep_objectdef_line(self):
        indent,result = mandelbrot.mcon.parse_line("deep.nested.object:")
        self.assertIsInstance(result, mandelbrot.mcon.ObjectDef)
        result_fields = vars(result)
        other_fields = vars(mandelbrot.mcon.ObjectDef(mandelbrot.mcon.Path(['deep','nested','object'])))
        self.assertDictEqual(result_fields, other_fields)

    def test_parse_fielddef_line(self):
        indent,result = mandelbrot.mcon.parse_line("foo = bar")
        self.assertIsInstance(result, mandelbrot.mcon.FieldDef)
        result_fields = vars(result)
        other_fields = vars(mandelbrot.mcon.FieldDef('foo', ' bar'))
        self.assertDictEqual(result_fields, other_fields)

    def test_parse_valuecontinuation_line(self):
        indent,result = mandelbrot.mcon.parse_line("| this is a continuation")
        self.assertIsInstance(result, mandelbrot.mcon.ValueContinuation)
        result_fields = vars(result)
        other_fields = vars(mandelbrot.mcon.ValueContinuation(' this is a continuation'))
        self.assertDictEqual(result_fields, other_fields)

    def test_parse_listcontinuation_line(self):
        indent,result = mandelbrot.mcon.parse_line(", this is a continuation")
        self.assertIsInstance(result, mandelbrot.mcon.ListContinuation)
        result_fields = vars(result)
        other_fields = vars(mandelbrot.mcon.ListContinuation(' this is a continuation'))
        self.assertDictEqual(result_fields, other_fields)

    def test_mcon_load_multi_line(self):
        mandelbrot.mcon.debugs(self.multi_line_data)
        root = mandelbrot.mcon.loads(self.multi_line_data)
        print(root)
        self.assertEquals(root['field1'], ' value1')
        self.assertEquals(root['field2'], ' value2')
        self.assertEquals(root['object1']['field3'], ' value3')
        self.assertEquals(root['object1']['field6'], ' value6')
        self.assertEquals(root['object1']['object2']['field4'], ' value4')
        self.assertEquals(root['object1']['object2']['object3']['field5'], ' value5')
        self.assertEquals(root['object1']['object4']['field7'], ' value7')
        self.assertEquals(root['field8'], ' value8')
        self.assertEquals(root['object5']['field9'], ' value9')

    def test_mcon_load_deep_path(self):
        mandelbrot.mcon.debugs(self.deep_path_data)
        root = mandelbrot.mcon.loads(self.deep_path_data)
        print(root)
        self.assertEquals(root['toplevel']['this']['is']['deep']['field1'], ' value1')
        self.assertEquals(root['toplevel']['shallow']['field2'], ' value2')
