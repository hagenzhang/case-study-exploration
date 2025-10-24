
## Weather MCP Server

This project provides an MCP (Model Context Protocol) server for fetching weather data and alerts from the US National Weather Service (NWS) API. It exposes tools for retrieving weather alerts by US state and weather forecasts by latitude/longitude.

### Features
- Fetches active weather alerts for any US state.
- Retrieves weather forecasts for any location in the US using latitude and longitude.
- Runs as an MCP server using HTTP transport.
- Easily configurable port (edit the `PORT` variable in `weather.py`).

### Requirements
- Python 3.13 or newer
- [httpx](https://www.python-httpx.org/)
- [mcp](https://github.com/microsoft/model-context-protocol)

All dependencies are listed in `pyproject.toml` and can be installed with your preferred Python package manager (e.g., `uv`, `pip`).

### Setup
1. Install dependencies:
	 - Using [uv](https://github.com/astral-sh/uv) (recommended):
		 ```sh
		 uv pip install -r pyproject.toml
		 ```
	 - Or using pip:
		 ```sh
		 pip install -r pyproject.toml
		 ```

2. (Optional) Edit the `PORT` variable at the top of `weather.py` to change the server port (default is 8000):
	 ```python
	 PORT = 8000
	 ```

### Running the Server
Run the following command in the `weather` directory:

```sh
python weather.py
```

The server will start and listen on the port specified by the `PORT` variable (default: 8000).

### What the Project Does
- **Weather Alerts**: Provides a tool to fetch active weather alerts for a given US state (by two-letter code, e.g., `CA`, `NY`).
- **Weather Forecast**: Provides a tool to fetch the weather forecast for a given latitude and longitude.

These tools are exposed via the MCP protocol and can be integrated with MCP-compatible clients or agents.

### File Overview
- `weather.py`: Main server code, defines the MCP tools and runs the server.
- `pyproject.toml`: Project metadata and dependencies.
- `uv.lock`: Lock file for reproducible installs (if using `uv`).
- `README.md`: This file.

### Example Usage
**Get Alerts:**
```
get_alerts(state="CA")
```

**Get Forecast:**
```
get_forecast(latitude=34.05, longitude=-118.25)
```

### License
MIT License (add details as appropriate)

