import sys
from pathlib import Path


sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "app")
)

from pipeline import TraceFlowPipeline


def test_transform():

    config = {
        "input_file": "data/input.csv",
        "output_file": "data/output.csv",
        "tax_rate": 0.10,
        "pipeline_name": "Test Pipeline"
    }

    pipeline = TraceFlowPipeline(config)

    data = [
        {
            "id": "1",
            "name": "Vivek",
            "city": "Pune",
            "product": "Laptop",
            "amount": "55000",
            "status": "Completed"
        }
    ]

    result = pipeline.transform(data)

    assert result[0]["final_amount"] == 60500