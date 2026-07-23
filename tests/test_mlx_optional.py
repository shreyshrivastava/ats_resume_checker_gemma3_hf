import os

import pytest


@pytest.mark.mlx
@pytest.mark.skipif(
    os.getenv("RUN_MLX_TESTS") != "1",
    reason="Set RUN_MLX_TESTS=1 on Apple Silicon to run the local MLX smoke test.",
)
def test_optional_mlx_generation_smoke():
    from backend.processor import generate_with_mlx

    result = generate_with_mlx("Reply with exactly one short sentence.", max_tokens=12)

    assert result
    assert not result.startswith("Error:")
