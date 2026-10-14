import os

import pandas as pd
import requests
import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="TraceFlow Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("TraceFlow")
st.caption("Predictive Data Pipeline Monitoring & Auto-Recovery Platform")


# --------------------------------------------------
# API CONFIGURATION
# --------------------------------------------------

DEFAULT_API_URL = "http://127.0.0.1:8000"

with st.sidebar:
    st.header("API Settings")

    api_url = st.text_input(
        "API Base URL",
        value=os.getenv("TRACEFLOW_API_URL", DEFAULT_API_URL),
    ).rstrip("/")

    access_token = st.text_input(
        "Access Token",
        type="password",
        help="Get your token from POST /login in Swagger.",
    )

    st.caption("API: " + api_url)


# --------------------------------------------------
# API HELPER FUNCTIONS
# --------------------------------------------------

def api_get(endpoint, params=None):
    """Send an authenticated GET request to the TraceFlow API."""

    if not access_token:
        return None, "Please enter your access token in the sidebar."

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    try:
        response = requests.get(
            f"{api_url}{endpoint}",
            headers=headers,
            params=params,
            timeout=30,
        )

        if response.status_code == 401:
            return None, "Authentication failed. Please log in again."

        if response.status_code == 403:
            return None, "You do not have permission to access this resource."

        response.raise_for_status()
        return response.json(), None

    except requests.exceptions.ConnectionError:
        return None, (
            "Cannot connect to the API. Start FastAPI in another terminal."
        )

    except requests.exceptions.Timeout:
        return None, "The API request timed out."

    except requests.exceptions.HTTPError as exc:
        details = exc.response.text if exc.response is not None else str(exc)
        return None, f"API error: {details}"

    except requests.exceptions.RequestException as exc:
        return None, f"Request failed: {exc}"

    except ValueError:
        return None, "The API returned an invalid JSON response."


def as_list(data):
    """Convert API list responses into a consistent Python list."""

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("items", "results", "data", "runs", "logs"):
            if isinstance(data.get(key), list):
                return data[key]

    return []


def show_api_error(error):
    if error:
        st.error(error)


