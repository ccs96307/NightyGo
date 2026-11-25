"""Tests for navigation paths in the visual SGF tree."""

import unittest

from nightygo.sgf import SgfNode
from nightygo.ui.game_tree_view import _find_path


class GameTreePathTests(unittest.TestCase):
    def test_finds_only_the_selected_variation_path(self) -> None:
        root = SgfNode()
        main = SgfNode({"B": ["dd"]})
        main_reply = SgfNode({"W": ["qp"]})
        branch = SgfNode({"B": ["pd"]})
        root.children.extend((main, branch))
        main.children.append(main_reply)

        self.assertEqual(_find_path(root, main_reply), [root, main, main_reply])
        self.assertEqual(_find_path(root, branch), [root, branch])

    def test_returns_empty_path_for_detached_node(self) -> None:
        self.assertEqual(_find_path(SgfNode(), SgfNode()), [])


if __name__ == "__main__":
    unittest.main()
