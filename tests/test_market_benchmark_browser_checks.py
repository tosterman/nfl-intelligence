"""Acceptance failure gates; browser observations are simulated, not live QA."""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


class BrowserAcceptanceChecks(unittest.TestCase):
    def setUp(self):
        # Run before CI installs browser binaries, without mocking other tests'
        # imports. The live two-browser checks remain separate release evidence.
        api = MagicMock()
        spec = importlib.util.spec_from_file_location(
            'benchmark_browser_under_test',
            Path(__file__).resolve().parents[1] / 'scripts/check_market_benchmark_ui.py')
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'playwright': MagicMock(), 'playwright.sync_api': api}):
            spec.loader.exec_module(self.module)
        self.browser = MagicMock()
        runtime = api.sync_playwright.return_value.__enter__.return_value
        runtime.chromium.launch.return_value = self.browser
        runtime.webkit.launch.return_value = self.browser
        self.page = self.browser.new_page.return_value
        self.page.goto.return_value.status = 200
        self.page.url = 'http://localhost:3000/performance'
        self.page.evaluate.side_effect = lambda expression: (
            {'violations': [], 'incomplete': []} if 'axe.run' in expression else False)
        self.expected = {'reportHash': 'a' * 64, 'checkedAt': '2026-09-11T12:00:00Z',
                         'coverageThrough': '2026-09-11T11:00:00Z',
                         'pairedGameCount': 0, 'books': [], 'excludedBookMarketCount': 0}

    def run_check(self):
        return self.module.check('http://localhost:3000', self.expected)

    def reject(self, message):
        with self.assertRaisesRegex(ValueError, message):
            self.run_check()
        self.browser.close.assert_called_once()

    def test_http_failure_rejects_and_closes_browser(self):
        self.page.goto.return_value.status = 503
        self.reject('HTTP 200')

    def test_redirect_rejects_and_closes_browser(self):
        self.page.url = 'https://unrelated.example/performance'
        self.reject('redirect')

    def test_page_error_cannot_produce_success(self):
        self.page.on.side_effect = lambda event, callback: callback(Exception('Injected error'))
        self.reject('Browser or accessibility')

    def test_overflow_cannot_produce_success(self):
        self.page.evaluate.side_effect = lambda expression: (
            {'violations': [], 'incomplete': []} if 'axe.run' in expression else True)
        self.reject('Browser or accessibility')

    def test_axe_violation_cannot_produce_success(self):
        self.page.evaluate.side_effect = lambda expression: (
            {'violations': [{'id': 'color-contrast'}], 'incomplete': []}
            if 'axe.run' in expression else False)
        self.reject('Browser or accessibility')

    def test_displayed_error_must_match_report(self):
        self.expected.update(pairedGameCount=1, books=[{
            'book': 'example', 'market': 'spread', 'pairedGames': 1,
            'excludedGames': 0, 'modelMae': 1.25, 'marketMae': 2.5}])
        cells = self.page.locator.return_value.locator.return_value.nth.return_value.locator.return_value
        cells.nth.return_value.inner_text.return_value = '100.00'
        self.reject('Displayed error differs')

    def test_healthy_empty_report_checks_both_browsers(self):
        report = self.run_check()
        self.assertEqual([row['engine'] for row in report['results']], ['chromium', 'webkit'])
        self.assertEqual(self.browser.close.call_count, 2)

    @unittest.skipIf(sys.flags.optimize, 'Already running optimized acceptance regression')
    def test_failure_gates_survive_optimized_python(self):
        result = subprocess.run([sys.executable, '-O', str(Path(__file__).resolve())],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
