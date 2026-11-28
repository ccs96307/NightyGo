"""Tests for GTP analysis line parsing."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication

from nightygo.engine import (
    EngineConfig,
    GtpEngine,
    parse_katago_info,
    parse_katago_info_lines,
    parse_katago_ownership,
    parse_katago_root_info,
)


class KataGoInfoTests(unittest.TestCase):
    def test_parses_candidate_metrics_and_principal_variation(self) -> None:
        result = parse_katago_info(
            "info move Q16 visits 1234 winrate 0.624 scoreLead 3.5 "
            "prior 0.2 order 1 pv Q16 D4 C3"
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.vertex, "Q16")
        self.assertEqual(result.visits, 1234)
        self.assertEqual(result.winrate, 0.624)
        self.assertEqual(result.score_lead, 3.5)
        self.assertEqual(result.principal_variation, ("Q16", "D4", "C3"))

    def test_parses_multiple_candidates_from_one_output_line(self) -> None:
        results = parse_katago_info_lines(
            "info move D4 visits 20 winrate 0.62 scoreLead 3 order 0 pv D4 C3 "
            "info move Q16 visits 10 winrate 0.55 scoreLead 1 order 1 pv Q16 D16"
        )

        self.assertEqual([item.vertex for item in results], ["D4", "Q16"])
        self.assertEqual(results[1].order, 1)

    def test_ignores_non_analysis_lines(self) -> None:
        self.assertIsNone(parse_katago_info("KataGo v1.15.0"))
        self.assertIsNone(parse_katago_info("info time 100"))

    def test_rejects_invalid_numeric_values(self) -> None:
        self.assertIsNone(parse_katago_info("info move D4 visits many winrate 0.5"))

    def test_reads_inline_root_info_from_native_katago_stream(self) -> None:
        line = (
            "info move K13 visits 8 order 0 pv K13 D4 "
            "rootInfo visits 89 utility 0.155677 winrate 0.578115 "
            "scoreMean 0.195523 scoreLead 0.195523 ownership 0.10269 -0.087118"
        )
        move = parse_katago_info(line)
        self.assertEqual(move.principal_variation, ("K13", "D4"))
        root = parse_katago_root_info(line)
        self.assertEqual(root.visits, 89)
        self.assertEqual(root.winrate, 0.578115)
        self.assertEqual(root.score_lead, 0.195523)
        self.assertEqual(parse_katago_ownership(line), (0.10269, -0.087118))

    def test_parses_root_metrics_and_ownership_map(self) -> None:
        line = (
            "info rootInfo visits 500 winrate 0.62 scoreLead 3.5 "
            "ownership 0.2 -0.4 0.8"
        )
        root = parse_katago_root_info(line)

        self.assertEqual(root.visits, 500)
        self.assertEqual(root.winrate, 0.62)
        self.assertEqual(root.score_lead, 3.5)
        self.assertEqual(parse_katago_ownership(line), (0.2, -0.4, 0.8))


class GtpProcessTests(unittest.TestCase):
    def test_replacing_engine_does_not_terminate_replacement(self) -> None:
        app = QApplication.instance() or QApplication([])
        # Answer the handshake and quit promptly like a real GTP process.
        script = (
            "import sys\n"
            "for line in sys.stdin:\n"
            "    if line.strip() == 'quit': break\n"
            "    command_id, command = line.split(maxsplit=1)\n"
            "    print(f'={command_id} ok\\n', flush=True)\n"
        )
        config = EngineConfig(sys.executable, ("-u", "-c", script))
        engine = GtpEngine()
        ready = []
        engine.ready.connect(lambda *_: ready.append(True))

        def wait_until(predicate) -> bool:
            deadline = QtCore.QDeadlineTimer(3000)
            while not predicate() and not deadline.hasExpired():
                app.processEvents(QtCore.QEventLoop.ProcessEventsFlag.AllEvents, 10)
                QtCore.QThread.msleep(5)
            return predicate()

        try:
            engine.start(config)
            self.assertTrue(wait_until(lambda: len(ready) == 1))
            engine.start(config)
            self.assertTrue(wait_until(lambda: len(ready) == 2))
            deadline = QtCore.QDeadlineTimer(1150)
            self.assertTrue(wait_until(deadline.hasExpired))
            self.assertTrue(engine.is_running)
            self.assertEqual(engine.status, engine.READY)
        finally:
            engine.stop()
            wait_until(lambda: not engine.is_running)

    def test_process_handshake_and_command_response_are_async(self) -> None:
        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "fake_gtp.py"
            script.write_text(
                "import sys\n"
                "for raw in sys.stdin:\n"
                "    line = raw.strip()\n"
                "    if not line: continue\n"
                "    command_id, command = line.split(' ', 1)\n"
                "    name = command.split()[0]\n"
                "    if name == 'kata-analyze':\n"
                "        print('info move D4 visits 20 winrate 0.62 scoreLead 3 order 0 pv D4 C3 info move Q16 visits 10 winrate 0.55 scoreLead 1 order 1 pv Q16 D16', flush=True)\n"
                "    values = {'protocol_version': '2', 'name': 'Fake GTP', "
                "'version': '1.0', 'genmove': 'D4'}\n"
                "    response = values[name] if name in values else ''\n"
                "    print(f'= {command_id} {response}\\n', flush=True)\n"
                "    if name == 'quit': break\n",
                encoding="utf-8",
            )
            engine = GtpEngine()
            ready_loop = QtCore.QEventLoop()
            engine.ready.connect(lambda *_: ready_loop.quit())
            engine.errorOccurred.connect(lambda *_: ready_loop.quit())
            QtCore.QTimer.singleShot(2500, ready_loop.quit)
            engine.start(EngineConfig(sys.executable, (str(script),)))
            ready_loop.exec()
            self.assertEqual(engine.status, GtpEngine.READY)

            responses: list[str] = []
            response_loop = QtCore.QEventLoop()

            def on_response(_command_id: int, command: str, response: str) -> None:
                if command == "genmove b":
                    responses.append(response)
                    response_loop.quit()

            engine.responseReceived.connect(on_response)
            engine.send_command("genmove b")
            QtCore.QTimer.singleShot(2500, response_loop.quit)
            response_loop.exec()
            self.assertEqual(responses, ["D4"])

            candidates = []
            analysis_loop = QtCore.QEventLoop()

            def on_analysis(candidate) -> None:
                candidates.append(candidate.vertex)
                if len(candidates) >= 2:
                    analysis_loop.quit()

            engine.analysisUpdated.connect(on_analysis)
            engine.start_analysis("B")
            QtCore.QTimer.singleShot(2500, analysis_loop.quit)
            analysis_loop.exec()
            self.assertEqual(candidates, ["D4", "Q16"])
            stop_loop = QtCore.QEventLoop()
            engine.statusChanged.connect(
                lambda status: stop_loop.quit() if status == GtpEngine.STOPPED else None
            )
            engine.stop()
            QtCore.QTimer.singleShot(1500, stop_loop.quit)
            stop_loop.exec()
            self.assertFalse(engine.is_running)
            app.processEvents()


if __name__ == "__main__":
    unittest.main()
