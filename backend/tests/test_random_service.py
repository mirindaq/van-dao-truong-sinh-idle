from app.game.random_service import RandomService


def test_random_service_is_seedable() -> None:
    first = RandomService(seed=108)
    second = RandomService(seed=108)

    assert [first.randint(1, 100) for _ in range(5)] == [
        second.randint(1, 100) for _ in range(5)
    ]

