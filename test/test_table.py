import bootstrap

import unittest
import unittest.mock

from mandelbrot.table import Table, Column, Output, Rowstore

class MockOutput(Output):
    def __init__(self, width):
        self.width = width
        self.lines = []
    def get_width(self):
        return self.width
    def write_line(self, line):
        self.lines.append(line)

class TestTable(unittest.TestCase):

    rows = [
        {
            'foo': 'hello, world',
            'bar': 'the meaning of life',
            'baz': 'now is the time for all good men to come to the aid of their country',
        },
        {
            'baz': 'now is the time for all good men to come to the aid of their country',
        },
    ]

    def test_render_cell_single_span_left_justify(self):
        "A Table should render a cell with a single span left justified"
        table = Table()
        column = Column("Foo", 'foo')
        table.append_column(column)
        spans = table.render_cell(self.rows[0]['foo'], column, column_width=20)
        self.assertListEqual(spans, [
            'hello, world        ',
            ])

    def test_render_cell_single_span_right_justify(self):
        "A Table should render a cell with a single span right justified"
        table = Table()
        column = Column("Foo", 'foo', justify_left=False)
        table.append_column(column)
        spans = table.render_cell(self.rows[0]['foo'], column, column_width=20)
        self.assertListEqual(spans, [
            '        hello, world',
            ])

    def test_render_cell_multiple_span_left_justify(self):
        "A Table should render a cell with multiple spans left justified"
        table = Table()
        column = Column("Baz", 'baz')
        table.append_column(column)
        spans = table.render_cell(self.rows[1]['baz'], column, column_width=20)
        self.assertListEqual(spans, [
            'now is the time for ',
            'all good men to come',
            'to the aid of their ',
            'country             ',
            ])

    def test_render_cell_multiple_span_right_justify(self):
        "A Table should render a cell with multiple spans right justified"
        table = Table()
        column = Column("Baz", 'baz', justify_left=False)
        table.append_column(column)
        spans = table.render_cell(self.rows[1]['baz'], column, column_width=20)
        self.assertListEqual(spans, [
            ' now is the time for',
            'all good men to come',
            ' to the aid of their',
            '             country',
            ])

    def test_render_cell_no_word_wrap_left_justify(self):
        "A Table should render a cell with word-wrapping disabled left justified"
        table = Table()
        column = Column("Baz", 'baz', wrap_words=False)
        table.append_column(column)
        spans = table.render_cell(self.rows[1]['baz'], column, column_width=20)
        self.assertListEqual(spans, [
            'now is the time for ',
            ])

    def test_render_cell_no_word_wrap_right_justify(self):
        "A Table should render a cell with word-wrapping disabled right justified"
        table = Table()
        column = Column("Baz", 'baz', justify_left=False, wrap_words=False)
        table.append_column(column)
        spans = table.render_cell(self.rows[1]['baz'], column, column_width=20)
        self.assertListEqual(spans, [
            'aid of their country',
            ])

    def test_render_row_left_justify(self):
        "A Table should render a row with word-wrapping left justified"
        table = Table()
        column1 = Column("Foo", 'foo')
        table.append_column(column1)
        column2 = Column("Bar", 'bar')
        table.append_column(column2)
        column3 = Column("Baz", 'baz')
        table.append_column(column3)
        spans = list(table.render_row(self.rows[0], column_widths=[20,20,20]))
        self.assertListEqual(spans, [
            'hello, world         the meaning of life  now is the time for ',
            '                                          all good men to come',
            '                                          to the aid of their ',
            '                                          country             ',
            ])

    def test_render_row_right_justify(self):
        "A Table should render a row with word-wrapping right justified"
        table = Table()
        column1 = Column("Foo", 'foo', justify_left=False)
        table.append_column(column1)
        column2 = Column("Bar", 'bar', justify_left=False)
        table.append_column(column2)
        column3 = Column("Baz", 'baz', justify_left=False)
        table.append_column(column3)
        spans = list(table.render_row(self.rows[0], column_widths=[20,20,20]))
        self.assertListEqual(spans, [
            '        hello, world  the meaning of life  now is the time for',
            '                                          all good men to come',
            '                                           to the aid of their',
            '                                                       country',
            ])

    def test_render_row_no_word_wrap_left_justify(self):
        "A Table should render a row with word-wrapping disabled left justified"
        table = Table()
        column1 = Column("Foo", 'foo', wrap_words=False)
        table.append_column(column1)
        column2 = Column("Bar", 'bar', wrap_words=False)
        table.append_column(column2)
        column3 = Column("Baz", 'baz', wrap_words=False)
        table.append_column(column3)
        spans = list(table.render_row(self.rows[0], column_widths=[20,20,20]))
        self.assertListEqual(spans, [
            'hello, world         the meaning of life  now is the time for ',
            ])

    def test_render_row_no_word_wrap_right_justify(self):
        "A Table should render a row with word-wrapping disabled right justified"
        table = Table()
        column1 = Column("Foo", 'foo', justify_left=False, wrap_words=False)
        table.append_column(column1)
        column2 = Column("Bar", 'bar', justify_left=False, wrap_words=False)
        table.append_column(column2)
        column3 = Column("Baz", 'baz', justify_left=False, wrap_words=False)
        table.append_column(column3)
        spans = list(table.render_row(self.rows[0], column_widths=[20,20,20]))
        self.assertListEqual(spans, [
            '        hello, world  the meaning of life aid of their country',
            ])
 
    def test_render_table_from_rowstore_with_headings(self):
        "A Table should render a Rowstore with headings"
        table = Table()
        column1 = Column("Foo", 'foo', minimum_width=20, expand=False)
        table.append_column(column1)
        column2 = Column("Bar", 'bar', minimum_width=20, expand=False)
        table.append_column(column2)
        column3 = Column("Baz", 'baz', minimum_width=20, expand=False)
        table.append_column(column3)
        rowstore = Rowstore()
        rowstore.append_row(self.rows[0])
        output = MockOutput(60)
        table.print_table(rowstore, output)
        self.assertListEqual(output.lines, [
            'Foo                  Bar                  Baz                 ',
            '-------------------- -------------------- --------------------',
            'hello, world         the meaning of life  now is the time for ',
            '                                          all good men to come',
            '                                          to the aid of their ',
            '                                          country             ',
            ])
 
    def test_render_table_from_rowstore_without_headings(self):
        "A Table should render a Rowstore without headings"
        table = Table(display_headings=False)
        column1 = Column("Foo", 'foo', minimum_width=20, expand=False)
        table.append_column(column1)
        column2 = Column("Bar", 'bar', minimum_width=20, expand=False)
        table.append_column(column2)
        column3 = Column("Baz", 'baz', minimum_width=20, expand=False)
        table.append_column(column3)
        rowstore = Rowstore()
        rowstore.append_row(self.rows[0])
        output = MockOutput(60)
        table.print_table(rowstore, output)
        self.assertListEqual(output.lines, [
            'hello, world         the meaning of life  now is the time for ',
            '                                          all good men to come',
            '                                          to the aid of their ',
            '                                          country             ',
            ])

