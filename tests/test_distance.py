from distance import haversine

def test_haversine_distance():
    # Chennai to nearby point
    dist = haversine(13.0827, 80.2707, 13.05, 80.25)

    assert dist > 0
    assert dist < 10  # should be small distance