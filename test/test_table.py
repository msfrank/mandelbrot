import bootstrap

import unittest
import unittest.mock

from mandelbrot.table import Table, Column, Output, Rowstore

class TestTable(unittest.TestCase):

    rows = [
        {'foo': 'hello, world', 'bar': 'the meaning of life', 'baz': 'spooky action at a distance'},
        {'baz': 'now is the time for all good men to come to the aid of their country'},
        ]

    def test_render_cell_single_span_left_justify(self):
        "A Table should render a cell with a single span left justified"
        rowstore = Rowstore()
        rowstore.append_row(self.rows[0])
        table = Table()
        column = Column("Foo", 'foo')
        table.append_column(column)
        spans = table.render_cell(self.rows[0]['foo'], column, column_width=20)
        self.assertListEqual(spans, [
            'hello, world        ',
            ])

    def test_render_cell_single_span_right_justify(self):
        "A Table should render a cell with a single span right justified"
        rowstore = Rowstore()
        rowstore.append_row(self.rows[0])
        table = Table()
        column = Column("Foo", 'foo', justify_left=False)
        table.append_column(column)
        spans = table.render_cell(self.rows[0]['foo'], column, column_width=20)
        self.assertListEqual(spans, [
            '        hello, world',
            ])

    def test_render_cell_multiple_span_left_justify(self):
        "A Table should render a cell with multiple spans left justified"
        rowstore = Rowstore()
        rowstore.append_row(self.rows[0])
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
        rowstore = Rowstore()
        rowstore.append_row(self.rows[0])
        table = Table()
        column = Column("Foo", 'foo', justify_left=False)
        table.append_column(column)
        spans = table.render_cell(self.rows[1]['baz'], column, column_width=20)
        self.assertListEqual(spans, [
            ' now is the time for',
            'all good men to come',
            ' to the aid of their',
            '             country',
            ])

#    def test_render_table(self):
#        "A Table should render a Rowstore"
#        table = Table()
#        table.append_column(Column("Foo", 'foo'))
#        table.append_column(Column("Bar", 'bar'))
#        table.append_column(Column("Baz", 'baz'))
#        rowstore = Rowstore()
#        rowstore.append_row({'foo': 'hello, world', 'bar': 'the meaning of life', 'baz': 'spooky action at a distance'})
#        output = Output()
#        output.get_width = unittest.mock
#        table.render_table(rowstore)
