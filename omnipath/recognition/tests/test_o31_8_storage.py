from omnipath.recognition.recovery_vault import verify


def test_o31_8_storage_contract():
    report = verify()
    assert report["verdict"] == "PASS"
    assert report["original_path_present"] is False
    assert report["historical_git_required_for_reconstruction"] is False
