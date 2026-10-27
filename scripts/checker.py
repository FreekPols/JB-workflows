import json
import ast
import pickle
import jupytext
from matplotlib.axes import Axes
import numpy as np
import matplotlib.pyplot as plt
from pyparsing import warnings


# CodeCell class (source + tags), could add other things later
class CodeCell:
    tags = []
    source = ""

    def __init__(self, source, tags):
        self.source = source
        self.tags = tags

class CodeChecker():
    namespace = {}

    # Load .ipynb
    def from_notebook(self, source_code):
        notebook = json.loads(source_code)
        plt.switch_backend("Agg")
        warnings.filterwarnings("ignore")
        cells = []

        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                cells.append(CodeCell("".join(cell["source"]), cell.get("metadata", {}).get("tags", [])))

        self.cells = cells
        self.namespace = {
            "np": np,
            "plt": plt,
        }

    # Load notebook from .md (jupytext)
    def __init__(self, jupytext_filename):
        """
        :param jupytext_filename: The path to a jupytext file containing the notebook code.

        :example:
        checker = CodeChecker("my_notebook.md")
        """

        # Load cells from jupytext
        jupytext_cells = jupytext.read(jupytext_filename).cells

        # Set matplotlib backend to Agg (non-interactive) and ignore warnings to avoid cluttering the output
        plt.switch_backend("Agg")
        warnings.filterwarnings("ignore")

        # Init namespace with imports
        self.namespace = {
            "np": np,
            "plt": plt,
        }

        # Load cells from jupytext
        self.cells = []
        for cell in jupytext_cells:
            if cell.cell_type == "code":
                self.cells.append(CodeCell(cell.source, cell.get("metadata", {}).get("tags", [])))

    # Get plots and namespace from a cell with a specific tag, optionally running all previous cells first
    def checkWithTag(self, tag, init_tags = [], run_previous_cells=False):
        """
        :param tag: The tag to search for in the notebook cells.
        :param run_previous_cells: If True, execute all cells before the tagged cell.
        :return: A tuple containing a list of matplotlib Axes objects and the namespace dictionary.
        """
        # get id of first cell with tag
        cell_id = None
        for index, cell in enumerate(self.cells):
            if tag in cell.tags:
                cell_id = index
                break

        if cell_id is None:
            return [], {}

        if run_previous_cells:
            for cell in self.cells[:cell_id]:
                self.executeSource(cell.source)

        if len(init_tags) > 0:
            for cell in self.cells[:cell_id]:
                if any(tag in cell.tags for tag in init_tags):
                    self.executeSource(cell.source)

        return self.executeSourceTraced(self.cells[cell_id].source)

    # Get plots of all cells, returning a dict of cell_id -> list of axes
    def checkAllCells(self):
        """
        :return: A dictionary mapping cell indices to lists of matplotlib Axes objects.
        """
        results = {}
        for index, cell in enumerate(self.cells):
            results[index], _ = self.executeSourceTraced(cell.source)

        return results


    # Prepare source code for execution, removing imports to avoid re-importing matplotlib and numpy and overwriting the tracing functions
    def prepareSource(self, source):
        tree = ast.parse(source, mode="exec")

        class ImportRemover(ast.NodeTransformer):

            def visit_Import(self, node):
                return None

            def visit_ImportFrom(self, node):
                if node.module in ("matplotlib", "numpy"):
                    return None
                return node

        tree = ImportRemover().visit(tree)
        ast.fix_missing_locations(tree)

        code = compile(tree, "<plot-source>", "exec")

        return code

    # execute cell normally, without tracing
    def executeSource(self, source):
        code = self.prepareSource(source)
        exec(code, self.namespace, self.namespace)
        plt.close("all")

    # execute cell with tracing, capturing all figures and returning their axes
    def executeSourceTraced(self, source):
        code = self.prepareSource(source)
        captured_figures = []
        original_show = plt.show
        original_axes_show = getattr(Axes, "show", None)

        # A somewhat convoluted way to snapshot a figure, but it works and ensures a deep copy of the matplotlib figure is made.
        def snapshot_figure(fig):
            return pickle.loads(
                pickle.dumps(
                    fig,
                    protocol=pickle.HIGHEST_PROTOCOL
                )
            )

        # plt.show() proxy that captures all figures and closes them (it does not show plots!)
        def traced_show(*args, **kwargs):

            figure_numbers = list(plt.get_fignums())

            current_figures = [
                plt.figure(num)
                for num in figure_numbers
            ]

            for fig in current_figures:

                snapshot = snapshot_figure(fig)

                captured_figures.append(snapshot)

            plt.close("all")

            return None

        # ax.show() proxy that captures the specific figure containing this Axes and closes it (it does not show plots!)
        def traced_axes_show(self, *args, **kwargs):

            # Snapshot the specific figure containing this Axes.
            snapshot = snapshot_figure(self.figure)

            captured_figures.append(snapshot)

            # Immediately remove all pyplot state.
            plt.close("all")

            return None

        # replace maplotlib functions with traced functions
        plt.show = traced_show
        Axes.show = traced_axes_show

        try:
            exec(
                code,
                self.namespace,
                self.namespace
            )

        finally:

            # Restore original matplotlib functions.
            plt.show = original_show

            if original_axes_show is None:
                try:
                    del Axes.show
                except AttributeError:
                    pass
            else:
                Axes.show = original_axes_show

            # Also clean matplotlib state
            plt.close("all")

        result = []

        for fig in captured_figures:
            result.extend(fig.axes)

        return result, self.namespace


        
