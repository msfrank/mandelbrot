import sys
import itertools
import shutil

class Column(object):
    """
    """
    def __init__(self, name, field, minimum_width=None, justify_left=True, expand=False, wrap_words=True, normalize=True):
        self.name = name
        self.field = field
        self.minimum_width = minimum_width
        self.justify_left = justify_left
        self.expand = expand
        self.wrap_words = wrap_words
        self.normalize = normalize

    def render_value(self, value):
        if value is None:
            return None
        if self.normalize:
            return ' '.join(str(value).split())
        return str(value)

class ColumnStats(object):
    def __init__(self, smallest_cell=0, largest_cell=0, smallest_cell_word=0):
        self.smallest_cell = smallest_cell
        self.largest_cell = largest_cell
        self.smallest_cell_word = smallest_cell_word

class Rowstore(object):
    """
    """
    def __init__(self):
        self.rows = []

    def append_row(self, row):
        """
        :param row:
        :type row: dict[str,str]
        """
        self.rows.append(row)

    def __iter__(self):
        return iter(self.rows)

class Output(object):
    def get_width(self):
        raise NotImplementedError()
    def write_line(self, line):
        raise NotImplementedError()

class Terminal(Output):
    """
    """
    def __init__(self, f=sys.stdout):
        self.f = f
        columns,lines = shutil.get_terminal_size()
        self.width = columns
        self.height = lines

    def get_width(self):
        return self.width

    def write_line(self, line):
        """
        """
        if len(line) > self.width:
            line = line[0:self.width]
        self.f.write(line + '\n')

