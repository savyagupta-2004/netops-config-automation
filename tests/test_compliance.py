from netauto.compliance import compare_configs

GOLDEN = """frr version 8.4
hostname r1
!
interface eth1
 ip address 10.12.0.1/30
!
router ospf
 ospf router-id 10.0.0.1
 network 10.12.0.0/30 area 0.0.0.0
!
"""


def test_identical_config_is_compliant():
    report = compare_configs("r1", GOLDEN, GOLDEN)
    assert report.compliant is True
    assert report.diff == []


def test_drifted_config_is_flagged_with_diff():
    drifted = GOLDEN.replace("10.12.0.1/30", "10.12.0.99/30")
    report = compare_configs("r1", GOLDEN, drifted)
    assert report.compliant is False
    assert any("10.12.0.1/30" in line for line in report.diff)
    assert any("10.12.0.99/30" in line for line in report.diff)


def test_cosmetic_differences_are_ignored():
    # Live devices prepend banner/comment lines that shouldn't count as drift.
    live = "Building configuration...\n!\n" + GOLDEN + "\n\n"
    report = compare_configs("r1", GOLDEN, live)
    assert report.compliant is True
