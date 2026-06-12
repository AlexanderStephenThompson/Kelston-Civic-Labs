from kelston.ksl.types import check_scalar


def test_scalars_accept_good_values():
    assert check_scalar("id", "PLOT-000482") is None
    assert check_scalar("text", "hello") is None
    assert check_scalar("integer", 3) is None
    assert check_scalar("decimal", 3.5) is None
    assert check_scalar("boolean", True) is None
    assert check_scalar("date", "2026-06-12") is None
    assert check_scalar("time_of_day", "23:59") is None
    assert check_scalar("datetime", "2026-06-12T08:30:00") is None
    assert check_scalar("duration", "P3D") is None
    assert check_scalar("duration", "PT2H") is None
    assert check_scalar("duration", "P1DT4H30M") is None
    assert check_scalar("quantity", 12.25) is None


def test_scalars_reject_bad_values():
    assert check_scalar("id", "plot-1") is not None
    assert check_scalar("integer", True) is not None
    assert check_scalar("integer", 3.5) is not None
    assert check_scalar("boolean", 1) is not None
    assert check_scalar("date", "12/06/2026") is not None
    assert check_scalar("time_of_day", "24:00") is not None
    assert check_scalar("duration", "3 days") is not None
    assert check_scalar("quantity", "5 kg") is not None