class Table(object):
    """
    """
    def __init__(self, display_headings=True):
        self.display_headings = display_headings
        self.columns = []

    def append_column(self, column):
        """
        :param column:
        :type column: Column
        """
        self.columns.append(column)

    def print_table(self, rowstore, output):
        """
        """
        # the current width of the terminal
        output_width = output.get_width()
        for line in self.render_table(rowstore, output_width):
            output.write_line(line)

    def calculate_column_stats(self, rowstore):
        """
        :param rowstore:
        :return:
        """
        columns = {column.field:column for column in self.columns}
        column_stats = {field:ColumnStats() for field in columns.keys()}

        for row in rowstore:
            for field,value in row.items():
                try:
                    column = columns[field]
                    stats = column_stats[field]

                    # possibly convert and normalize each field value
                    if column.normalize:
                        words = str(value).split()
                        normalized_value = ' '.join(words)
                    else:
                        normalized_value = str(value)
                        words = [normalized_value]

                    # update column stats
                    num_chars = len(normalized_value)
                    smallest_word = min(map(lambda word: len(word), words))
                    if stats.smallest_cell == 0 or num_chars < stats.smallest_cell:
                        stats.smallest_cell = num_chars
                    if stats.largest_cell == 0 or num_chars > stats.largest_cell:
                        stats.largest_cell = num_chars
                    if stats.smallest_cell_word == 0 or smallest_word < stats.smallest_cell_word:
                        stats.smallest_cell_word = smallest_word

                except KeyError:
                    pass
        return column_stats

    def render_table(self, rowstore, output_width):
        """
        :param rowstore:
        :type rowstore: Rowstore
        :param output_width:
        :type output_width: int
        :return: A generator yielding each line of the rendered table
        :rtype: generator
        """

        column_stats = self.calculate_column_stats(rowstore)

        # the total width of all single-space separators between columns
        heading_separators_width = 0 if not self.columns else len(self.columns) - 1

        column_widths = []
        for column in self.columns:

            # the width of the column heading, or 0 if we aren't displaying headings
            column_width = 0 if not self.display_headings else len(column.name)

            stats = column_stats.get(column.field, ColumnStats(0, 0, 0))

            # the minimum number of chars to display at least one word of each cell
            if stats.smallest_cell_word > column_width:
                column_width = stats.smallest_cell_word

            # if a minimum width is explicitly specified for the column, then use it
            if column.minimum_width is not None and column.minimum_width > column_width:
                column_width = column.minimum_width

            column_widths.append(column_width)

        # the minimum chars needed to reasonably display the table
        minimum_width = sum(column_widths) + heading_separators_width

        # if we have more than the minimum space, then divide up the extra amount
        # evenly between all columns which have expand set to True
        if minimum_width < output_width:
            expand_columns = [i for i in range(len(self.columns)) if self.columns[i].expand]
            if expand_columns:
                total_extra_space = output_width - minimum_width
                for i in itertools.cycle(expand_columns):
                    if total_extra_space == 0:
                        break
                    column_widths[i] += 1
                    total_extra_space -= 1

        # if headings are displayed, then render the heading and a separator
        if self.display_headings:
            row = {column.field:column.name for column in self.columns}
            yield from self.render_row(row, column_widths)
            row = {self.columns[i].field:'-' * column_widths[i] for i in range(len(self.columns))}
            yield from self.render_row(row, column_widths)

        # render each row in the rowstore
        columns = {column.field:column for column in self.columns}
        for row in rowstore:
            row = {field:columns[field].render_value(value) for field, value in row.items() if field in columns}
            yield from self.render_row(row, column_widths)

    def render_row(self, row, column_widths):
        """
        :param row:
        :type row: dict[str,str]
        :param column_widths:
        :type column_widths: list[int]
        :rtype: generator
        """
        rendered_cells = []
        for i in range(len(self.columns)):
            column = self.columns[i]
            cell = row.get(column.field)
            rendered_cells.append(self.render_cell(cell, column, column_widths[i]))
        max_height = max(map(lambda x: len(x), rendered_cells))

        #
        for i in range(len(rendered_cells)):
            cell = rendered_cells[i]
            for _ in range(max_height - len(cell)):
                cell += self.render_cell(None, self.columns[i], column_widths[i])
        #
        for i in range(max_height):
            yield ' '.join([cell[i] for cell in rendered_cells])

    def render_cell(self, cell, column, column_width):
        """
        :param cell: the cell value, or None to render an empty cell
        :type cell: str or None
        :param column:
        :type column: Column
        :param column_width:
        :type column_width: int
        :return:
        """
        if cell is None:
            return [' ' * column_width]

        # if word wrapping is disabled, then render the cell as a single line
        # and truncate it if it exceeds the column width
        if column.wrap_words is False:
            return [self.render_span([cell], column_width, column.justify_left)]

        # render the cell with word wrapping enabled, using a greedy algorithm
        spans = []
        current_span = []
        for word in cell.split():
            proposed_length = len(' '.join(current_span + [word]))
            if proposed_length <= column_width:
                current_span.append(word)
            else:
                word_length = len(word)
                if word_length <= column_width:
                    spans.append(self.render_span(current_span, column_width, column.justify_left))
                    current_span = [word]
                else:
                    span_length = len(' '.join(current_span))
                    parts = self.split_word_at_width(word, column_width, column_width - span_length - 1)
                    current_span.append(parts.pop(0))
                    spans.append(self.render_span(current_span, column_width, column.justify_left))
                    for part in parts:
                        if len(part) == column_width:
                            spans.append(part)
                        else:
                            current_span = [part]
        spans.append(self.render_span(current_span, column_width, column.justify_left))
        return spans

    def render_span(self, words, width, justify_left):
        """
        :param words:
        :param width:
        :param justify_left:
        :return:
        """
        span = ' '.join(words)
        if justify_left:
            return span.ljust(width)[0:width]
        span = span.rjust(width)
        if len(span) > width:
            return span[len(span)-width:]
        return span

    def split_word_at_width(self, word, width, initial=None):
        """
        :param word:
        :param width:
        :param initial:
        :return:
        """
        parts = []
        if initial:
            parts.append(word[0:initial])
            word = word[initial:-1]
        while word:
            parts.append(word[0:width])
            word = word[width:-1]
        return parts
