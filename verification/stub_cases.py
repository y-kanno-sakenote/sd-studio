#!/usr/bin/env python3
"""担当: 検証係 — gen.py の失敗経路をスタブComfyUIで実測する。

本番コード（gen.py）はそのまま import し、SERVER だけ差し替えて main() を実走させる。
各ケースで exit code / stdout / stderr / 保存枚数 を記録する。
"""
import json, os, pathlib, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = pathlib.Path(__file__).resolve().parent
PNG = (b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)  # 中身はダミー（保存経路の確認のみ）

PID = "stub-pid-1"


def hist(status_str, images, completed=True, messages=None, outputs_key=True):
    e = {"status": {"status_str": status_str, "completed": completed,
                    "messages": messages or []}}
    if outputs_key:
        e["outputs"] = {"8": {"images": [
            {"filename": f"stub_{i}.png", "subfolder": "", "type": "output"}
            for i in range(images)]}}
    return {PID: e}


CASES = {
    # name: (prompt_response, history_sequence(list of dicts, last repeats), view_status)
    "1_partial":       (None, [hist("success", 2)], 200),
    "2_error_status":  (None, [hist("error", 0, completed=False,
                                    messages=[["execution_error", {"node_type": "KSampler",
                                               "exception_message": "stub: boom"}]])], 200),
    "3_zero_success":  (None, [hist("success", 0)], 200),
    "4_never_appears": (None, [{}], 200),
    "5_prompt_400":    ("400", [hist("success", 1)], 200),
    "6_view_404":      (None, [hist("success", 1)], 404),
    "7_no_outputs_key":(None, [hist("success", 0, outputs_key=False)], 200),
    "8_extra_images":  (None, [hist("success", 2)], 200),   # -n 1 要求に2枚返る
    "9_queue_wait":    (None, [{}, {}, {}, hist("success", 1)], 200),
}

ARGS = {
    "1_partial":       ["p", "-n", "4", "--timeout", "10"],
    "2_error_status":  ["p", "-n", "1", "--timeout", "10"],
    "3_zero_success":  ["p", "-n", "1", "--timeout", "10"],
    "4_never_appears": ["p", "-n", "1", "--timeout", "3"],
    "5_prompt_400":    ["p", "-n", "1", "--timeout", "10"],
    "6_view_404":      ["p", "-n", "1", "--timeout", "10"],
    "7_no_outputs_key":["p", "-n", "1", "--timeout", "10"],
    "8_extra_images":  ["p", "-n", "1", "--timeout", "10"],
    "9_queue_wait":    ["p", "-n", "1", "--timeout", "30"],
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        case = self.server.case
        if self.path.startswith("/system_stats"):
            return self._send(200, b'{"system":{"os":"stub"}}')
        if self.path.startswith("/history/"):
            seq = CASES[case][1]
            i = min(self.server.poll, len(seq) - 1)
            self.server.poll += 1
            return self._send(200, json.dumps(seq[i]).encode())
        if self.path.startswith("/view"):
            st = CASES[case][2]
            if st != 200:
                return self._send(st, b"not found", "text/plain")
            return self._send(200, PNG, "image/png")
        self._send(404, b"{}")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        self.rfile.read(n)
        if CASES[self.server.case][0] == "400":
            return self._send(400, json.dumps(
                {"error": {"type": "prompt_outputs_failed_validation",
                           "message": "stub: ckpt not found"}}).encode())
        self._send(200, json.dumps({"prompt_id": PID}).encode())


def run_case(name):
    srv = HTTPServer(("127.0.0.1", 0), Handler)
    srv.case, srv.poll = name, 0
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    outdir = ROOT / "stub_out" / name
    subprocess.run(["rm", "-rf", str(outdir)])
    code = (f"import sys; sys.path.insert(0,{str(ROOT.parent)!r});"
            f"import gen; gen.SERVER='http://127.0.0.1:{port}';"
            f"sys.argv=['gen.py']+{ARGS[name] + ['-o', str(outdir)]!r}; gen.main()")
    t0 = time.time()
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    el = time.time() - t0
    srv.shutdown()
    files = sorted(p.name for p in outdir.glob("*")) if outdir.exists() else []
    print(f"### {name}  exit={r.returncode}  {el:.1f}s  saved={files}")
    for line in (r.stdout or "").splitlines():
        print("  out| " + line)
    for line in (r.stderr or "").splitlines()[-6:]:
        print("  err| " + line)
    print()


if __name__ == "__main__":
    for n in (sys.argv[1:] or CASES):
        run_case(n)
