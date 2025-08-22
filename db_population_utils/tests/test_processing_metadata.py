import json
from dataclasses import dataclass
from datetime import datetime
from db_population_utils.data_processor.processing_metadata import ProcessingMetadata

@dataclass
class DummyReport:
    file_path: str = "x.csv"
    file_size_mb: float = 1.23
    quality_score: int = 85
    warnings: list = None
    errors: list = None

def test_from_load_report_dict_and_dataclass(tmp_path):
    d = {"file_path":"a.csv","file_size_mb":2.5,"quality_score":90,"warnings":["w"],"errors":["e"]}
    m1 = ProcessingMetadata.from_load_report(d)
    assert m1.file_path == "a.csv" and m1.file_size_mb == 2.5 and m1.quality_score == 90

    m2 = ProcessingMetadata.from_load_report(DummyReport())
    assert m2.file_path == "x.csv" and m2.quality_score == 85

def test_steps_validation_and_score_clamp():
    m = ProcessingMetadata(file_path="y.csv", file_size_mb=0.1, )
    m.add_processing_step("standardize", {"cols":3})
    assert m.processing_steps and m.processing_steps[-1]["step_name"] == "standardize"

    m.quality_score = 95
    m.set_validation_results({"passed": False, "issues":[1,2,3]})
    assert 0 <= m.quality_score <= 100

def test_json_roundtrip(tmp_path):
    m = ProcessingMetadata(file_path="z.csv", file_size_mb=3.14)
    m.add_warning("w1"); m.add_error("e1")
    p = tmp_path / "meta.json"
    m.save_to_json(str(p))
    loaded = ProcessingMetadata.load_from_json(str(p))
    assert loaded.file_path == "z.csv"
    assert loaded.warnings == ["w1"] and loaded.errors == ["e1"]
