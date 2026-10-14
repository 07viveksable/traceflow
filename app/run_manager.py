from datetime import datetime


pipeline_runs = []


def create_run(run_id, pipeline_name):
    run = {
        "run_id": run_id,
        "pipeline_name": pipeline_name,
        "status": "RUNNING",
        "records_processed": 0,
        "start_time": datetime.now().isoformat(),
        "end_time": None
    }

    pipeline_runs.append(run)

    return run


def complete_run(run_id, records_processed):
    for run in pipeline_runs:
        if run["run_id"] == run_id:
            run["status"] = "SUCCESS"
            run["records_processed"] = records_processed
            run["end_time"] = datetime.now().isoformat()

            return run

    return None


def fail_run(run_id):
    for run in pipeline_runs:
        if run["run_id"] == run_id:
            run["status"] = "FAILED"
            run["end_time"] = datetime.now().isoformat()

            return run

    return None


def get_all_runs():
    return pipeline_runs


def get_run(run_id):
    for run in pipeline_runs:
        if run["run_id"] == run_id:
            return run

    return None