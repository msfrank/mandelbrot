# Copyright 2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Mandelbrot.
#
# Mandelbrot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Mandelbrot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Mandelbrot.  If not, see <http://www.gnu.org/licenses/>.

import os, tempfile, subprocess

class EditorException(Exception):
   pass

class NoEditorAvailable(EditorException):
    def __str__(self):
        return "no editor specified, and neither VISUAL nor EDITOR are set"

class EditorFailed(EditorException):
   def __init__(self, exitstatus, stdout, stderr):
       self.exitstatus = exitstatus
       self.stdout = stdout
       self.stderr = stderr
   def __str__(self):
       return "editor command failed with exit status %i" % self.exitstatus

def run_editor(editor=None, tmpdir=None, content=None):
    """
    Read input from the user by spawning an editor (optionally pre-filled
    with content) and reading the saved content from a tmpfile.  Returns
    the content entered by the user as a string, otherwise None if the user
    did not enter any content.
    """
    # determine the editor to use
    if editor is None:
        if 'VISUAL' in os.environ:
            editor = os.environ['VISUAL']
        elif 'EDITOR' in os.environ:
            editor = os.environ['EDITOR']
        else:
            raise NoEditorAvailable()
    # safely create a tempfile in tmpdir
    if tmpdir is not None:
        fd,tmpfile = tempfile.mkstemp(prefix='repair.', dir=tmpdir)
    else:
        fd,tmpfile = tempfile.mkstemp(prefix='repair.')
    os.close(fd)
    # if initial content is specified, then insert into the tmpfile
    if content is not None:
        with open(tmpfile, 'w') as f:
            f.write(content)
        initialcontent = content
    else:
        initialcontent = ""
    # execute the editor
    args = [editor, tmpfile]
    p = subprocess.Popen(args, shell=False)
    stdout,stderr = p.communicate()
    exitstatus = p.returncode
    # non-zero exit status is interpreted as failure
    if exitstatus != 0:
        raise EditorFailed(exitstatus, stdout, stderr)
    # read in the input and remove the tmpfile
    with open(tmpfile, 'r') as f:
        finalcontent = f.read()
    os.remove(tmpfile)
    # if content has not changed, return None, otherwise return the input
    if initialcontent == finalcontent:
        return None
    return finalcontent

def strip_comments(content):
    """
    Remove all lines in the content which start with '#'.
    """
    if content is None:
        return None
    lines = filter(lambda x: not x.strip().startswith('#'), content.split('\n'))
    return '\n'.join(lines).strip()
