#!/usr/bin/env python3
"""
Start mlx_lm.server, run test_finetuned_ontoclean.py, then shut down the server.

This wrapper bypasses the Ollama/GGUF pipeline entirely, serving the fused
HuggingFace safetensors model directly via mlx_lm's OpenAI-compatible server.
This avoids the 'model runner has unexpectedly stopped' Ollama crash caused by
mlx_lm exporting GGUF files with incorrect architecture metadata.

Usage:
    python scripts/test_with_mlx_server.py --model-path output/fine-tunning/models/mistral7b-ontoclean-fused
    python scripts/test_with_mlx_server.py --model-path output/fine-tunning/models/gemma9b-ontoclean-fused --port 8081
    python scripts/test_with_mlx_server.py \\
        --model-path output/fine-tunning/models/qwen7b-ontoclean-fused \\
        --output output/finetuned_tests/qwen7b_results.tsv \\
        --limit 5
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

import requests


def wait_for_server(endpoint: str, proc: subprocess.Popen, timeout: int = 300) -> bool:
    """Poll the server health endpoint until it responds, times out, or process dies."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        # Check if server process exited early
        if proc.poll() is not None:
            print(f"\nServer process exited with code {proc.returncode}")
            return False
        try:
            # Health endpoint is at /health, not under /v1/
            base = endpoint.rstrip("/").rsplit("/v1", 1)[0]
            resp = requests.get(f"{base}/health", timeout=3)
            if resp.status_code == 200:
                print()
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(3)
        print(".", end="", flush=True)
    print(f"\nServer did not respond within {timeout}s")
    return False


def main() -> None:
    project_root = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(
        description="Serve a fused MLX model and run test_finetuned_ontoclean.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test_with_mlx_server.py \\
      --model-path output/fine-tunning/models/mistral7b-ontoclean-fused

  python scripts/test_with_mlx_server.py \\
      --model-path output/fine-tunning/models/gemma9b-ontoclean-fused \\
      --output output/finetuned_tests/gemma9b_results.tsv
        """,
    )
    parser.add_argument("--model-path", required=True,
                        help="Path to the fused HuggingFace model directory")
    parser.add_argument("--port", type=int, default=8080,
                        help="Port for mlx_lm.server (default: 8080)")
    parser.add_argument("--model-name", default=None,
                        help="Display name passed to test script (default: basename of model-path)")
    parser.add_argument("--output", default=None,
                        help="TSV output path passed to test script")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of entities (passed to test script)")
    parser.add_argument("--no-compare", action="store_true",
                        help="Skip ground truth comparison (passed to test script)")
    parser.add_argument("--no-system-role", action="store_true",
                        help="Merge system prompt into first user message "
                             "(required for Gemma 2; passed to test script)")
    args = parser.parse_args()

    model_path = Path(args.model_path)
    if not model_path.exists():
        print(f"Error: model path not found: {model_path}", file=sys.stderr)
        sys.exit(1)

    model_name  = args.model_name or model_path.name
    endpoint    = f"http://localhost:{args.port}/v1"
    server_proc = None

    try:
        # ---------------------------------------------------------------
        # Start mlx_lm.server
        # ---------------------------------------------------------------
        print(f"Starting mlx_lm.server for {model_path.name} on port {args.port}...")
        server_proc = subprocess.Popen(
            ["uv", "run", "mlx_lm.server",
             "--model", str(model_path),
             "--port", str(args.port)],
            stdout=subprocess.DEVNULL,
            stderr=None,   # inherit stderr so model load errors are visible
            cwd=str(project_root),
        )

        print(f"Waiting for server to be ready at {endpoint} (up to 300s for large models)...")
        if not wait_for_server(endpoint, server_proc, timeout=300):
            print("Error: server failed to start.", file=sys.stderr)
            sys.exit(1)
        print(f"Server ready.\n")

        # ---------------------------------------------------------------
        # Run test script
        # ---------------------------------------------------------------
        # mlx_lm.server registers the model by its absolute path, not a
        # short name. Use the resolved path as the model ID in requests.
        mlx_model_id = str(model_path.resolve())
        test_cmd = [
            "uv", "run", "python",
            "scripts/test_finetuned_ontoclean.py",
            "--model", mlx_model_id,
            "--endpoint", endpoint,
        ]
        if args.output:
            test_cmd += ["--output", args.output]
        if args.limit:
            test_cmd += ["--limit", str(args.limit)]
        if args.no_compare:
            test_cmd.append("--no-compare")
        if args.no_system_role:
            test_cmd.append("--no-system-role")

        result = subprocess.run(test_cmd, cwd=str(project_root))
        sys.exit(result.returncode)

    finally:
        if server_proc and server_proc.poll() is None:
            print("\nShutting down mlx_lm.server...")
            server_proc.terminate()
            try:
                server_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server_proc.kill()


if __name__ == "__main__":
    main()
