# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# pylint: disable=line-too-long,trailing-whitespace

import yaml
from .types import _sanitize_pip_show_output

PIP_SHOW_OUTPUT_DATA = [
    # pip show -f ipython
    """
Name: ipython
Version: 8.13.2
Summary: IPython: Productive Interactive Computing
Home-page: https://ipython.org
Author: The IPython Development Team
Author-email: ipython-dev@python.org
License: BSD-3-Clause
Location: /home/user/venv/lib/python3.10/site-packages
Requires: appnope, backcall, decorator, jedi, matplotlib-inline, pexpect, pickleshare, prompt-toolkit, pygments, stack-data, traitlets
Required-by: adcm-client
Files:
  ../../../bin/ipython
  ../../../bin/ipython3
  ../../../share/man/man1/ipython.1
  IPython/__init__.py
  IPython/__main__.py
  IPython/__pycache__/__init__.cpython-310.pyc
  IPython/__pycache__/__main__.cpython-310.pyc
  IPython/__pycache__/conftest.cpython-310.pyc
  IPython/__pycache__/consoleapp.cpython-310.pyc
  IPython/__pycache__/display.cpython-310.pyc
  IPython/__pycache__/paths.cpython-310.pyc
  IPython/conftest.py
  IPython/consoleapp.py
  IPython/core/__init__.py
  IPython/core/__pycache__/__init__.cpython-310.pyc
  IPython/core/__pycache__/alias.cpython-310.pyc
  IPython/core/__pycache__/application.cpython-310.pyc
  IPython/core/__pycache__/async_helpers.cpython-310.pyc
  IPython/core/__pycache__/autocall.cpython-310.pyc
  IPython/core/__pycache__/builtin_trap.cpython-310.pyc
  IPython/core/__pycache__/compilerop.cpython-310.pyc
  IPython/core/__pycache__/completer.cpython-310.pyc
  IPython/core/__pycache__/completerlib.cpython-310.pyc
  IPython/core/__pycache__/crashhandler.cpython-310.pyc
  IPython/core/__pycache__/debugger.cpython-310.pyc
  IPython/core/__pycache__/display.cpython-310.pyc
  IPython/core/__pycache__/display_functions.cpython-310.pyc
  IPython/core/__pycache__/display_trap.cpython-310.pyc
  IPython/core/__pycache__/displayhook.cpython-310.pyc
  IPython/core/__pycache__/displaypub.cpython-310.pyc
  IPython/core/__pycache__/error.cpython-310.pyc
  IPython/core/__pycache__/events.cpython-310.pyc
  IPython/core/__pycache__/excolors.cpython-310.pyc
  IPython/core/__pycache__/extensions.cpython-310.pyc
  IPython/core/__pycache__/formatters.cpython-310.pyc
  IPython/core/__pycache__/getipython.cpython-310.pyc
  IPython/core/__pycache__/guarded_eval.cpython-310.pyc
  IPython/core/__pycache__/history.cpython-310.pyc
  IPython/core/__pycache__/historyapp.cpython-310.pyc
  IPython/core/__pycache__/hooks.cpython-310.pyc
  IPython/core/__pycache__/inputsplitter.cpython-310.pyc
  IPython/core/__pycache__/inputtransformer.cpython-310.pyc
  IPython/core/__pycache__/inputtransformer2.cpython-310.pyc
  IPython/core/__pycache__/interactiveshell.cpython-310.pyc
  IPython/core/__pycache__/latex_symbols.cpython-310.pyc
  IPython/core/__pycache__/logger.cpython-310.pyc
  IPython/core/__pycache__/macro.cpython-310.pyc
  IPython/core/__pycache__/magic.cpython-310.pyc
  IPython/core/__pycache__/magic_arguments.cpython-310.pyc
  IPython/core/__pycache__/oinspect.cpython-310.pyc
  IPython/core/__pycache__/page.cpython-310.pyc
  IPython/core/__pycache__/payload.cpython-310.pyc
  IPython/core/__pycache__/payloadpage.cpython-310.pyc
  IPython/core/__pycache__/prefilter.cpython-310.pyc
  IPython/core/__pycache__/profileapp.cpython-310.pyc
  IPython/core/__pycache__/profiledir.cpython-310.pyc
  IPython/core/__pycache__/prompts.cpython-310.pyc
  IPython/core/__pycache__/pylabtools.cpython-310.pyc
  IPython/core/__pycache__/release.cpython-310.pyc
  IPython/core/__pycache__/shellapp.cpython-310.pyc
  IPython/core/__pycache__/splitinput.cpython-310.pyc
  IPython/core/__pycache__/ultratb.cpython-310.pyc
  IPython/core/__pycache__/usage.cpython-310.pyc
  IPython/core/alias.py
  IPython/core/application.py
  IPython/core/async_helpers.py
  IPython/core/autocall.py
  IPython/core/builtin_trap.py
  IPython/core/compilerop.py
  IPython/core/completer.py
  IPython/core/completerlib.py
  IPython/core/crashhandler.py
  IPython/core/debugger.py
  IPython/core/display.py
  IPython/core/display_functions.py
  IPython/core/display_trap.py
  IPython/core/displayhook.py
  IPython/core/displaypub.py
  IPython/core/error.py
  IPython/core/events.py
  IPython/core/excolors.py
  IPython/core/extensions.py
  IPython/core/formatters.py
  IPython/core/getipython.py
  IPython/core/guarded_eval.py
  IPython/core/history.py
  IPython/core/historyapp.py
  IPython/core/hooks.py
  IPython/core/inputsplitter.py
  IPython/core/inputtransformer.py
  IPython/core/inputtransformer2.py
  IPython/core/interactiveshell.py
  IPython/core/latex_symbols.py
  IPython/core/logger.py
  IPython/core/macro.py
  IPython/core/magic.py
  IPython/core/magic_arguments.py
  IPython/core/magics/__init__.py
  IPython/core/magics/__pycache__/__init__.cpython-310.pyc
  IPython/core/magics/__pycache__/auto.cpython-310.pyc
  IPython/core/magics/__pycache__/basic.cpython-310.pyc
  IPython/core/magics/__pycache__/code.cpython-310.pyc
  IPython/core/magics/__pycache__/config.cpython-310.pyc
  IPython/core/magics/__pycache__/display.cpython-310.pyc
  IPython/core/magics/__pycache__/execution.cpython-310.pyc
  IPython/core/magics/__pycache__/extension.cpython-310.pyc
  IPython/core/magics/__pycache__/history.cpython-310.pyc
  IPython/core/magics/__pycache__/logging.cpython-310.pyc
  IPython/core/magics/__pycache__/namespace.cpython-310.pyc
  IPython/core/magics/__pycache__/osm.cpython-310.pyc
  IPython/core/magics/__pycache__/packaging.cpython-310.pyc
  IPython/core/magics/__pycache__/pylab.cpython-310.pyc
  IPython/core/magics/__pycache__/script.cpython-310.pyc
  IPython/core/magics/auto.py
  IPython/core/magics/basic.py
  IPython/core/magics/code.py
  IPython/core/magics/config.py
  IPython/core/magics/display.py
  IPython/core/magics/execution.py
  IPython/core/magics/extension.py
  IPython/core/magics/history.py
  IPython/core/magics/logging.py
  IPython/core/magics/namespace.py
  IPython/core/magics/osm.py
  IPython/core/magics/packaging.py
  IPython/core/magics/pylab.py
  IPython/core/magics/script.py
  IPython/core/oinspect.py
  IPython/core/page.py
  IPython/core/payload.py
  IPython/core/payloadpage.py
  IPython/core/prefilter.py
  IPython/core/profile/README_STARTUP
  IPython/core/profileapp.py
  IPython/core/profiledir.py
  IPython/core/prompts.py
  IPython/core/pylabtools.py
  IPython/core/release.py
  IPython/core/shellapp.py
  IPython/core/splitinput.py
  IPython/core/tests/2x2.jpg
  IPython/core/tests/2x2.png
  IPython/core/tests/__init__.py
  IPython/core/tests/__pycache__/__init__.cpython-310.pyc
  IPython/core/tests/__pycache__/bad_all.cpython-310.pyc
  IPython/core/tests/__pycache__/nonascii.cpython-310.pyc
  IPython/core/tests/__pycache__/nonascii2.cpython-310.pyc
  IPython/core/tests/__pycache__/print_argv.cpython-310.pyc
  IPython/core/tests/__pycache__/refbug.cpython-310.pyc
  IPython/core/tests/__pycache__/simpleerr.cpython-310.pyc
  IPython/core/tests/__pycache__/tclass.cpython-310.pyc
  IPython/core/tests/__pycache__/test_alias.cpython-310.pyc
  IPython/core/tests/__pycache__/test_application.cpython-310.pyc
  IPython/core/tests/__pycache__/test_async_helpers.cpython-310.pyc
  IPython/core/tests/__pycache__/test_autocall.cpython-310.pyc
  IPython/core/tests/__pycache__/test_compilerop.cpython-310.pyc
  IPython/core/tests/__pycache__/test_completer.cpython-310.pyc
  IPython/core/tests/__pycache__/test_completerlib.cpython-310.pyc
  IPython/core/tests/__pycache__/test_debugger.cpython-310.pyc
  IPython/core/tests/__pycache__/test_display.cpython-310.pyc
  IPython/core/tests/__pycache__/test_displayhook.cpython-310.pyc
  IPython/core/tests/__pycache__/test_events.cpython-310.pyc
  IPython/core/tests/__pycache__/test_extension.cpython-310.pyc
  IPython/core/tests/__pycache__/test_formatters.cpython-310.pyc
  IPython/core/tests/__pycache__/test_guarded_eval.cpython-310.pyc
  IPython/core/tests/__pycache__/test_handlers.cpython-310.pyc
  IPython/core/tests/__pycache__/test_history.cpython-310.pyc
  IPython/core/tests/__pycache__/test_hooks.cpython-310.pyc
  IPython/core/tests/__pycache__/test_imports.cpython-310.pyc
  IPython/core/tests/__pycache__/test_inputsplitter.cpython-310.pyc
  IPython/core/tests/__pycache__/test_inputtransformer.cpython-310.pyc
  IPython/core/tests/__pycache__/test_inputtransformer2.cpython-310.pyc
  IPython/core/tests/__pycache__/test_inputtransformer2_line.cpython-310.pyc
  IPython/core/tests/__pycache__/test_interactiveshell.cpython-310.pyc
  IPython/core/tests/__pycache__/test_iplib.cpython-310.pyc
  IPython/core/tests/__pycache__/test_logger.cpython-310.pyc
  IPython/core/tests/__pycache__/test_magic.cpython-310.pyc
  IPython/core/tests/__pycache__/test_magic_arguments.cpython-310.pyc
  IPython/core/tests/__pycache__/test_magic_terminal.cpython-310.pyc
  IPython/core/tests/__pycache__/test_oinspect.cpython-310.pyc
  IPython/core/tests/__pycache__/test_page.cpython-310.pyc
  IPython/core/tests/__pycache__/test_paths.cpython-310.pyc
  IPython/core/tests/__pycache__/test_prefilter.cpython-310.pyc
  IPython/core/tests/__pycache__/test_profile.cpython-310.pyc
  IPython/core/tests/__pycache__/test_prompts.cpython-310.pyc
  IPython/core/tests/__pycache__/test_pylabtools.cpython-310.pyc
  IPython/core/tests/__pycache__/test_run.cpython-310.pyc
  IPython/core/tests/__pycache__/test_shellapp.cpython-310.pyc
  IPython/core/tests/__pycache__/test_splitinput.cpython-310.pyc
  IPython/core/tests/__pycache__/test_ultratb.cpython-310.pyc
  IPython/core/tests/bad_all.py
  IPython/core/tests/daft_extension/__pycache__/daft_extension.cpython-310.pyc
  IPython/core/tests/daft_extension/daft_extension.py
  IPython/core/tests/nonascii.py
  IPython/core/tests/nonascii2.py
  IPython/core/tests/print_argv.py
  IPython/core/tests/refbug.py
  IPython/core/tests/simpleerr.py
  IPython/core/tests/tclass.py
  IPython/core/tests/test_alias.py
  IPython/core/tests/test_application.py
  IPython/core/tests/test_async_helpers.py
  IPython/core/tests/test_autocall.py
  IPython/core/tests/test_compilerop.py
  IPython/core/tests/test_completer.py
  IPython/core/tests/test_completerlib.py
  IPython/core/tests/test_debugger.py
  IPython/core/tests/test_display.py
  IPython/core/tests/test_displayhook.py
  IPython/core/tests/test_events.py
  IPython/core/tests/test_extension.py
  IPython/core/tests/test_formatters.py
  IPython/core/tests/test_guarded_eval.py
  IPython/core/tests/test_handlers.py
  IPython/core/tests/test_history.py
  IPython/core/tests/test_hooks.py
  IPython/core/tests/test_imports.py
  IPython/core/tests/test_inputsplitter.py
  IPython/core/tests/test_inputtransformer.py
  IPython/core/tests/test_inputtransformer2.py
  IPython/core/tests/test_inputtransformer2_line.py
  IPython/core/tests/test_interactiveshell.py
  IPython/core/tests/test_iplib.py
  IPython/core/tests/test_logger.py
  IPython/core/tests/test_magic.py
  IPython/core/tests/test_magic_arguments.py
  IPython/core/tests/test_magic_terminal.py
  IPython/core/tests/test_oinspect.py
  IPython/core/tests/test_page.py
  IPython/core/tests/test_paths.py
  IPython/core/tests/test_prefilter.py
  IPython/core/tests/test_profile.py
  IPython/core/tests/test_prompts.py
  IPython/core/tests/test_pylabtools.py
  IPython/core/tests/test_run.py
  IPython/core/tests/test_shellapp.py
  IPython/core/tests/test_splitinput.py
  IPython/core/tests/test_ultratb.py
  IPython/core/ultratb.py
  IPython/core/usage.py
  IPython/display.py
  IPython/extensions/__init__.py
  IPython/extensions/__pycache__/__init__.cpython-310.pyc
  IPython/extensions/__pycache__/autoreload.cpython-310.pyc
  IPython/extensions/__pycache__/storemagic.cpython-310.pyc
  IPython/extensions/autoreload.py
  IPython/extensions/storemagic.py
  IPython/extensions/tests/__init__.py
  IPython/extensions/tests/__pycache__/__init__.cpython-310.pyc
  IPython/extensions/tests/__pycache__/test_autoreload.cpython-310.pyc
  IPython/extensions/tests/__pycache__/test_storemagic.cpython-310.pyc
  IPython/extensions/tests/test_autoreload.py
  IPython/extensions/tests/test_storemagic.py
  IPython/external/__init__.py
  IPython/external/__pycache__/__init__.cpython-310.pyc
  IPython/external/__pycache__/qt_for_kernel.cpython-310.pyc
  IPython/external/__pycache__/qt_loaders.cpython-310.pyc
  IPython/external/qt_for_kernel.py
  IPython/external/qt_loaders.py
  IPython/external/tests/__init__.py
  IPython/external/tests/__pycache__/__init__.cpython-310.pyc
  IPython/external/tests/__pycache__/test_qt_loaders.cpython-310.pyc
  IPython/external/tests/test_qt_loaders.py
  IPython/lib/__init__.py
  IPython/lib/__pycache__/__init__.cpython-310.pyc
  IPython/lib/__pycache__/backgroundjobs.cpython-310.pyc
  IPython/lib/__pycache__/clipboard.cpython-310.pyc
  IPython/lib/__pycache__/deepreload.cpython-310.pyc
  IPython/lib/__pycache__/demo.cpython-310.pyc
  IPython/lib/__pycache__/display.cpython-310.pyc
  IPython/lib/__pycache__/editorhooks.cpython-310.pyc
  IPython/lib/__pycache__/guisupport.cpython-310.pyc
  IPython/lib/__pycache__/latextools.cpython-310.pyc
  IPython/lib/__pycache__/lexers.cpython-310.pyc
  IPython/lib/__pycache__/pretty.cpython-310.pyc
  IPython/lib/backgroundjobs.py
  IPython/lib/clipboard.py
  IPython/lib/deepreload.py
  IPython/lib/demo.py
  IPython/lib/display.py
  IPython/lib/editorhooks.py
  IPython/lib/guisupport.py
  IPython/lib/latextools.py
  IPython/lib/lexers.py
  IPython/lib/pretty.py
  IPython/lib/tests/__init__.py
  IPython/lib/tests/__pycache__/__init__.cpython-310.pyc
  IPython/lib/tests/__pycache__/test_backgroundjobs.cpython-310.pyc
  IPython/lib/tests/__pycache__/test_clipboard.cpython-310.pyc
  IPython/lib/tests/__pycache__/test_deepreload.cpython-310.pyc
  IPython/lib/tests/__pycache__/test_display.cpython-310.pyc
  IPython/lib/tests/__pycache__/test_editorhooks.cpython-310.pyc
  IPython/lib/tests/__pycache__/test_imports.cpython-310.pyc
  IPython/lib/tests/__pycache__/test_latextools.cpython-310.pyc
  IPython/lib/tests/__pycache__/test_lexers.cpython-310.pyc
  IPython/lib/tests/__pycache__/test_pretty.cpython-310.pyc
  IPython/lib/tests/__pycache__/test_pygments.cpython-310.pyc
  IPython/lib/tests/test.wav
  IPython/lib/tests/test_backgroundjobs.py
  IPython/lib/tests/test_clipboard.py
  IPython/lib/tests/test_deepreload.py
  IPython/lib/tests/test_display.py
  IPython/lib/tests/test_editorhooks.py
  IPython/lib/tests/test_imports.py
  IPython/lib/tests/test_latextools.py
  IPython/lib/tests/test_lexers.py
  IPython/lib/tests/test_pretty.py
  IPython/lib/tests/test_pygments.py
  IPython/paths.py
  IPython/py.typed
  IPython/sphinxext/__init__.py
  IPython/sphinxext/__pycache__/__init__.cpython-310.pyc
  IPython/sphinxext/__pycache__/custom_doctests.cpython-310.pyc
  IPython/sphinxext/__pycache__/ipython_console_highlighting.cpython-310.pyc
  IPython/sphinxext/__pycache__/ipython_directive.cpython-310.pyc
  IPython/sphinxext/custom_doctests.py
  IPython/sphinxext/ipython_console_highlighting.py
  IPython/sphinxext/ipython_directive.py
  IPython/terminal/__init__.py
  IPython/terminal/__pycache__/__init__.cpython-310.pyc
  IPython/terminal/__pycache__/console.cpython-310.pyc
  IPython/terminal/__pycache__/debugger.cpython-310.pyc
  IPython/terminal/__pycache__/embed.cpython-310.pyc
  IPython/terminal/__pycache__/interactiveshell.cpython-310.pyc
  IPython/terminal/__pycache__/ipapp.cpython-310.pyc
  IPython/terminal/__pycache__/magics.cpython-310.pyc
  IPython/terminal/__pycache__/prompts.cpython-310.pyc
  IPython/terminal/__pycache__/ptutils.cpython-310.pyc
  IPython/terminal/console.py
  IPython/terminal/debugger.py
  IPython/terminal/embed.py
  IPython/terminal/interactiveshell.py
  IPython/terminal/ipapp.py
  IPython/terminal/magics.py
  IPython/terminal/prompts.py
  IPython/terminal/pt_inputhooks/__init__.py
  IPython/terminal/pt_inputhooks/__pycache__/__init__.cpython-310.pyc
  IPython/terminal/pt_inputhooks/__pycache__/asyncio.cpython-310.pyc
  IPython/terminal/pt_inputhooks/__pycache__/glut.cpython-310.pyc
  IPython/terminal/pt_inputhooks/__pycache__/gtk.cpython-310.pyc
  IPython/terminal/pt_inputhooks/__pycache__/gtk3.cpython-310.pyc
  IPython/terminal/pt_inputhooks/__pycache__/gtk4.cpython-310.pyc
  IPython/terminal/pt_inputhooks/__pycache__/osx.cpython-310.pyc
  IPython/terminal/pt_inputhooks/__pycache__/pyglet.cpython-310.pyc
  IPython/terminal/pt_inputhooks/__pycache__/qt.cpython-310.pyc
  IPython/terminal/pt_inputhooks/__pycache__/tk.cpython-310.pyc
  IPython/terminal/pt_inputhooks/__pycache__/wx.cpython-310.pyc
  IPython/terminal/pt_inputhooks/asyncio.py
  IPython/terminal/pt_inputhooks/glut.py
  IPython/terminal/pt_inputhooks/gtk.py
  IPython/terminal/pt_inputhooks/gtk3.py
  IPython/terminal/pt_inputhooks/gtk4.py
  IPython/terminal/pt_inputhooks/osx.py
  IPython/terminal/pt_inputhooks/pyglet.py
  IPython/terminal/pt_inputhooks/qt.py
  IPython/terminal/pt_inputhooks/tk.py
  IPython/terminal/pt_inputhooks/wx.py
  IPython/terminal/ptutils.py
  IPython/terminal/shortcuts/__init__.py
  IPython/terminal/shortcuts/__pycache__/__init__.cpython-310.pyc
  IPython/terminal/shortcuts/__pycache__/auto_match.cpython-310.pyc
  IPython/terminal/shortcuts/__pycache__/auto_suggest.cpython-310.pyc
  IPython/terminal/shortcuts/__pycache__/filters.cpython-310.pyc
  IPython/terminal/shortcuts/auto_match.py
  IPython/terminal/shortcuts/auto_suggest.py
  IPython/terminal/shortcuts/filters.py
  IPython/terminal/tests/__init__.py
  IPython/terminal/tests/__pycache__/__init__.cpython-310.pyc
  IPython/terminal/tests/__pycache__/test_debug_magic.cpython-310.pyc
  IPython/terminal/tests/__pycache__/test_embed.cpython-310.pyc
  IPython/terminal/tests/__pycache__/test_help.cpython-310.pyc
  IPython/terminal/tests/__pycache__/test_interactivshell.cpython-310.pyc
  IPython/terminal/tests/__pycache__/test_pt_inputhooks.cpython-310.pyc
  IPython/terminal/tests/__pycache__/test_shortcuts.cpython-310.pyc
  IPython/terminal/tests/test_debug_magic.py
  IPython/terminal/tests/test_embed.py
  IPython/terminal/tests/test_help.py
  IPython/terminal/tests/test_interactivshell.py
  IPython/terminal/tests/test_pt_inputhooks.py
  IPython/terminal/tests/test_shortcuts.py
  IPython/testing/__init__.py
  IPython/testing/__pycache__/__init__.cpython-310.pyc
  IPython/testing/__pycache__/decorators.cpython-310.pyc
  IPython/testing/__pycache__/globalipapp.cpython-310.pyc
  IPython/testing/__pycache__/ipunittest.cpython-310.pyc
  IPython/testing/__pycache__/skipdoctest.cpython-310.pyc
  IPython/testing/__pycache__/tools.cpython-310.pyc
  IPython/testing/decorators.py
  IPython/testing/globalipapp.py
  IPython/testing/ipunittest.py
  IPython/testing/plugin/README.txt
  IPython/testing/plugin/__init__.py
  IPython/testing/plugin/__pycache__/__init__.cpython-310.pyc
  IPython/testing/plugin/__pycache__/dtexample.cpython-310.pyc
  IPython/testing/plugin/__pycache__/ipdoctest.cpython-310.pyc
  IPython/testing/plugin/__pycache__/pytest_ipdoctest.cpython-310.pyc
  IPython/testing/plugin/__pycache__/setup.cpython-310.pyc
  IPython/testing/plugin/__pycache__/simple.cpython-310.pyc
  IPython/testing/plugin/__pycache__/simplevars.cpython-310.pyc
  IPython/testing/plugin/__pycache__/test_ipdoctest.cpython-310.pyc
  IPython/testing/plugin/__pycache__/test_refs.cpython-310.pyc
  IPython/testing/plugin/dtexample.py
  IPython/testing/plugin/ipdoctest.py
  IPython/testing/plugin/pytest_ipdoctest.py
  IPython/testing/plugin/setup.py
  IPython/testing/plugin/simple.py
  IPython/testing/plugin/simplevars.py
  IPython/testing/plugin/test_combo.txt
  IPython/testing/plugin/test_example.txt
  IPython/testing/plugin/test_exampleip.txt
  IPython/testing/plugin/test_ipdoctest.py
  IPython/testing/plugin/test_refs.py
  IPython/testing/skipdoctest.py
  IPython/testing/tests/__init__.py
  IPython/testing/tests/__pycache__/__init__.cpython-310.pyc
  IPython/testing/tests/__pycache__/test_decorators.cpython-310.pyc
  IPython/testing/tests/__pycache__/test_ipunittest.cpython-310.pyc
  IPython/testing/tests/__pycache__/test_tools.cpython-310.pyc
  IPython/testing/tests/test_decorators.py
  IPython/testing/tests/test_ipunittest.py
  IPython/testing/tests/test_tools.py
  IPython/testing/tools.py
  IPython/utils/PyColorize.py
  IPython/utils/__init__.py
  IPython/utils/__pycache__/PyColorize.cpython-310.pyc
  IPython/utils/__pycache__/__init__.cpython-310.pyc
  IPython/utils/__pycache__/_process_cli.cpython-310.pyc
  IPython/utils/__pycache__/_process_common.cpython-310.pyc
  IPython/utils/__pycache__/_process_posix.cpython-310.pyc
  IPython/utils/__pycache__/_process_win32.cpython-310.pyc
  IPython/utils/__pycache__/_process_win32_controller.cpython-310.pyc
  IPython/utils/__pycache__/_sysinfo.cpython-310.pyc
  IPython/utils/__pycache__/capture.cpython-310.pyc
  IPython/utils/__pycache__/colorable.cpython-310.pyc
  IPython/utils/__pycache__/coloransi.cpython-310.pyc
  IPython/utils/__pycache__/contexts.cpython-310.pyc
  IPython/utils/__pycache__/daemonize.cpython-310.pyc
  IPython/utils/__pycache__/data.cpython-310.pyc
  IPython/utils/__pycache__/decorators.cpython-310.pyc
  IPython/utils/__pycache__/dir2.cpython-310.pyc
  IPython/utils/__pycache__/docs.cpython-310.pyc
  IPython/utils/__pycache__/encoding.cpython-310.pyc
  IPython/utils/__pycache__/eventful.cpython-310.pyc
  IPython/utils/__pycache__/frame.cpython-310.pyc
  IPython/utils/__pycache__/generics.cpython-310.pyc
  IPython/utils/__pycache__/importstring.cpython-310.pyc
  IPython/utils/__pycache__/io.cpython-310.pyc
  IPython/utils/__pycache__/ipstruct.cpython-310.pyc
  IPython/utils/__pycache__/jsonutil.cpython-310.pyc
  IPython/utils/__pycache__/localinterfaces.cpython-310.pyc
  IPython/utils/__pycache__/log.cpython-310.pyc
  IPython/utils/__pycache__/module_paths.cpython-310.pyc
  IPython/utils/__pycache__/openpy.cpython-310.pyc
  IPython/utils/__pycache__/path.cpython-310.pyc
  IPython/utils/__pycache__/process.cpython-310.pyc
  IPython/utils/__pycache__/py3compat.cpython-310.pyc
  IPython/utils/__pycache__/sentinel.cpython-310.pyc
  IPython/utils/__pycache__/shimmodule.cpython-310.pyc
  IPython/utils/__pycache__/signatures.cpython-310.pyc
  IPython/utils/__pycache__/strdispatch.cpython-310.pyc
  IPython/utils/__pycache__/sysinfo.cpython-310.pyc
  IPython/utils/__pycache__/syspathcontext.cpython-310.pyc
  IPython/utils/__pycache__/tempdir.cpython-310.pyc
  IPython/utils/__pycache__/terminal.cpython-310.pyc
  IPython/utils/__pycache__/text.cpython-310.pyc
  IPython/utils/__pycache__/timing.cpython-310.pyc
  IPython/utils/__pycache__/tokenutil.cpython-310.pyc
  IPython/utils/__pycache__/traitlets.cpython-310.pyc
  IPython/utils/__pycache__/tz.cpython-310.pyc
  IPython/utils/__pycache__/ulinecache.cpython-310.pyc
  IPython/utils/__pycache__/version.cpython-310.pyc
  IPython/utils/__pycache__/wildcard.cpython-310.pyc
  IPython/utils/_process_cli.py
  IPython/utils/_process_common.py
  IPython/utils/_process_posix.py
  IPython/utils/_process_win32.py
  IPython/utils/_process_win32_controller.py
  IPython/utils/_sysinfo.py
  IPython/utils/capture.py
  IPython/utils/colorable.py
  IPython/utils/coloransi.py
  IPython/utils/contexts.py
  IPython/utils/daemonize.py
  IPython/utils/data.py
  IPython/utils/decorators.py
  IPython/utils/dir2.py
  IPython/utils/docs.py
  IPython/utils/encoding.py
  IPython/utils/eventful.py
  IPython/utils/frame.py
  IPython/utils/generics.py
  IPython/utils/importstring.py
  IPython/utils/io.py
  IPython/utils/ipstruct.py
  IPython/utils/jsonutil.py
  IPython/utils/localinterfaces.py
  IPython/utils/log.py
  IPython/utils/module_paths.py
  IPython/utils/openpy.py
  IPython/utils/path.py
  IPython/utils/process.py
  IPython/utils/py3compat.py
  IPython/utils/sentinel.py
  IPython/utils/shimmodule.py
  IPython/utils/signatures.py
  IPython/utils/strdispatch.py
  IPython/utils/sysinfo.py
  IPython/utils/syspathcontext.py
  IPython/utils/tempdir.py
  IPython/utils/terminal.py
  IPython/utils/tests/__init__.py
  IPython/utils/tests/__pycache__/__init__.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_capture.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_decorators.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_deprecated.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_dir2.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_imports.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_importstring.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_io.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_module_paths.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_openpy.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_path.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_process.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_pycolorize.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_shimmodule.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_sysinfo.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_tempdir.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_text.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_tokenutil.cpython-310.pyc
  IPython/utils/tests/__pycache__/test_wildcard.cpython-310.pyc
  IPython/utils/tests/test_capture.py
  IPython/utils/tests/test_decorators.py
  IPython/utils/tests/test_deprecated.py
  IPython/utils/tests/test_dir2.py
  IPython/utils/tests/test_imports.py
  IPython/utils/tests/test_importstring.py
  IPython/utils/tests/test_io.py
  IPython/utils/tests/test_module_paths.py
  IPython/utils/tests/test_openpy.py
  IPython/utils/tests/test_path.py
  IPython/utils/tests/test_process.py
  IPython/utils/tests/test_pycolorize.py
  IPython/utils/tests/test_shimmodule.py
  IPython/utils/tests/test_sysinfo.py
  IPython/utils/tests/test_tempdir.py
  IPython/utils/tests/test_text.py
  IPython/utils/tests/test_tokenutil.py
  IPython/utils/tests/test_wildcard.py
  IPython/utils/text.py
  IPython/utils/timing.py
  IPython/utils/tokenutil.py
  IPython/utils/traitlets.py
  IPython/utils/tz.py
  IPython/utils/ulinecache.py
  IPython/utils/version.py
  IPython/utils/wildcard.py
  ipython-8.13.2.dist-info/INSTALLER
  ipython-8.13.2.dist-info/LICENSE
  ipython-8.13.2.dist-info/METADATA
  ipython-8.13.2.dist-info/RECORD
  ipython-8.13.2.dist-info/WHEEL
  ipython-8.13.2.dist-info/entry_points.txt
  ipython-8.13.2.dist-info/top_level.txt
""",
    # pip show -f pydantic_core typing_extensions
    """
Name: pydantic_core
Version: 2.14.5
Summary: 
Home-page: https://github.com/pydantic/pydantic-core
Author: 
Author-email: Samuel Colvin <s@muelcolvin.com>
License: MIT
Location: /home/user/venv/lib/python3.10/site-packages
Requires: typing-extensions
Required-by: pydantic
Files:
  pydantic_core-2.14.5.dist-info/INSTALLER
  pydantic_core-2.14.5.dist-info/METADATA
  pydantic_core-2.14.5.dist-info/RECORD
  pydantic_core-2.14.5.dist-info/WHEEL
  pydantic_core-2.14.5.dist-info/license_files/LICENSE
  pydantic_core/__init__.py
  pydantic_core/__pycache__/__init__.cpython-310.pyc
  pydantic_core/__pycache__/core_schema.cpython-310.pyc
  pydantic_core/_pydantic_core.cpython-310-darwin.so
  pydantic_core/_pydantic_core.pyi
  pydantic_core/core_schema.py
  pydantic_core/py.typed
---
Name: typing_extensions
Version: 4.8.0
Summary: Backported and Experimental Type Hints for Python 3.8+
Home-page: 
Author: 
Author-email: "Guido van Rossum, Jukka Lehtosalo, Łukasz Langa, Michael Lee" <levkivskyi@gmail.com>
License: 
Location: /home/user/venv/lib/python3.10/site-packages
Requires: 
Required-by: astroid, black, pydantic, pydantic_core
Files:
  __pycache__/typing_extensions.cpython-310.pyc
  typing_extensions-4.8.0.dist-info/INSTALLER
  typing_extensions-4.8.0.dist-info/LICENSE
  typing_extensions-4.8.0.dist-info/METADATA
  typing_extensions-4.8.0.dist-info/RECORD
  typing_extensions-4.8.0.dist-info/WHEEL
  typing_extensions.py
""",
]


def test_sanitize_pip_show_output_valid():
    """
    Testing that _sanitize_pip_show_output produce valid yaml output
    with Location and Files keys for every module inside
    """
    for data in PIP_SHOW_OUTPUT_DATA:
        sanitized_pip_show_output = _sanitize_pip_show_output(data)
        modules_data = list(yaml.safe_load_all(sanitized_pip_show_output))
        assert modules_data, "no module parsed"
        for module in modules_data:
            assert "Location" in module, "No location found in module"
            assert module.get("Files", []), "No files found in module"
