import os
from uuid import uuid4

import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
import webviz_core_components as wcc
from dash.dependencies import Input, Output
from webviz_config.webviz_store import webvizstore
from webviz_config.common_cache import CACHE
from webviz_config import WebvizContainerABC

import fmu.ensemble

class Completions(WebvizContainerABC):
    """### Completion viewer

This container will provide a viewer for the well completions as they
have been configured in an Eclipse deck.

This needs ensembles configured in container_settings
"""

    def __init__(self, app, container_settings):

        self.uid = f"{uuid4()}"
        self.chart_id = "chart-id-{}".format(uuid4())
        #self.plot_type_id = "plot-type-id-{}".format(uuid4())
        #self.disk_usage = get_disk_usage(self.scratch_dir)
        self.ensemble_paths = container_settings["scratch_ensembles"]
        self.dropdown_ens_id = f"dropdown-ens-{self.uid}"
        self.dropdown_real_id = f"dropdown-real-{self.uid}"
        self.set_callbacks(app)

    @property
    def layout(self):
        return html.Div(
            [
                html.P(f"Completion view on {self.ensemble_paths}"),
                wcc.Graph(id=self.chart_id),
            ]
        )

    def set_callbacks(self, app):
        #@app.callback(
        #    Output(self.chart_id, "figure"), [Input(self.plot_type_id, "value")]
        #)
        def _update_plot(plot_type):
            return
            if plot_type == "Pie chart":
                data = [
                    {
                        "values": self.usage,
                        "labels": self.users,
                        "text": (self.usage).map("{:.2f} GB".format),
                        "textinfo": "label",
                        "textposition": "inside",
                        "hoverinfo": "label+text",
                        "type": "pie",
                    }
                ]
                layout = {}

            layout["height"] = 800
            layout["width"] = 1000
            layout["font"] = {"family": "Equinor"}
            layout["hoverlabel"] = {"font": {"family": "Equinor"}}

            return {"data": data, "layout": layout}

    def add_webvizstore(self):
        return [(get_disk_usage, [{"scratch_dir": self.scratch_dir}])]

@CACHE.memoize(timeout=CACHE.TIMEOUT)
def scratch_ensemble(ensemble_name, ensemble_path):
    return fmu.ensemble.ScratchEnsemble(ensemble_name, ensemble_path)

@CACHE.memoize(timeout=CACHE.TIMEOUT)
@webvizstore
def get_realization_compdat(ensemble_paths, ensemble_name, realization) -> pd.DataFrame:

    try:
        ens = scratch_ensemble(ens_name, ens_path)
        df = pd.read_csv(os.path.join(scratch_dir, "disk_usage.csv"))
    except FileNotFoundError:
        raise FileNotFoundError(f"No disk usage file found at {scratch_dir}")

    last_date = sorted(list(df["date"].unique()))[-1]
    return df.loc[df["date"] == last_date]