def show_table(data, empty_message="No records available."):
    if not data:
        st.info(empty_message)
        return

    st.dataframe(
        pd.DataFrame(data),
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------
# LOGIN HELP
# --------------------------------------------------

with st.sidebar.expander("How to get an access token"):
    st.markdown(
        """
        1. Start the FastAPI server.
        2. Open [Swagger UI](http://127.0.0.1:8000/docs).
        3. Open `POST /login`.
        4. Enter your username and password.
        5. Copy `access_token` from the response.
        6. Paste it into the Access Token field above.
        """
    )


# --------------------------------------------------
# CHECK API CONNECTION
# --------------------------------------------------

if not access_token:
    st.info(
        "Enter your access token in the sidebar to load TraceFlow data."
    )
    st.stop()


# --------------------------------------------------
# LOAD CORE DATA
# --------------------------------------------------

runs_data, runs_error = api_get("/runs")
incidents_data, incidents_error = api_get("/incidents")
retry_data, retry_error = api_get("/retry-monitoring/analytics")

runs = as_list(runs_data) if not runs_error else []
incidents = as_list(incidents_data) if not incidents_error else []

if runs_error:
    show_api_error(runs_error)

if incidents_error:
    show_api_error(incidents_error)


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

st.header("Pipeline Overview")

total_runs = len(runs)

successful_runs = sum(
    1
    for run in runs
    if str(run.get("status", "")).upper()
    in {"SUCCESS", "SUCCEEDED"}
)

failed_runs = sum(
    1
    for run in runs
    if str(run.get("status", "")).upper()
    in {"FAILED", "ERROR"}
)

total_incidents = len(incidents)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Runs", total_runs)
col2.metric("Successful Runs", successful_runs)
col3.metric("Failed Runs", failed_runs)
col4.metric("Incidents", total_incidents)

if total_runs:
    overview_df = pd.DataFrame(runs)

    if "status" in overview_df.columns:
        st.subheader("Pipeline Run Status")

        status_counts = (
            overview_df["status"]
            .fillna("UNKNOWN")
            .astype(str)
            .value_counts()
        )

        st.bar_chart(status_counts)


# --------------------------------------------------
# PIPELINE RUN EXPLORER
# --------------------------------------------------

st.divider()
st.header("Pipeline Run Explorer")

if runs:
    run_df = pd.DataFrame(runs)

    if "status" in run_df.columns:
        statuses = sorted(
            run_df["status"].fillna("UNKNOWN").astype(str).unique()
        )

        selected_status = st.selectbox(
            "Filter by status",
            ["ALL"] + statuses,
        )

        filtered_runs = run_df.copy()

        if selected_status != "ALL":
            filtered_runs = filtered_runs[
                filtered_runs["status"].fillna("UNKNOWN").astype(str)
                == selected_status
            ]

        st.dataframe(
            filtered_runs,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.dataframe(run_df, use_container_width=True, hide_index=True)
else:
    st.info("No pipeline runs are available yet.")


# --------------------------------------------------
# RUN DETAILS
# --------------------------------------------------

st.divider()
st.header("Pipeline Run Details")

if runs:
    available_run_ids = [
        str(run["run_id"])
        for run in runs
        if run.get("run_id") is not None
    ]

    if available_run_ids:
        selected_run_id = st.selectbox(
            "Select a pipeline run",
            available_run_ids,
            key="details_run_id",
        )

        tab_logs, tab_metrics, tab_incidents, tab_retries = st.tabs(
            ["Logs", "Metrics", "Incidents", "Retries"]
        )

        with tab_logs:
            if st.button("Load Run Logs", key="load_run_logs"):
                logs_data, logs_error = api_get(
                    f"/logs/{selected_run_id}"
                )

                if logs_error:
                    show_api_error(logs_error)
                else:
                    show_table(
                        as_list(logs_data),
                        "No logs found for this run.",
                    )

        with tab_metrics:
            if st.button("Load Run Metrics", key="load_run_metrics"):
                metrics_data, metrics_error = api_get(
                    f"/metrics/{selected_run_id}"
                )

                if metrics_error:
                    show_api_error(metrics_error)
                else:
                    show_table(
                        as_list(metrics_data),
                        "No metrics found for this run.",
                    )

        with tab_incidents:
            if st.button(
                "Load Run Incident",
                key="load_run_incident",
            ):
                incident_data, incident_error = api_get(
                    f"/incidents/run/{selected_run_id}"
                )

                if incident_error:
                    show_api_error(incident_error)
                else:
                    show_table(
                        as_list(incident_data)
                        if isinstance(incident_data, list)
                        else [incident_data]
                        if isinstance(incident_data, dict)
                        else [],
                        "No incident found for this run.",
                    )

        with tab_retries:
            if st.button("Load Run Retries", key="load_run_retries"):
                retries_data, retries_error = api_get(
                    f"/retries/run/{selected_run_id}"
                )

                if retries_error:
                    show_api_error(retries_error)
                else:
                    show_table(
                        as_list(retries_data),
                        "No retry attempts found for this run.",
                    )
else:
    st.info("Create a pipeline run to explore its logs and metrics.")


# --------------------------------------------------
# ADVANCED LOG EXPLORER - DAY 28
# --------------------------------------------------

st.divider()
st.header("Advanced Log Explorer")

with st.form("advanced_log_search"):
    log_col1, log_col2 = st.columns(2)

    with log_col1:
        log_run_id = st.text_input(
            "Run ID (optional)",
            placeholder="Enter a run ID",
        )

        log_level = st.selectbox(
            "Log severity",
            ["ALL", "INFO", "WARNING", "ERROR", "DEBUG"],
        )

    with log_col2:
        log_keyword = st.text_input(
            "Search keyword",
            placeholder="For example: timeout or database",
        )

        log_limit = st.number_input(
            "Maximum results",
            min_value=1,
            max_value=500,
            value=100,
            step=10,
        )

    search_logs_clicked = st.form_submit_button(
        "Search Logs",
        use_container_width=True,
    )

if search_logs_clicked:
    log_params = {"limit": int(log_limit)}

    if log_run_id.strip():
        log_params["run_id"] = log_run_id.strip()

    if log_level != "ALL":
        log_params["level"] = log_level

    if log_keyword.strip():
        log_params["keyword"] = log_keyword.strip()

    search_data, search_error = api_get(
        "/logs/search",
        params=log_params,
    )

    if search_error:
        show_api_error(search_error)
    else:
        show_table(
            as_list(search_data),
            "No logs matched your search.",
        )


# --------------------------------------------------
# INCIDENT MONITORING
# --------------------------------------------------

st.divider()
st.header("Incident Monitoring")

if incidents:
    show_table(incidents)
else:
    st.info("No incidents available, or no incident data was returned.")


# --------------------------------------------------
# RETRY ANALYTICS
# --------------------------------------------------

st.divider()
st.header("Retry Analytics")

if retry_error:
    show_api_error(retry_error)
elif isinstance(retry_data, dict):
    retry_col1, retry_col2, retry_col3, retry_col4 = st.columns(4)

    retry_col1.metric(
        "Total Retries",
        retry_data.get("total_retries", 0),
    )

    retry_col2.metric(
        "Successful Retries",
        retry_data.get("successful_retries", 0),
    )

    retry_col3.metric(
        "Failed Retries",
        retry_data.get("failed_retries", 0),
    )

    retry_col4.metric(
        "Pending Retries",
        retry_data.get("pending_retries", 0),
    )

    st.json(retry_data)
else:
    st.info("Retry analytics are not available.")


# --------------------------------------------------
# DAY 29: PIPELINE PERFORMANCE ANALYTICS
# --------------------------------------------------

st.divider()
st.header("Pipeline Performance Analytics")

st.write(
    "Analyze execution times, success rates, failure rates, "
    "and slow pipeline runs."
)

with st.form("performance_analysis_form"):
    slow_threshold = st.number_input(
        "Slow pipeline threshold (seconds)",
        min_value=0.1,
        max_value=3600.0,
        value=5.0,
        step=1.0,
        help="Runs taking longer than this threshold are classified as slow.",
    )

    analyze_performance = st.form_submit_button(
        "Analyze Performance",
        use_container_width=True,
    )

if analyze_performance:
    performance_data, performance_error = api_get(
        "/performance/analytics",
        params={"slow_threshold": slow_threshold},
    )

    if performance_error:
        show_api_error(performance_error)

    elif isinstance(performance_data, dict):
        st.subheader("Performance Summary")

        completed_runs = performance_data.get("completed_runs", 0)
        success_rate = performance_data.get("success_rate_percent", 0)
        failure_rate = performance_data.get("failure_rate_percent", 0)
        average_time = performance_data.get(
            "average_execution_time_seconds", 0
        )
        slow_count = performance_data.get("slow_runs_count", 0)

        metric_col1, metric_col2, metric_col3 = st.columns(3)

        metric_col1.metric(
            "Completed Runs",
            completed_runs,
        )

        metric_col2.metric(
            "Success Rate",
            f"{success_rate:.2f}%",
        )

        metric_col3.metric(
            "Failure Rate",
            f"{failure_rate:.2f}%",
        )

        metric_col4, metric_col5, metric_col6 = st.columns(3)

        metric_col4.metric(
            "Average Execution Time",
            f"{average_time:.3f} sec",
        )

        metric_col5.metric(
            "Slow Runs",
            slow_count,
        )

        metric_col6.metric(
            "Configured Threshold",
            f"{performance_data.get('slow_threshold_seconds', slow_threshold)} sec",
        )

        st.subheader("Execution Time Details")

        time_col1, time_col2 = st.columns(2)

        time_col1.metric(
            "Fastest Execution",
            f"{performance_data.get('fastest_execution_time_seconds', 0):.3f} sec",
        )

        time_col2.metric(
            "Slowest Execution",
            f"{performance_data.get('slowest_execution_time_seconds', 0):.3f} sec",
        )

        # Execution history chart
        execution_history = performance_data.get(
            "execution_history", []
        )

        if execution_history:
            history_df = pd.DataFrame(execution_history)

            required_columns = {
                "run_id",
                "execution_time_seconds",
            }

            if required_columns.issubset(history_df.columns):
                history_df["run_id"] = (
                    history_df["run_id"].astype(str)
                )